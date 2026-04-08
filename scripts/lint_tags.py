import os
import subprocess
import sys

import yaml

# Load canonical allowlist
with open(".github/tags.yml") as f:
    allowlist = yaml.safe_load(f).get("tags", [])
lookup = {t.lower(): t for t in allowlist}

# Find .md files added or modified in this PR
base_sha = os.environ["BASE_SHA"]
result = subprocess.run(
    [
        "git",
        "diff",
        "--name-only",
        "--diff-filter=AM",
        f"{base_sha}...HEAD",
    ],
    capture_output=True,
    text=True,
    check=True,
)
changed_files = [
    p for p in result.stdout.splitlines() if p.startswith("docs/") and p.endswith(".md")
]

if not changed_files:
    print("No changed documentation files to check.")
    sys.exit(0)

modified = []
for filepath in changed_files:
    with open(filepath) as f:
        content = f.read()

    if not content.startswith("---"):
        continue

    parts = content.split("---", 2)
    if len(parts) < 3:
        continue

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        continue

    tags = meta.get("tags")
    if not tags or not isinstance(tags, list):
        continue

    # Normalise: match canonical form (case-insensitive), fall back to str.title()
    normalised = [
        lookup.get(t.lower(), t.title()) for t in tags if isinstance(t, str) and t
    ]
    if normalised == tags:
        continue

    meta["tags"] = normalised
    key_order = ["tags", "doi", "contributors", "comments"]
    ordered = {k: meta[k] for k in key_order if k in meta}
    ordered.update({k: v for k, v in meta.items() if k not in ordered})
    new_frontmatter = (
        "---\n"
        + yaml.dump(
            ordered,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=float("inf"),
        )
        + "---\n"
    )
    with open(filepath, "w") as f:
        f.write(new_frontmatter + parts[2])
    modified.append(filepath)

if modified:
    print(f"Normalised tags in: {', '.join(modified)}")
else:
    print(f"All tags in {len(changed_files)} changed file(s) are already canonical.")
