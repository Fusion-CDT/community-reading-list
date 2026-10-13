"""
Write every page's frontmatter in the standard layout.

The standard layout is the one the issue workflows write (see
`format_frontmatter` in issue_to_note.py): keys in a fixed order, every value
in double quotes, and one contributor per line. For example:

    ---
    doi: "10.1063/1.2178779"
    tags:
      - "MCF"
      - "Gyrokinetics"
    contributors:
      - {"name": "Ada Lovelace", "github": "ada"}
    comments: true
    ---

Only the frontmatter changes: the rest of each page is left exactly as it is.
Pages without frontmatter are skipped.

Usage:

    uv run scripts/format_notes.py          # rewrite pages not in the layout
    uv run scripts/format_notes.py --check  # list them, and fail if any

The build check runs it with `--check`, so a pull request with frontmatter in
another layout (e.g. a note written by hand) fails until it's formatted.
"""

import argparse
import sys
from pathlib import Path

import yaml

from issue_to_note import format_frontmatter

DOCS = Path("docs")


def split_page(text: str) -> tuple[str, str] | None:
    r"""Split a page into its frontmatter and the rest, or None if it has none.

    For example, "---\ntags: [MCF]\n---\n\nText\n" splits into
    "tags: [MCF]\n" and "\nText\n".
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)  # the closing `---`
    if end == -1:
        return None
    return text[4 : end + 1], text[end + 5 :]


def format_page(text: str) -> str:
    """Return the page's text with its frontmatter in the standard layout."""
    parts = split_page(text)
    if parts is None:
        return text
    frontmatter, rest = parts
    meta = yaml.safe_load(frontmatter) or {}
    return format_frontmatter(meta) + rest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write every page's frontmatter in the standard layout."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="don't change anything; list pages not in the layout, and fail "
        "if there are any",
    )
    args = parser.parse_args()

    unformatted = []
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            formatted = format_page(text)
        except yaml.YAMLError as error:
            sys.exit(f"{path}: the frontmatter isn't valid YAML.\n{error}")
        if formatted == text:
            continue
        unformatted.append(path)
        if not args.check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(formatted)

    if args.check:
        for path in unformatted:
            print(f"{path}: frontmatter isn't in the standard layout")
        if unformatted:
            sys.exit("Run `uv run scripts/format_notes.py` to format them.")
        print("All frontmatter is in the standard layout.")
    else:
        print(f"Formatted {len(unformatted)} page(s).")


if __name__ == "__main__":
    main()
