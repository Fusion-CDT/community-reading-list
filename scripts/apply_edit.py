"""
Apply an edit suggestion to an existing page, ready for a pull request.

Edit issues come from the ✏️ button on each page, which opens an edit form
with the page's path in the title (`Edit: docs/...md`) and its current text
in the form. This script replaces the page's content with the proposed
content, and writes the frontmatter in the standard layout (see
`format_frontmatter` in issue_to_note.py), adding the contributor to
`contributors` if they aren't credited yet.

It writes these to `$GITHUB_OUTPUT` for the rest of the workflow:

- `filepath`: the page it edited
- `user_images`: the images uploaded with the issue, for localise_images.py

Usage (in a workflow step, with the issue in environment variables):

    ISSUE_TITLE=... ISSUE_BODY=... ISSUE_AUTHOR=... ISSUE_LABELS='["edit-literature"]' \\
        uv run --locked --only-group scripts scripts/apply_edit.py
"""

import json
import os
import sys
from pathlib import Path, PurePosixPath

import yaml

from issue_to_note import format_frontmatter
from parse_issue import TEMPLATE_DIR, load_fields, parse_body, set_outputs

# Each edit label, and the issue form that applies it
TEMPLATES = {
    "edit-literature": "edit-literature.yml",
    "edit-tutorial": "edit-tutorial.yml",
}

def edit_label(labels: list[str]) -> str:
    """Return the issue's edit label, e.g. "edit-literature"."""
    for label in labels:
        if label in TEMPLATES:
            return label
    raise ValueError(f"No edit label in {labels}")


def page_path(title: str) -> str:
    """Return the page's path from the issue title, checking it's a page under docs/.

    Anyone can change an issue's title, so only accept existing Markdown files
    under docs/.
    """
    # An example issue title created with the ✏️ button is
    # "Edit: docs/literature/Machine Learning/mitchell1997machine-learning.md"
    if not title.startswith("Edit: "):
        sys.exit(
            "::error::The issue title should start with 'Edit: docs/'. "
            "Use the ✏️ button on the page you want to change."
        )
    path = title.removeprefix("Edit: ").strip()
    parts = PurePosixPath(path).parts
    if not path.endswith(".md") or not parts or parts[0] != "docs" or ".." in parts:
        sys.exit(f"::error::'{path}' is not a Markdown page under docs/.")
    if not Path(path).is_file():
        sys.exit(f"::error::{path} doesn't exist.")
    return path


def apply_edit(existing: str, proposed_content: str, contributor_name: str, author: str) -> str:
    """Return the page's new text: its frontmatter, then the proposed content."""
    _, frontmatter_text, _ = existing.split("---", 2)
    meta = yaml.safe_load(frontmatter_text)

    # Credit the contributor, by name if they gave one, unless they're already credited
    contributors = meta.setdefault("contributors", [])  # some pages have none yet
    credited = {c["github"] for c in contributors}
    if author not in credited:
        # If name given, credit as e.g. [Ada Lovelace](https://github.com/ada)
        # else credit as e.g. [ada](https://github.com/ada)
        contributors.append({"name": contributor_name or author, "github": author})

    # Write the frontmatter in the standard layout. A page already in it comes
    # out unchanged, apart from any new contributor.
    return f"{format_frontmatter(meta)}\n{proposed_content.strip()}\n"


def main() -> None:
    label = edit_label(json.loads(os.environ["ISSUE_LABELS"]))

    fields = load_fields(TEMPLATE_DIR / TEMPLATES[label])
    answers = parse_body(os.environ["ISSUE_BODY"], fields)

    path = Path(page_path(os.environ["ISSUE_TITLE"]))
    existing = path.read_text(encoding="utf-8")
    contributor_name = answers["contributor_name"].strip()
    updated = apply_edit(existing, answers["proposed_content"], contributor_name, os.environ["ISSUE_AUTHOR"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Updated {path}")

    set_outputs(
        {"filepath": str(path), "user_images": answers["user_images"]},
        os.environ["GITHUB_OUTPUT"],
    )


if __name__ == "__main__":
    main()
