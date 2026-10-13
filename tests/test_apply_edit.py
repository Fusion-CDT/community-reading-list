import shutil
from pathlib import Path

import pytest

from apply_edit import TEMPLATES, apply_edit, main, page_path
from parse_issue import load_fields

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


def answers(**fields):
    """Return an edit form's answers: no name, new content, and `fields`.

    `fields` are the form's frontmatter fields, e.g. tags="MCF, ELMs". Keys
    without a field in the form (here, any not given) are left alone.
    """
    return {"contributor_name": "", "proposed_content": "New text.", **fields}


def test_keeps_frontmatter_exactly_if_already_credited():
    """An edit by someone already credited only changes the content.

    Their existing credit is kept as it is, even if they give a different
    name this time, and stray blank lines around the content are removed.
    """
    edit = answers(
        contributor_name="Joe Bloggs", proposed_content="New text.\n\n"
    )
    new = apply_edit(PAGE, edit, "joe")
    assert new == PAGE.replace("Old text.", "New text.")


def test_adds_contributor_keeping_key_order():
    """A new editor is credited after the existing contributors."""
    new = apply_edit(PAGE, answers(contributor_name="Ada Lovelace"), "ada")
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
    new = apply_edit(PAGE, answers(), "ada")
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
    assert apply_edit(page, answers(), "joe") == (
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
    new = apply_edit(page, answers(), "ada")
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


def test_applies_changes_to_frontmatter():
    """The form's frontmatter fields replace the page's values.

    The edit form is filled in with the page's values, so a field left empty
    removes its key (here, the ISBN), and an unchanged field changes nothing.
    """
    edit = answers(
        resource_title="Machine learning",
        isbn="",
        tags="Machine learning, Neural networks",
        url="https://example.com/book",
    )
    assert apply_edit(PAGE, edit, "joe") == (
        "---\n"
        'title: "Machine learning"\n'
        "tags:\n"
        '  - "Machine learning"\n'
        '  - "Neural networks"\n'
        "url:\n"
        '  - "https://example.com/book"\n'
        "contributors:\n"
        '  - {"name": "Joe", "github": "joe"}\n'
        "comments: true\n"
        "---\n"
        "\n"
        "New text.\n"
    )


def test_keeps_keys_the_form_does_not_ask_about():
    """Keys without a field in the form, e.g. `isbn` in the tutorial form,
    are kept as they are."""
    new = apply_edit(PAGE, answers(tags="Machine learning"), "joe")
    assert 'isbn: "0070428077"' in new
    assert 'title: "Machine learning"' in new


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
    monkeypatch.setenv("ISSUE_LABELS", '["edit-textbook"]')
    monkeypatch.setenv("ISSUE_AUTHOR", "ada")
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output"))
    monkeypatch.setenv(
        "ISSUE_BODY",
        "### What needs changing?\n\nAdd a tag\n\n"
        "### Title\n\nMachine learning\n\n"
        "### Authors\n\nTom Mitchell\n\n"
        "### ISBN\n\n0070428077\n\n"
        "### Availability (optional)\n\n_No response_\n\n"
        "### URL(s)\n\n_No response_\n\n"
        "### URL name(s)\n\n_No response_\n\n"
        "### Tags\n\nMachine learning, Neural networks\n\n"
        "### Proposed content\n\nNew text.\n\n"
        "### Images (optional)\n\n_No response_\n\n"
        "### Your name (optional)\n\n_No response_\n",
    )

    main()

    page = (tmp_path / "docs" / "page.md").read_text()
    assert page == (
        "---\n"
        'title: "Machine learning"\n'
        'authors: "Tom Mitchell"\n'
        'isbn: "0070428077"\n'
        "tags:\n"
        '  - "Machine learning"\n'
        '  - "Neural networks"\n'
        "contributors:\n"
        '  - {"name": "Joe", "github": "joe"}\n'
        '  - {"name": "ada", "github": "ada"}\n'
        "comments: true\n"
        "---\n"
        "\n"
        "New text.\n"
    )
    assert "docs/page.md" in (tmp_path / "output").read_text()


@pytest.mark.parametrize(
    "label",
    ["edit-paper", "edit-textbook", "edit-lecture-notes", "edit-tutorial"],
)
def test_every_edit_form_asks_for_tags_and_content(label):
    """Each edit label has a form, with the fields every edit needs."""
    fields = load_fields(REPO / ".github" / "ISSUE_TEMPLATE" / TEMPLATES[label])
    ids = {field_id for field_id, _ in fields.values()}
    assert {"tags", "proposed_content", "contributor_name"} <= ids
