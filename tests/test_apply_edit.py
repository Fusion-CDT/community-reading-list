import shutil
from pathlib import Path

import pytest

from apply_edit import apply_edit, main, page_path

REPO = Path(__file__).resolve().parents[1]

# A page in the standard layout
PAGE = """---
title: "Machine learning"
isbn: "0070428077"
tags:
  - "Machine learning"
contributors:
  - {"name": "Joe", "github": "joe"}
comments: true
---

Old text.
"""


def test_keeps_frontmatter_exactly_if_already_credited():
    """An edit by someone already credited only changes the content.

    Their existing credit is kept as it is, even if they give a different
    name this time, and stray blank lines around the content are removed.
    """
    new = apply_edit(PAGE, "New text.\n\n", "Joe Bloggs", "joe")
    assert new == PAGE.replace("Old text.", "New text.")


def test_adds_contributor_keeping_key_order():
    """A new editor is credited after the existing contributors."""
    new = apply_edit(PAGE, "New text.", "Ada Lovelace", "ada")
    assert new == (
        "---\n"
        'title: "Machine learning"\n'
        'isbn: "0070428077"\n'
        "tags:\n"
        '  - "Machine learning"\n'
        "contributors:\n"
        '  - {"name": "Joe", "github": "joe"}\n'
        '  - {"name": "Ada Lovelace", "github": "ada"}\n'
        "comments: true\n"
        "---\n"
        "\n"
        "New text.\n"
    )


def test_credits_username_without_a_name():
    """An editor who gives no name is credited by their GitHub username."""
    new = apply_edit(PAGE, "New text.", "", "ada")
    assert '  - {"name": "ada", "github": "ada"}\n' in new


def test_tidies_other_layouts():
    """A page in another layout is rewritten in the standard layout.

    e.g. a page written by hand, or before the standard layout existed.
    """
    page = (
        "---\n"
        "comments: true\n"
        "tags:\n"
        "- Machine learning\n"
        "contributors:\n"
        "  - name: Joe\n"
        "    github: joe\n"
        "isbn: '0070428077'\n"
        "---\n\nOld text.\n"
    )
    assert apply_edit(page, "New text.", "", "joe") == (
        "---\n"
        'isbn: "0070428077"\n'
        "tags:\n"
        '  - "Machine learning"\n'
        "contributors:\n"
        '  - {"name": "Joe", "github": "joe"}\n'
        "comments: true\n"
        "---\n\nNew text.\n"
    )


def test_credits_first_contributor():
    """A page with no `contributors` key gets one, in the right place."""
    page = '---\ntitle: "Small ELMs"\ncomments: true\n---\n\nOld text.\n'
    new = apply_edit(page, "New text.", "", "ada")
    assert new == (
        "---\n"
        'title: "Small ELMs"\n'
        "contributors:\n"
        '  - {"name": "ada", "github": "ada"}\n'
        "comments: true\n"
        "---\n"
        "\n"
        "New text.\n"
    )


def test_page_path(tmp_path, monkeypatch):
    """The page's path is read from the title the ✏️ button gives the issue."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "page.md").write_text(PAGE)
    assert page_path("Edit: docs/page.md") == "docs/page.md"


@pytest.mark.parametrize(
    "title",
    [
        "Edit literature",  # no "Edit: " prefix
        "Edit: docs/missing.md",  # no such page
        "Edit: docs/../README.md",  # climbs out of docs/
        "Edit: .github/workflows/build.yml",  # outside docs/
    ],
)
def test_rejects_bad_titles(title, tmp_path, monkeypatch):
    """A title that doesn't name an existing page under docs/ fails.

    Anyone can edit an issue's title, so this stops an edit issue from
    changing any other file in the repository.
    """
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        page_path(title)


def test_main_applies_edit(tmp_path, monkeypatch):
    """The whole script, run as the workflow runs it, edits the page.

    It reads the real issue forms, so this also checks that the script and
    the forms agree (e.g. on the field labels and ids).
    """
    forms = Path(".github", "ISSUE_TEMPLATE")
    shutil.copytree(REPO / forms, tmp_path / forms)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "page.md").write_text(PAGE)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ISSUE_TITLE", "Edit: docs/page.md")
    monkeypatch.setenv("ISSUE_LABELS", '["edit-literature"]')
    monkeypatch.setenv("ISSUE_AUTHOR", "ada")
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output"))
    monkeypatch.setenv(
        "ISSUE_BODY",
        "### What needs changing?\n\nTypo\n\n"
        "### Proposed content\n\nNew text.\n\n"
        "### Images (optional)\n\n_No response_\n\n"
        "### Your name (optional)\n\n_No response_\n",
    )

    main()

    page = (tmp_path / "docs" / "page.md").read_text()
    assert page.endswith(
        '  - {"name": "ada", "github": "ada"}\n'
        "comments: true\n"
        "---\n\n"
        "New text.\n"
    )
    assert "docs/page.md" in (tmp_path / "output").read_text()
