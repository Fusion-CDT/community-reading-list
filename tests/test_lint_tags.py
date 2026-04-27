from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "lint_tags.py"


def load_lint_module(
    monkeypatch: pytest.MonkeyPatch, changed_docs: list[Path] | list[None]
):
    """Load lint_tags and optionally mock changed docs returned by git diff."""
    spec = importlib.util.spec_from_file_location("lint_tags", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(module, "get_changed_docs", lambda base_sha: changed_docs)

    return module


def mock_write_repo_files(
    tmp_path: Path, canonical_tags: list[str], frontmatter_tags: list[str]
):
    # Build the expected directories for the tag linter
    (tmp_path / ".github").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)

    # Create a new tags file with the canonical_tags, using the same 2-space-indented
    # block-sequence format as the real .github/tags.yml so appended items parse correctly.
    tmp_tags = tmp_path / ".github" / "tags.yml"
    with tmp_tags.open("w", encoding="utf-8") as f:
        f.write("tags:\n")
        for tag in canonical_tags:
            f.write(f"  - {tag}\n")

    # Create a new MarkDown file with the frontmatter_tags
    tmp_file = tmp_path / "docs" / "fake.md"
    with tmp_file.open("w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.safe_dump({"tags": frontmatter_tags}, f, sort_keys=False)
        f.write("---\n\nBody\n")

    return tmp_tags, tmp_file


def test_normalises_known_tags_and_keeps_unknown(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    tags_path, doc_path = mock_write_repo_files(
        tmp_path,
        canonical_tags=["EPFL", "MCF", "SFQED"],
        frontmatter_tags=["epfl", "mcf", "unknownTag"],
    )

    module = load_lint_module(monkeypatch, changed_docs=[doc_path])

    module.main(base_sha="abc123", tags_path=tags_path)
    output = capsys.readouterr().out

    assert "Warning:" in output
    assert "unknownTag" in output
    assert "Normalised tags in:" in output
    assert "fake.md" in output

    rewritten = yaml.safe_load(
        doc_path.read_text(encoding="utf-8").split("---\n", 2)[1]
    )
    assert rewritten["tags"] == ["EPFL", "MCF", "unknownTag"]

    tags_in_file = yaml.safe_load(tags_path.read_text(encoding="utf-8")).get("tags", [])
    assert "unknownTag" in tags_in_file
    assert "Added" in output


def test_unknown_tag_not_duplicated_in_tags_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """An unknown tag that appears in two docs should only be added to tags.yml once."""
    (tmp_path / ".github").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)

    tags_path = tmp_path / ".github" / "tags.yml"
    with tags_path.open("w", encoding="utf-8") as f:
        f.write("tags:\n  - MCF\n")

    doc_paths = []
    for name in ("a.md", "b.md"):
        p = tmp_path / "docs" / name
        with p.open("w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.safe_dump({"tags": ["newTag"]}, f)
            f.write("---\n\nBody\n")
        doc_paths.append(p)

    module = load_lint_module(monkeypatch, changed_docs=doc_paths)
    module.main(base_sha="abc123", tags_path=tags_path)

    tags_in_file = yaml.safe_load(tags_path.read_text(encoding="utf-8")).get("tags", [])
    assert tags_in_file.count("newTag") == 1


def test_existing_unknown_tag_not_re_added(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    """A tag already in tags.yml (but not matching any doc tag by case) is not added again."""
    tags_path, doc_path = mock_write_repo_files(
        tmp_path,
        canonical_tags=["MCF", "AlreadyThere"],
        frontmatter_tags=["alreadythere"],
    )

    module = load_lint_module(monkeypatch, changed_docs=[doc_path])
    module.main(base_sha="abc123", tags_path=tags_path)

    tags_in_file = yaml.safe_load(tags_path.read_text(encoding="utf-8")).get("tags", [])
    assert tags_in_file.count("AlreadyThere") == 1
    assert tags_in_file.count("alreadythere") == 0


def test_no_changed_docs_exits_cleanly(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    tags_path, _ = mock_write_repo_files(
        tmp_path,
        canonical_tags=["MCF", "SFQED"],
        frontmatter_tags=[],
    )

    module = load_lint_module(monkeypatch, changed_docs=[])

    exit_code = module.main(base_sha="abc123", tags_path=tags_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "No changed documentation files to check." in output


def test_already_canonical_reports_no_changes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    tags_path, doc_path = mock_write_repo_files(
        tmp_path, canonical_tags=["EPFL", "MCF"], frontmatter_tags=["EPFL", "MCF"]
    )
    module = load_lint_module(monkeypatch, changed_docs=[doc_path])

    module.main(base_sha="abc123", tags_path=tags_path)
    output = capsys.readouterr().out

    assert "already canonical" in output
