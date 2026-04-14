import os
import subprocess
import sys

import yaml


def main():
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
        p
        for p in result.stdout.splitlines()
        if p.startswith("docs/") and p.endswith(".md")
    ]

    if not changed_files:
        print("No changed documentation files to check.")
        sys.exit(0)

    modified = []
    for filepath in changed_files:
        with open(filepath) as f:
            content = f.read()

        if not content.startswith("---\n"):
            continue

        try:
            # limit=2 ensures we only split on the first two occurrences of ---
            _, frontmatter_str, body = content.split("---\n", 2)
            meta = yaml.safe_load(frontmatter_str) or {}
        except (ValueError, yaml.YAMLError):
            continue

        tags = meta.get("tags")
        if not tags or not isinstance(tags, list):
            continue

        # normalise tags to match canonical form (case-insensitive), leave unknown tags unchanged
        normalised = []
        unknown = []
        for t in tags:
            if not (isinstance(t, str) and t):
                continue
            canonical = lookup.get(t.lower())
            if canonical is not None:
                normalised.append(canonical)
            else:
                normalised.append(t)
                unknown.append(t)

        if unknown:
            print(
                f"Warning: {filepath} contains tag(s) not in tags.yml: "
                + ", ".join(f"'{u}'" for u in unknown)
                + " — consider adding them to .github/tags.yml"
            )

        if normalised == tags:
            continue

        meta["tags"] = normalised
        key_order = ["tags", "doi", "contributors", "comments"]
        ordered_meta = {k: meta[k] for k in key_order if k in meta}
        ordered_meta.update({k: v for k, v in meta.items() if k not in ordered_meta})

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(
                ordered_meta, f, sort_keys=False, allow_unicode=True, width=float("inf")
            )
            f.write("---\n\n")
            # .lstrip() removes any leading whitespace/newlines from the original body
            f.write(body.lstrip())

        modified.append(filepath)

    if modified:
        print(f"Normalised tags in: {', '.join(modified)}")
    else:
        print(
            f"All tags in {len(changed_files)} changed file(s) are already canonical."
        )


if __name__ == "__main__":
    main()
