"""
Split an issue created from one of our issue forms into the form's answers.

When someone submits an issue form, GitHub writes each field into the issue
body as a `### <label>` heading followed by the answer. For example, a paper
suggestion looks like this:

    ### DOI

    10.1063/1.2178779

    ### Location and filename

    plasma/MCF/abel2013multiscale

    ### Tags

    MCF, Gyrokinetics

    ### Content

    A clear introduction to multiscale gyrokinetics.

    ### Images (optional)

    [figure 1.png](https://github.com/user-attachments/assets/1a2b3c)

    ### Your name (optional)

    _No response_

`load_fields` reads the form the issue was submitted with (for a paper, this
is `.github/ISSUE_TEMPLATE/suggest-literature-paper.yml`), which gives each
field's label and id.

`parse_body` then matches each `### <label>` heading to its field's id, and
returns:

    {
        "doi": "10.1063/1.2178779",
        "filepath": "plasma/MCF/abel2013multiscale",
        "tags": "MCF, Gyrokinetics",
        "content": "A clear introduction to multiscale gyrokinetics.",
        "user_images": [{"name": "figure 1.png",
                         "url": "https://github.com/user-attachments/assets/1a2b3c"}],
        "contributor_name": "",
    }

Fields left empty become "", and each uploaded file becomes a {"name", "url"}
dictionary.
"""

import json
import uuid
from pathlib import Path
from typing import Any

import yaml

TEMPLATE_DIR = Path(".github/ISSUE_TEMPLATE")


def load_fields(template_path: Path) -> dict[str, tuple[str, str]]:
    """Return {label: (id, type)} for every answerable field in the template."""
    with template_path.open(encoding="utf-8") as f:
        template = yaml.safe_load(f)
    fields = {}
    for item in template["body"]:
        if item["type"] == "markdown": # skip this (part of the form)
            continue
        label = item["attributes"]["label"]
        fields[label] = (item["id"], item["type"])
    return fields


def parse_body(body: str, fields: dict[str, tuple[str, str]]) -> dict[str, Any]:
    """Split the issue body (example at top of file) into {field id: answer}.

    `fields` comes from `load_fields`: {label: (id, type)}. Each `### <label>`
    heading in the body is matched against those labels, and each answer is
    returned under the field's id, e.g. the answer under `### DOI` as "doi".

    Only headings matching a field label start a new field, so a `###`
    heading written inside an answer stays part of that answer.
    """
    # Pass 1: collect the lines under each field's `### <label>` heading
    sections: dict[str, list[str]] = {} # {"DOI": ..., "Tags": ..., }
    current: str | None = None  # section we're in
    for line in body.splitlines():
        heading = line.removeprefix("### ").strip() if line.startswith("### ") else None
        if heading in fields: # new field starts here
            current = heading
            sections[current] = []
        elif current is not None:  # H3 (`###`) heading in answer; keep this line
            sections[current].append(line)

    # Pass 2: clean up each answer, and key it by the field's id.
    # Each section is still the raw lines under its heading, including the
    # blank lines GitHub puts around each answer, e.g.
    #     {
    #         "DOI": ["", "10.1063/1.2178779", ""],
    #         "Location and filename": ["", "plasma/MCF/abel2013multiscale", ""],
    #         "Tags": ["", "MCF, Gyrokinetics", ""],
    #     }
    # Joining the lines and stripping the result removes those blank lines,
    # but keeps any inside the answer (e.g. between paragraphs).
    parsed: dict[str, Any] = {}
    for label, (field_id, field_type) in fields.items():
        value = "\n".join(sections.get(label, [])).strip()
        if value == "_No response_": # GitHub writes this for fields left empty
            value = ""
        if field_type == "upload": # image
            parsed[field_id] = parse_uploads(value)
        else:
            parsed[field_id] = value
    return parsed


def parse_uploads(answer: str) -> list[dict[str, str]]:
    """Return image uploads as [{"name": ..., "url": ...}].

    GitHub writes each uploaded file as a Markdown link on its own line. For
    example, an answer with two images:

        [figure 1.png](https://github.com/user-attachments/assets/1a2b3c)
        [convergence.png](https://github.com/user-attachments/assets/4d5e6f)

    becomes:

        [
            {"name": "figure 1.png", "url": "https://github.com/user-attachments/assets/1a2b3c"},
            {"name": "convergence.png", "url": "https://github.com/user-attachments/assets/4d5e6f"},
        ]
    """
    uploads = []
    for line in answer.splitlines():
        # "[figure 1.png](https://...)" -> "figure 1.png", "](", "https://..."
        name, separator, url = line.strip().removeprefix("[").removesuffix(")").partition("](")
        if separator:
            uploads.append({"name": name, "url": url})
    return uploads


def set_outputs(outputs: dict[str, Any], output_path: str | Path) -> None:
    """Append {name: value} to a GitHub Actions output file.

    Each value is written in GitHub's format for values that may span several
    lines, between two copies of a marker:

        name<<EOF_3f9c2a71
        value
        EOF_3f9c2a71

    Values that aren't strings are written as JSON.
    """
    with open(output_path, "a", encoding="utf-8") as f:
        for name, value in outputs.items():
            if not isinstance(value, str):
                value = json.dumps(value)
            # The marker must not appear in the value, so use a random one
            marker = f"EOF_{uuid.uuid4().hex}"
            f.write(f"{name}<<{marker}\n{value}\n{marker}\n")

