# Tests

The tests in this directory cover the scripts in [`scripts/`](../scripts/).

| Test file | Script under test |
|-----------|-------------------|
| `test_lint_tags.py` | `scripts/lint_tags.py` |

## Running the tests

The project uses [`uv`](https://docs.astral.sh/uv/) for dependency management. From the repository root, run:

```sh
uv run --with pytest pytest
```

To run a single test file:

```sh
uv run --with pytest pytest tests/test_lint_tags.py
```

To run a specific test by name:

```sh
uv run --with pytest pytest -k test_normalises_known_tags_and_keeps_unknown
```

## What the tests cover

`test_lint_tags.py` tests three behaviours of the tag linter:

- **Known tags are normalised** — tags present in `.github/tags.yml` are rewritten to their canonical casing (e.g. `epfl` → `EPFL`).
- **Unknown tags trigger a warning** — tags not in the allowlist are left unchanged and a warning is printed so CI surfaces them.
- **Already-canonical tags are reported as unchanged** — the linter reports no changes when every tag already matches its canonical form.
