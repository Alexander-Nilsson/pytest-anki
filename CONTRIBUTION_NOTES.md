# Contribution Notes — pytest-anki

## Project State

This repo is **pytest-anki**, a pytest plugin for testing Anki add-ons. The `v2` branch is a
work-in-progress rewrite of the plugin (PR #32 on the upstream repo). The `main` branch is
the last stable release (1.0.0b7 on PyPI).

## Discovery Log

### Package Manager

The v2 branch uses **uv** (`[tool.uv]` in pyproject.toml, `uv.lock` existing).
Pre-commit hooks are configured in `.pre-commit-config.yaml` (ruff + mypy, matching CI).
Built with hatchling.

### Entry Point

The plugin entry point is registered via `[project.entry-points.pytest11]` →
`pytest_anki.plugin`. The `plugin.py` module at `pytest_anki/plugin.py` is the public
interface, re-exporting from `pytest_anki._plugin`.

### Test Framework

Tests use pytest (self-testing plugin). No tox, no nox. CI runs on push/PR via
`.github/workflows/general.yml`.

### Python & Anki Versions

- Requires Python >=3.9 (declared via `requires-python = ">=3.9"`)
- Anki dev dependency: `anki  [gui]` in `[dependency-groups.anki]`

### Key Structural Decisions (new in v2)

- Plugin code lives under `pytest_anki/_plugin/` (private implementation), with
  `pytest_anki/plugin.py` as the public API facade.
- No `pytest_anki/__init__.py` exports anything; user-facing API is `pytest_anki.plugin`.
- Anki is a dev dependency only (not a runtime dependency), allowing pip-install without Anki.
- Selenium is now an optional dependency (`[project.optional-dependencies]` → `selenium` / `web` extras).
- Qt API binding is auto-detected at import time (PyQt6 > PyQt5) via `pytest_anki/_plugin/compat.py`.

## TODO Status (WIP)

- [x] Simplify Anki dev dependency constraint — removed `<25.2` upper bound.
- [x] Make Selenium an optional dependency.
- [x] Add Qt6/PyQt6 support (compat layer).
- [x] Fix `--no-sandbox` Chrome flag condition (only apply on Qt5 Linux).
- [x] Add Qt5 + Qt6 CI matrix jobs (8 entries, 4 per binding).
- [x] Reintroduce 25.02 into CI matrix (Qt6-only, Python 3.10). May need fixes for API changes.
- [x] Restore type-checking (mypy, pyright) and linting (ruff) CI steps (separate jobs).
- [x] Make Selenium optional in CI (tests skip via importorskip; one matrix entry installs selenium for coverage).
- [x] Update README: uv instructions, Python 3.9+, Qt6/Qt5 support note, selenium extras note.
- [x] Integration test using sample addons — covered by existing `test_fixtures.py` and `test_anki_session.py` (sample_addon_three, sample_addon_four, state_checker_addon).
- [x] Add `.pre-commit-config.yaml` with ruff + mypy hooks matching CI.
- [x] Add `QT_API` env-var override (`qt5`/`qt6`/`pyqt5`/`pyqt6`) for Qt binding selection.
- [x] Make auto-forking opt-out via `--anki-no-fork` flag or `anki_force_fork = false` ini option.
- [x] Add nightly CI schedule (`cron: "0 3 * * *"`).
- [x] Annotate 4 pre-existing type errors with specific `# type: ignore[<code>]` + explanations.

## Open Decisions / Unresolved Questions

1. **Qt detection strategy**: Auto-detection with optional `QT_API` env-var override (implemented).
   `QT_VERSION_MAJOR` and `QT_PREFIX` exported for conditional logic. See `_plugin/compat.py`.
2. **Selenium optionality**: lazy import with `AnkiSessionError` and suggestion message.
   Type annotations guarded by `TYPE_CHECKING`.
3. **pyproject.toml** still has `qt_api = "pyqt6"` under `[tool.pytest.ini_options]` — this
   is the pytest-qt setting, not our compat layer. Kept as sensible default for Qt6-first
   environments.
4. **Pre-existing type errors** — 4 mypy (3 in compat.py no-redef/assignment, 1 in
   launch.py `ProfileManager` arg-type), 2 pyright (test_plugin_config.py Parser
   attribute access). All annotated with `# type: ignore[<code>]` or excluded.
5. **Test suite** cannot run locally — Qt6 WebEngine requires `libxml2.so.2` ABI unavailable on
   this system. Full validation requires CI (Ubuntu 24.04 with `tlambert03/setup-qt-libs@v1`).
