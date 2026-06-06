# Changelog

## 2.0.0 (2025-06-06)

### Features
- Add `--anki-no-fork` CLI flag and `anki_force_fork` ini option to opt out of automatic test forking.
- Add `QT_API` environment variable override (`qt5`/`qt6`/`pyqt5`/`pyqt6`) for explicit Qt binding selection.
- Support Anki 25.07 and 25.09 in CI matrix.
- Python 3.13 added to CI test matrix.

### Improvements
- Auto-fork all tests by default via `pytest_collection_modifyitems`.
- Replace `pytest-forked` with xdist `>=3.0` native forking.
- Make Selenium an optional dependency (`selenium`/`web` extras).
- Add Qt6/PyQt6 support via compat layer with auto-detection.
- Split `qt6` extra into `qt6-system` and `qt6-pypi` for cross-distro compatibility.
- Pre-existing type errors annotated with specific `# type: ignore` codes.
- `.pre-commit-config.yaml` added with ruff + mypy hooks.
- Nightly CI schedule to catch regressions from Anki rolling releases.

### Documentation
- README rewritten with uv instructions, Qt6/Qt5 setup guide, selenium extras.
- Expanded usage section with comprehensive API examples.
- Documented local testing limitations (Qt6 ABI compatibility).

### Testing
- Tests added for `QT_API` env var mapping and `--anki-no-fork` option.
- Selenium tests skip gracefully via `importorskip`.

### Maintenance
- Bump pytest from `~=6.2.5` to `>=7.0`.
- Remove dead code: `config.py`, `anki-current.json`, stale build references.
- Lock file upgraded for Python 3.14 compatibility (flask/werkzeug).
- CI matrix expanded to 10 entries covering Qt5 + Qt6 across Anki 2.1.54–25.09.
- Lint (ruff) and typecheck (mypy + pyright) CI jobs restored.

## 1.0.0b7

- Last stable release on PyPI. See [GitHub releases](https://github.com/Alexander-Nilsson/pytest-anki/releases) for earlier changelogs.
