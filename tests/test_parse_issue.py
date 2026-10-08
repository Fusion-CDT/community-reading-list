from pathlib import Path

import pytest

from parse_issue import load_fields, parse_body, write_outputs

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
    path = tmp_path / "template.yml"
    path.write_text(TEMPLATE)
    return load_fields(path)


def test_parses_fields_and_uploads(fields):
    body = (
        "### DOI\n\n10.1063/1.2178779\n\n"
        "### Content\n\nSee the figure.\n\n"
        "### Images (optional)\n\n"
        "[angular velocity.png](https://github.com/user-attachments/assets/abc)\n"
        "[plot.jpg](https://github.com/user-attachments/assets/def)\n\n"
        "### Your name (optional)\n\nAda Lovelace\n"
    )
    assert parse_body(body, fields) == {
        "doi": "10.1063/1.2178779",
        "content": "See the figure.",
        "user_images": [
            {"name": "angular velocity.png", "url": "https://github.com/user-attachments/assets/abc"},
            {"name": "plot.jpg", "url": "https://github.com/user-attachments/assets/def"},
        ],
        "contributor_name": "Ada Lovelace",
    }


def test_empty_fields(fields):
    body = (
        "### DOI\n\n_No response_\n\n### Content\n\nText\n\n"
        "### Images (optional)\n\n_No response_\n\n### Your name (optional)\n\n_No response_\n"
    )
    parsed = parse_body(body, fields)
    assert parsed["doi"] == ""
    assert parsed["user_images"] == []
    assert parsed["contributor_name"] == ""


def test_headings_inside_an_answer_stay_in_it(fields):
    body = "### Content\r\n\r\nIntro\r\n\r\n### My own heading\r\n\r\nMore\r\n"
    assert parse_body(body, fields)["content"] == "Intro\n\n### My own heading\n\nMore"


def test_writes_multiline_outputs(tmp_path):
    output = tmp_path / "output"
    write_outputs({"content": "line 1\nline 2", "user_images": []}, output)
    text = output.read_text()
    assert "parsed_content<<" in text
    assert "line 1\nline 2\n" in text
    assert "parsed_user_images<<" in text and "\n[]\n" in text


def test_all_templates_parse():
    for path in Path(".github/ISSUE_TEMPLATE").glob("*.yml"):
        assert load_fields(path), path
