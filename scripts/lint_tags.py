import os
import subprocess
from pathlib import Path

import yaml


def load_canonical_tags(tags_path: Path):
    with tags_path.open(encoding="utf-8") as f:
        allowlist = yaml.safe_load(f).get("tags", [])
    return {t.lower(): t for t in allowlist}


def get_changed_docs(base_sha: str):
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
        Path(p)
        for p in result.stdout.splitlines()
        if p.startswith("docs/") and p.endswith(".md")
    ]

    return changed_files


def lint_tags(changed_files: list[Path], existing_tags: dict[str, str]):
    modified_files: list[Path] = []
    for filepath in changed_files:
        with filepath.open(encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---\n"):
            continue

        try:
            # limit=2 ensures we only split on the first two occurrences of ---
            _, frontmatter_str, body = content.split("---\n", 2)
            file_metadata = yaml.safe_load(frontmatter_str) or {}
        except (ValueError, yaml.YAMLError):
            continue

        tags = file_metadata.get("tags")
        if not tags or not isinstance(tags, list):
            continue

        # normalise tags to match canonical form (case-insensitive), leave unknown tags unchanged
        normalised = []
        unknown = []
        for t in tags:
            if not (isinstance(t, str) and t):
                continue
            canonical = existing_tags.get(t.lower())
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

        file_metadata["tags"] = normalised
        # Keep tags at the top and preserve the existing order of all other keys
        output_meta = {"tags": normalised}
        output_meta.update({k: v for k, v in file_metadata.items() if k != "tags"})

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(
                output_meta, f, sort_keys=False, allow_unicode=True, width=float("inf")
            )
            f.write("---\n\n")
            # .lstrip() removes any leading whitespace/newlines from the original body
            f.write(body.lstrip())

        modified_files.append(filepath)

    return modified_files


def main(
    base_sha: str | None = None,
    tags_path: str | Path = Path(".github/tags.yml"),
) -> int:
    canonical_tags = load_canonical_tags(Path(tags_path))

    # Find .md files added or modified in this PR
    if base_sha is None:
        base_sha = os.environ["BASE_SHA"]

    changed_files = get_changed_docs(base_sha)

    if not changed_files:
        print("No changed documentation files to check.")
        return 0

    modified_files = lint_tags(changed_files, canonical_tags)

    if modified_files:
        print(f"Normalised tags in: {[f.as_posix() for f in modified_files]}")
    else:
        print(
            f"All tags in {len(changed_files)} changed file(s) are already canonical."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
