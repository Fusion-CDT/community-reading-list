import shutil
from pathlib import Path

import pytest
import yaml

from issue_to_note import build_frontmatter, format_frontmatter, main, note_path

REPO = Path(__file__).resolve().parents[1]


def frontmatter_for(answers):
    """Return the frontmatter for a suggestion from GitHub user "ada"."""
    return format_frontmatter(build_frontmatter(answers, contributor="ada"))


def test_textbook_frontmatter():
    """A textbook's answers become frontmatter in the standard layout.

    Every value is in double quotes (so the ISBN keeps its leading zero),
    comma-separated answers become lists with blanks removed, and the keys
    come in KEY_ORDER.
    """
    frontmatter = frontmatter_for({
        "resource_title": 'Tokamaks: "the" book',
        "authors": "John Wesson",
        "isbn": "0070428077",
        "availability": "Library: 2 copies",
        "url": "https://a.example, https://b.example",
        "url_name": "Book",
        "tags": "MCF, Tokamaks , ",
        "contributor_name": "Ada Lovelace",
    })
    assert frontmatter == (
        "---\n"
        'title: "Tokamaks: \\"the\\" book"\n'
        'authors: "John Wesson"\n'
        'isbn: "0070428077"\n'
        'availability: "Library: 2 copies"\n'
        "tags:\n"
        '  - "MCF"\n'
        '  - "Tokamaks"\n'
        "url:\n"
        '  - "https://a.example"\n'
        '  - "https://b.example"\n'
        "url_name:\n"
        '  - "Book"\n'
        "contributors:\n"
        '  - {"name": "Ada Lovelace", "github": "ada"}\n'
        "comments: true\n"
        "---\n"
    )


def test_frontmatter_reads_back_as_written():
    """Awkward values read back unchanged, and empty answers are left out.

    The old bash workflow wrote titles containing quotes or colons as
    invalid YAML. Without a name, the contributor is credited by username.
    """
    answers = {
        "resource_title": 'Turbulence: a "review" \\ ✓',
        "isbn": "0070428077",
        "doi": "",
        "tags": "MCF",
    }
    meta = yaml.safe_load(frontmatter_for(answers).strip("-\n"))
    assert meta == {
        "tags": ["MCF"],
        "title": 'Turbulence: a "review" \\ ✓',
        "isbn": "0070428077",
        "contributors": [{"name": "ada", "github": "ada"}],
        "comments": True,
    }


def test_keys_in_standard_order():
    """Keys are written in KEY_ORDER, then any others (e.g. `icon`)."""
    meta = {
        "icon": "home",
        "comments": True,
        "tags": ["MCF"],
        "doi": "10.1063/1.2178779",
    }
    assert format_frontmatter(meta) == (
        "---\n"
        'doi: "10.1063/1.2178779"\n'
        "tags:\n"
        '  - "MCF"\n'
        "comments: true\n"
        'icon: "home"\n'
        "---\n"
    )


def test_empty_list_written_inline():
    """An empty list is written as `tags: []`, not a bare `tags:`.

    A bare `tags:` would be read as null, which fails the site build.
    """
    assert format_frontmatter({"tags": []}) == "---\ntags: []\n---\n"


def test_single_link_written_as_list():
    """A single link written by hand, without a list, becomes a list."""
    meta = {"url": "https://a.example", "url_name": "Notes"}
    assert format_frontmatter(meta) == (
        "---\n"
        "url:\n"
        '  - "https://a.example"\n'
        "url_name:\n"
        '  - "Notes"\n'
        "---\n"
    )


@pytest.mark.parametrize(
    "given, expected",
    [
        ("plasma/MCF/abel2013", "docs/literature/plasma/MCF/abel2013.md"),
        ("plasma/abel2013.md", "docs/literature/plasma/abel2013.md"),
        ("literature/plasma/abel2013", "docs/literature/plasma/abel2013.md"),
        ("/docs/literature/abel2013 ", "docs/literature/abel2013.md"),
    ],
)
def test_literature_paths(given, expected):
    """Literature goes under docs/literature/, however the path is written.

    With or without a leading `/`, `docs/`, `literature/` or `.md`, and
    with stray spaces, the path ends up the same.
    """
    assert note_path(given, "paper") == expected


@pytest.mark.parametrize(
    "given, expected",
    [
        ("docs/tutorials/heat.md", "docs/tutorials/heat.md"),
        ("tutorials/exhaust/heat", "docs/tutorials/exhaust/heat.md"),
        ("heat", "docs/tutorials/heat.md"),
    ],
)
def test_tutorial_paths(given, expected):
    """Tutorials go under docs/tutorials/, however the path is written."""
    assert note_path(given, "tutorial") == expected


@pytest.mark.parametrize(
    "given",
    [
        "../../.github/workflows/build",
        "plasma/../../../README.md",
        "docs/literature/",
        "",
    ],
)
def test_rejects_paths_outside_folder(given):
    """A path that climbs out of the folder, or names no file, fails."""
    with pytest.raises(SystemExit):
        note_path(given, "paper")


def test_main_writes_note(tmp_path, monkeypatch):
    """The whole script, run as the workflow runs it, writes the note.

    It reads the real issue forms, so this also checks that the script and
    the forms agree (e.g. on the field labels and ids).
    """
    forms = Path(".github", "ISSUE_TEMPLATE")
    shutil.copytree(REPO / forms, tmp_path / forms)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ISSUE_LABELS", '["lecture-notes-suggestion"]')
    monkeypatch.setenv("ISSUE_NUMBER", "7")
    monkeypatch.setenv("ISSUE_AUTHOR", "ada")
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output"))
    monkeypatch.setenv(
        "ISSUE_BODY",
        "### Title\n\nKinetic theory\n\n"
        "### Location and filename\n\nplasma/schekochihin2026kinetic\n\n"
        "### Tags\n\nMCF\n\n"
        "### Content\n\nGood notes.\n",
    )

    main()

    note = tmp_path / "docs/literature/plasma/schekochihin2026kinetic.md"
    assert note.read_text().endswith(
        'title: "Kinetic theory"\n'
        "tags:\n"
        '  - "MCF"\n'
        "contributors:\n"
        '  - {"name": "ada", "github": "ada"}\n'
        "comments: true\n"
        "---\n\n"
        "Good notes.\n"
    )
    output = (tmp_path / "output").read_text()
    assert "add-suggested-lecture-notes-7" in output
    assert "lecture notes" in output
