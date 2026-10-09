"""
Turn a suggestion issue into a new note, ready for a pull request.

The issue's label tells us what kind of suggestion it is (see `TEMPLATES` below).
This script parses the issue with that label's form, writes the note's Markdown file,
then writes the following to `$GITHUB_OUTPUT` for the rest of the workflow:

- `filepath`: the note it wrote
- `branch`: the branch to open the pull request from
- `kind`: e.g. "paper" or "textbook", for the pull request's description
- `user_images`: the images uploaded with the issue, for `localise_images.py`

Usage (in a workflow step, with the issue in environment variables):

    ISSUE_BODY=... ISSUE_NUMBER=... ISSUE_AUTHOR=... ISSUE_LABELS='["paper-suggestion"]' \\
        uv run --locked --only-group scripts scripts/issue_to_note.py
"""

import json
import os
import sys
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn

from parse_issue import TEMPLATE_DIR, load_fields, parse_body, set_outputs

# Each suggestion label, and the issue form that applies it
TEMPLATES = {
    "paper-suggestion": "suggest-literature-paper.yml",
    "textbook-suggestion": "suggest-literature-textbook.yml",
    "lecture-notes-suggestion": "suggest-literature-lecture-notes.yml",
    "tutorial-suggestion": "suggest-tutorial.yml",
}

# Frontmatter keys
LIST_KEYS = ["tags", "url", "url_name"]  # may be comma-separated lists
TEXT_KEYS = ["doi", "title", "authors", "isbn", "availability"] # values taken as-is
# The order keys are written in. Any other keys (e.g. `icon`) go after these.
KEY_ORDER = TEXT_KEYS + LIST_KEYS + ["contributors", "comments"]


def suggestion_label(labels: list[str]) -> str:
    """Return the issue's suggestion label, e.g. "paper-suggestion"."""
    for label in labels:
        if label in TEMPLATES:
            return label
    raise ValueError(f"No suggestion label in {labels}")


def split_commas(stream: str) -> list[str]:
    """Split comma-separated string into a list,
    e.g. "MCF, ELMs, " -> ["MCF", "ELMs"]."""
    return [item.strip() for item in stream.split(",") if item.strip()]


def note_path(filepath: str, kind: str) -> str:
    """Return the note's path, e.g. "docs/literature/plasma/abel2013.md"."""
    folder = "tutorials" if kind == "tutorial" else "literature"
    # Forgive a path that includes a leading/trailing `/`, `docs/`, or `.md` extension
    path = filepath.strip().lstrip("/").removeprefix("docs/").removeprefix(f"{folder}/")
    path = path.strip("/").removesuffix(".md")
    if not path or ".." in PurePosixPath(path).parts:
        sys.exit(f"::error::'{filepath}' must be a path inside docs/{folder}/.")
    return f"docs/{folder}/{path}.md"


def build_frontmatter(answers: dict[str, Any], contributor: str) -> dict[str, Any]:
    """Return the note's frontmatter as a dictionary from the form's answers."""
    meta = {}
    for key in TEXT_KEYS:
        if answers.get(key):
            meta[key] = answers[key]
    for key in LIST_KEYS:
        if answers.get(key):
            meta[key] = split_commas(answers[key])
    # Credit the contributor by name if they gave one, otherwise by GitHub username
    name = answers.get("contributor_name") or contributor
    meta["contributors"] = [{"name": name, "github": contributor}]
    meta["comments"] = True
    return meta


def format_frontmatter(meta: dict[str, Any]) -> str:
    """Return `meta` as a frontmatter block. For example,

        {
            "doi": "10.1063/1.2178779",
            "tags": ["MCF", "Gyrokinetics"],
            "contributors": [{"name": "Ada Lovelace", "github": "ada"}],
            "comments": True,
        }

    becomes

        ---
        doi: "10.1063/1.2178779"
        tags:
          - "MCF"
          - "Gyrokinetics"
        contributors:
          - {"name": "Ada Lovelace", "github": "ada"}
        comments: true
        ---
    """
    keys = [key for key in KEY_ORDER if key in meta]
    keys += [key for key in meta if key not in KEY_ORDER]

    lines = ["---"]
    for key in keys:
        value = meta[key]
        # Lists (e.g. tags, url): one item per line, under the key
        if isinstance(value, list) and value:
            lines.append(f"{key}:")
            lines += [f"  - {json.dumps(item, ensure_ascii=False)}" for item in value]
            
        # Everything else on one line (e.g. `doi: "10.1063/1.2178779"`).
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def main() -> None:
    # Determine what kind of suggestion this issue is (paper, textbook, etc.)
    labels = json.loads(os.environ["ISSUE_LABELS"]) # get _all_ issue labels
    label = suggestion_label(labels) # extract _relevant_ label, e.g. "paper-suggestion"
    kind = label.removesuffix("-suggestion")  # e.g. "paper"

    # Parse issue body using the relevant template
    fields = load_fields(TEMPLATE_DIR / TEMPLATES[label])
    answers = parse_body(os.environ["ISSUE_BODY"], fields)

    # Work out where the note goes, and don't overwrite an existing note
    path = Path(note_path(answers["filepath"], kind))
    if path.exists():
        sys.exit(f"::error::{path} already exists. Choose a different location or filename.")

    # Build and format frontmatter and content
    frontmatter = format_frontmatter(build_frontmatter(answers, os.environ["ISSUE_AUTHOR"]))
    content = answers["content"].strip()

    # Write note, creating its folder if it's new
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{frontmatter}\n{content}\n")
    print(f"Wrote {path}")
    
    # Pass outputs to GitHub Actions output file
    outputs = {
        "filepath": str(path),
        "branch": f"add-suggested-{kind}-{os.environ['ISSUE_NUMBER']}",
        "kind": kind.replace("-", " "),
        "user_images": answers["user_images"],
    }
    set_outputs(outputs, os.environ["GITHUB_OUTPUT"])


if __name__ == "__main__":
    main()
