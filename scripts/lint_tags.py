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


def lint_tags(
    changed_files: list[Path], existing_tags: dict[str, str]
) -> tuple[list[Path], list[str]]:
    modified_files: list[Path] = []
    all_unknown: list[str] = []
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
            )
            all_unknown.extend(u for u in unknown if u not in all_unknown)

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

    return modified_files, all_unknown


def append_unknown_tags(tags_path: Path, unknown_tags: list[str]) -> list[str]:
    """Append unknown tags to tags.yml; returns the tags actually added (duplicates skipped)."""
    with tags_path.open(encoding="utf-8") as f:
        existing = yaml.safe_load(f).get("tags", [])
    existing_lower = {t.lower() for t in existing}
    new_tags = [t for t in unknown_tags if t.lower() not in existing_lower]
    if new_tags:
        with tags_path.open("a", encoding="utf-8") as f:
            for tag in new_tags:
                f.write(f"  - {tag}\n")
    return new_tags


def main(
    base_sha: str | None = None,
    tags_path: str | Path = Path(".github/tags.yml"),
) -> int:
    tags_path = Path(tags_path)
    canonical_tags = load_canonical_tags(tags_path)

    # Find .md files added or modified in this PR
    if base_sha is None:
        base_sha = os.environ["BASE_SHA"]

    changed_files = get_changed_docs(base_sha)

    if not changed_files:
        print("No changed documentation files to check.")
        return 0

    modified_files, unknown_tags = lint_tags(changed_files, canonical_tags)

    if unknown_tags:
        added = append_unknown_tags(tags_path, unknown_tags)
        if added:
            print(
                f"Added {len(added)} unknown tag(s) to {tags_path} for review: "
                + ", ".join(f"'{t}'" for t in added)
            )

    if modified_files:
        print(f"Normalised tags in: {[f.as_posix() for f in modified_files]}")
    else:
        print(
            f"All tags in {len(changed_files)} changed file(s) are already canonical."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
