"""
Parse an issue created from one of our issue forms into its fields.

GitHub writes each issue form field into the issue body as a `### <label>`
heading followed by the answer. This script reads the form template from
`.github/ISSUE_TEMPLATE/`, splits the body on those headings, and writes each
answer to `$GITHUB_OUTPUT` as `parsed_<field id>`, plus all of them as `json`.

We used to use the `issue-ops/parser` action for this, but it rejects forms
containing an `upload` field. Upload fields are returned here as a JSON list
of `{"name": ..., "url": ...}`, one per uploaded file.

Usage (in a workflow step, with the issue body in the ISSUE_BODY variable):

    python3 scripts/parse_issue.py <template filename>
"""

import json
import os
import re
import sys
import uuid
from pathlib import Path

import yaml

TEMPLATE_DIR = Path(".github/ISSUE_TEMPLATE")

# GitHub writes this for fields left empty
NO_RESPONSE = "_No response_"

# An uploaded file, e.g. [figure.png](https://github.com/user-attachments/assets/...)
UPLOAD_LINK = re.compile(r"\[(?P<name>[^\]]+)\]\((?P<url>https://[^)\s]+)\)")


def load_fields(template_path):
    """Return {label: (id, type)} for every answerable field in the template."""
    template = yaml.safe_load(Path(template_path).read_text(encoding="utf-8"))
    fields = {}
    for item in template.get("body", []):
        if item.get("type") == "markdown":
            continue
        label = item["attributes"]["label"]
        fields[label] = (item.get("id"), item["type"])
    return fields


def parse_body(body, fields):
    """Split the issue body into {field id: answer}.

    Only headings matching a field label start a new field, so a `###`
    heading written inside an answer stays part of that answer.
    """
    answers = {}
    current = None
    lines = []

    def finish():
        if current is not None:
            answers[current] = "\n".join(lines)

    for line in body.replace("\r\n", "\n").split("\n"):
        heading = line[4:].strip() if line.startswith("### ") else None
        if heading in fields:
            finish()
            current, lines = heading, []
        elif current is not None:
            lines.append(line)
    finish()

    parsed = {}
    for label, (field_id, field_type) in fields.items():
        value = answers.get(label, "").strip()
        if value == NO_RESPONSE:
            value = ""
        if field_type == "upload":
            parsed[field_id] = [m.groupdict() for m in UPLOAD_LINK.finditer(value)]
        else:
            parsed[field_id] = value
    return parsed


def write_outputs(parsed, output_path):
    """Append the parsed fields to a GitHub Actions output file."""
    with open(output_path, "a", encoding="utf-8") as f:
        items = {f"parsed_{k}": v for k, v in parsed.items()}
        items["json"] = parsed
        for name, value in items.items():
            if not isinstance(value, str):
                value = json.dumps(value)
            # Multi-line values need a delimiter that can't appear in the value
            delimiter = f"EOF_{uuid.uuid4().hex}"
            f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    fields = load_fields(TEMPLATE_DIR / argv[1])
    parsed = parse_body(os.environ.get("ISSUE_BODY", ""), fields)
    print(json.dumps(parsed, indent=2))
    write_outputs(parsed, os.environ["GITHUB_OUTPUT"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
