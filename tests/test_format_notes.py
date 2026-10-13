import pytest

from format_notes import format_page, main, split_page

# A page written by hand: keys in another order, values unquoted, a single
# link without a list, and a horizontal rule (`---`) in the content
HAND_WRITTEN = """---
comments: true
contributors:
  - name: Ada Lovelace
    github: ada
url: https://a.example
tags:
- MCF
title: Kinetic theory
---

Some text.

---

More text.
"""

FORMATTED = """---
title: "Kinetic theory"
tags:
  - "MCF"
url:
  - "https://a.example"
contributors:
  - {"name": "Ada Lovelace", "github": "ada"}
comments: true
---

Some text.

---

More text.
"""


def test_split_page():
    """A page splits into its frontmatter and the rest, after the `---`."""
    page = "---\ntags: [MCF]\n---\n\nText\n"
    assert split_page(page) == ("tags: [MCF]\n", "\nText\n")


def test_split_page_without_frontmatter():
    """A page without frontmatter, or without a closing `---`, gives None."""
    assert split_page("# Title\n\n---\n\nText\n") is None
    assert split_page("---\ntags: [MCF]\n") is None


def test_formats_frontmatter_only():
    """Only the frontmatter is rewritten; the content is kept exactly."""
    assert format_page(HAND_WRITTEN) == FORMATTED


def test_formatted_page_unchanged():
    """A page already in the standard layout comes out unchanged."""
    assert format_page(FORMATTED) == FORMATTED


@pytest.fixture
def docs(tmp_path, monkeypatch):
    """A docs/ folder with one hand-written page and one formatted page."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs" / "notes").mkdir(parents=True)
    (tmp_path / "docs" / "notes" / "hand.md").write_text(HAND_WRITTEN)
    (tmp_path / "docs" / "formatted.md").write_text(FORMATTED)
    return tmp_path / "docs"


def test_main_formats_pages(docs, monkeypatch, capsys):
    """Run without arguments, it rewrites the pages not in the layout."""
    monkeypatch.setattr("sys.argv", ["format_notes.py"])
    main()
    assert (docs / "notes" / "hand.md").read_text() == FORMATTED
    assert (docs / "formatted.md").read_text() == FORMATTED
    assert "Formatted 1 page(s)." in capsys.readouterr().out


def test_main_check_lists_pages_and_fails(docs, monkeypatch, capsys):
    """With --check, it changes nothing, lists the pages, and fails."""
    monkeypatch.setattr("sys.argv", ["format_notes.py", "--check"])
    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code != 0
    assert (docs / "notes" / "hand.md").read_text() == HAND_WRITTEN
    assert "docs/notes/hand.md" in capsys.readouterr().out


def test_main_check_passes_when_formatted(docs, monkeypatch, capsys):
    """With --check, it passes once every page is in the layout."""
    (docs / "notes" / "hand.md").write_text(FORMATTED)
    monkeypatch.setattr("sys.argv", ["format_notes.py", "--check"])
    main()
    out = capsys.readouterr().out
    assert "All frontmatter is in the standard layout." in out


def test_invalid_yaml_names_the_page(docs, monkeypatch):
    """Frontmatter that isn't valid YAML fails with the page's path."""
    (docs / "broken.md").write_text("---\ntags: [MCF\n---\n\nText\n")
    monkeypatch.setattr("sys.argv", ["format_notes.py", "--check"])
    with pytest.raises(SystemExit, match="docs/broken.md"):
        main()
