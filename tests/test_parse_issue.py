from pathlib import Path

import pytest

from parse_issue import load_fields, parse_body, parse_uploads, set_outputs

REPO = Path(__file__).resolve().parents[1]
ASSETS = "https://github.com/user-attachments/assets/"

# A small issue form with one field of each type our forms use
TEMPLATE = """
name: Test
body:
  - type: markdown
    attributes:
      value: Intro text, not a field.
  - type: input
    id: doi
    attributes:
      label: DOI
  - type: textarea
    id: content
    attributes:
      label: Content
  - type: upload
    id: user_images
    attributes:
      label: Images (optional)
  - type: input
    id: contributor_name
    attributes:
      label: Your name (optional)
"""


@pytest.fixture
def fields(tmp_path):
    """The fields of TEMPLATE, as load_fields reads them."""
    path = tmp_path / "template.yml"
    path.write_text(TEMPLATE)
    return load_fields(path)


def test_parses_fields_and_uploads(fields):
    """Each answer is returned under its field's id, uploads as a list."""
    body = (
        "### DOI\n\n10.1063/1.2178779\n\n"
        "### Content\n\nSee the figure.\n\n"
        "### Images (optional)\n\n"
        f"[angular velocity.png]({ASSETS}abc)\n"
        f"[plot.jpg]({ASSETS}def)\n\n"
        "### Your name (optional)\n\nAda Lovelace\n"
    )
    assert parse_body(body, fields) == {
        "doi": "10.1063/1.2178779",
        "content": "See the figure.",
        "user_images": [
            {"name": "angular velocity.png", "url": ASSETS + "abc"},
            {"name": "plot.jpg", "url": ASSETS + "def"},
        ],
        "contributor_name": "Ada Lovelace",
    }


def test_empty_fields(fields):
    """Fields left empty (`_No response_`) become "", or [] for uploads."""
    body = (
        "### DOI\n\n_No response_\n\n"
        "### Content\n\nText\n\n"
        "### Images (optional)\n\n_No response_\n\n"
        "### Your name (optional)\n\n_No response_\n"
    )
    parsed = parse_body(body, fields)
    assert parsed["doi"] == ""
    assert parsed["user_images"] == []
    assert parsed["contributor_name"] == ""


def test_headings_inside_an_answer_stay_in_it(fields):
    """A `###` heading that isn't a field's label stays in the answer.

    The body uses `\\r\\n` line breaks, as the web form sends.
    """
    body = "### Content\r\n\r\nIntro\r\n\r\n### My own heading\r\n\r\nMore\r\n"
    content = parse_body(body, fields)["content"]
    assert content == "Intro\n\n### My own heading\n\nMore"


def test_writes_multiline_outputs(tmp_path):
    """Outputs are written as `name<<marker`, value, marker.

    Values that aren't strings, such as the list of uploads, become JSON.
    """
    output = tmp_path / "output"
    set_outputs({"content": "line 1\nline 2", "user_images": []}, output)
    text = output.read_text()
    assert "content<<" in text
    assert "line 1\nline 2\n" in text
    assert "user_images<<" in text and "\n[]\n" in text


def test_parse_uploads_ignores_other_lines():
    """Lines that aren't upload links, e.g. typed text, are skipped."""
    answer = (
        f"[figure 1.png]({ASSETS}abc)\n"
        "\n"
        "Some text a contributor typed\n"
        f"[plot.jpg]({ASSETS}def)\n"
    )
    assert parse_uploads(answer) == [
        {"name": "figure 1.png", "url": ASSETS + "abc"},
        {"name": "plot.jpg", "url": ASSETS + "def"},
    ]


def test_all_templates_parse():
    """Every issue form in the repository can be read by load_fields."""
    forms = sorted((REPO / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
    assert forms
    for path in forms:
        assert load_fields(path), path
