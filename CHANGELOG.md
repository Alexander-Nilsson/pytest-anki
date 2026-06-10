# Changelog

## [2.2.0-dev] — 2026-06-10

### Added
- `pytest_anki/_plugin/aniki_compat.py` — central version-compatibility seam for 8 version-gated functions (issue 001)
- `pytest_anki/_plugin/teardown.py` — `TeardownManager.shutdown()` extracts 7 inline teardown steps (issue 002)
- `pytest_anki/_plugin/qtbot.py` — `StandaloneQtBot` class replaces inline string constant in subprocess runner (issue 003)
- `pytest_anki/_plugin/hooks.py` — `HookRegistry` class replaces module-level `_snapshot_hooks`/`_restore_hooks` (issue 004)
- `pytest_anki/_plugin/testing.py` — `TestAnkiQtInit` class replaces closure-based `custom_init_factory` (issue 005)
### Changed
- `_plugin/` modules: 8 → 13 (5 new private modules)
- Subprocess runner imports `StandaloneQtBot` via `sys.path` instead of embedding raw code string

## [2.1.0] — 2026-06-10

### Added
- `@pytest.mark.anki_session(...)` marker for passing parameters to the fixture
- `anki_session_module` fixture (module-scoped, shares Anki across tests)
- `AnkiSession.reset_state()` for clearing addon modules between tests
- `py.typed` marker + full public type re-exports (`PathLike`, `UnpackedAddon`, `ConfigPaths`)
- Hook snapshot/restore in `loaded_addon()` for non-forked test isolation
- `CHANGELOG.md` file
- Docker test workflow (`make test-docker`, `docker-compose.yml`)
- `test-light` Makefile target for headless unit tests
- Version constraint files in `constraints/`

## [2.0.2] — 2026-06-10

### Fixed
- Include all source files in wheel build (fixes empty PyPI wheel)

## [2.0.1] — 2026-06-10

### Fixed
- `ty` type-checker compatibility: use keyword args for `pytest.skip`/`pytest.fail`
- Disable uv cache on lint and typecheck CI jobs
- Use `actions/setup-python` before `setup-uv` for reliable Python 3.9 install
- CI failures on macOS runner, segfault, E402

### Changed
- Migrate from mypy/pyright to `ty` for type checking

## [2.0.0] — 2026-06-09

### Added
- Qt6/PyQt6 support with auto-detection at import time
- `QT_API` env-var override for binding selection
- `QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox` only applies on Qt5 Linux
- `--anki-no-fork` CLI flag and `anki_force_fork` ini option to disable auto-forking
- `loaded_addon()` context manager for safe addon import/cleanup
- `skip_loading_addons` parameter for the `anki_session` fixture
- Pre-commit hooks (ruff + mypy)
- Python 3.14 CI
- Nightly CI schedule
- macOS test runner
- Web debugging via Selenium (optional dependency)
- Expanded CI matrix: 10 entries across Qt5/Qt6 and Anki 2.1.54–25.09

### Changed
- Package restructured: plugin code moved to `pytest_anki/_plugin/` (private), `pytest_anki/plugin.py` as public facade
- Migrated from Poetry to uv for dependency management
- Replaced flake8/pylint with ruff
- Replaced mypy/pyright with `ty` for type checking
- Selenium is now an optional dependency (extras: `selenium`, `web`)
- Anki/aqt moved from unconditional dependencies to extras only
- Package renamed to `pytest-anki2` on PyPI (namespace collision)

### Fixed
- 4 pre-existing type errors resolved
- `locale.getdefaultlocale()` deprecation in launch teardown
- Lazy-init `base_path` default instead of call at definition time
- QtWebEngine web-debugging tests isolated in subprocess
- CI stabilization across Qt5/Qt6 matrix
- Auto-forking via `pytest.mark.forked` (conftest.py)

### Removed
- Unconditional `anki`/`aqt` from `[project] dependencies` (must use extras)
- Stale `dependabot.yml` and unused `env_marker` module

## [1.0.0-beta.7] — 2025-03-15

### Added
- `addon_config_created` context manager
- `preset_anki_state` parameter for fixture-based API
- `set_anki_object_data` helper for `col.conf` ConfigManager API (Anki 2.1.45+)
- Compatibility with Anki's new `DeckId` NewType
- Test coverage for addon config management, addon loading, state updates
- Support for packed `.ankiaddon` files

### Fixed
- Collection access error when using `addon_config_created` without loaded profile
- Python 3.12 compatibility
- Qt6 nightly compatibility

## [1.0.0-beta.6] — 2024-08-20

### Added
- Python 3.11, 3.12 support
- Type annotations throughout
- Test for `--no-sandbox` flag on Linux

### Fixed
- `--no-sandbox` flag only applied on Linux (not macOS/Windows)
- PyQt6 compatibility for `QWebEngineProfile.defaultProfile()`

## [1.0.0-beta.5] — 2024-05-10

### Added
- Remote web debugging support via Selenium
- `run_with_chrome_driver()` and `reset_chrome_driver()` methods
- `chromium_version` property
- Web debugging tests

## [1.0.0-beta.4] — 2024-02-15

### Added
- `run_in_thread_and_wait()` for running tasks in QThreadPool
- `set_timeout()` for delayed task execution
- Deck management: `install_deck()`, `remove_deck()`, `deck_installed` context manager

## [1.0.0-beta.3] — 2023-10-01

### Added
- `create_addon_config()` API
- Anki state management: `update_anki_state()`, `AnkiStateUpdate` dataclass
- Support for `colconf_storage`, `profile_storage`, `meta_storage`

## [1.0.0-beta.2] — 2023-06-15

### Added
- Addon installation from source folders
- Addon configuration via `addon_configs` parameter
- Test samples for addon testing
- CI with GitHub Actions

## [1.0.0-beta.1] — 2023-03-01

### Added
- Initial `anki_session` pytest fixture
- Basic Anki profile management
- Addon loading via `load_addon()`
- QtBot integration
- Support for Anki 2.1.49–2.1.54
- Python 3.9, 3.10 support

[2.0.2]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v2.0.2
[2.0.1]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v2.0.1
[2.0.0]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v2.0.0
[1.0.0-beta.7]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.7
[1.0.0-beta.6]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.6
[1.0.0-beta.5]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.5
[1.0.0-beta.4]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.4
[1.0.0-beta.3]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.3
[1.0.0-beta.2]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/Alexander-Nilsson/pytest-anki/releases/tag/v1.0.0-beta.1
