# pytest-anki API Reference

## Fixtures

### `anki_session`

The main pytest fixture. Yields an `AnkiSession` instance.

Parameters can be passed via the `@pytest.mark.anki_session()` marker (recommended):

```python
@pytest.mark.anki_session(profile_name="test", load_profile=True)
def test_with_profile(anki_session: AnkiSession):
    ...
```

Or via indirect parametrization:

```python
@pytest.mark.parametrize("anki_session", [{"profile_name": "test", "load_profile": True}], indirect=True)
def test_with_profile(anki_session: AnkiSession):
    ...
```

See `pytest_anki.plugin.anki_session` docstring for all parameters.

### `anki_session_module`

Module-scoped variant of `anki_session`. Starts Anki once per module and reuses the same session for all tests. Accepts the same parameters.

```python
def test_a(anki_session_module: AnkiSession):
    ...

def test_b(anki_session_module: AnkiSession):
    # Shares the same Anki process as test_a
    ...
```

Use with `--anki-no-fork` to share a single process across all tests in the module.

---

## Classes

### `AnkiSession`

Full-featured session wrapper around a running Anki instance.

| Method | Description |
|---|---|
| `load_profile()` / `unload_profile()` | Manage Anki user profile lifecycle |
| `install_deck(path)` / `remove_deck(deck_id)` | Manage `.apkg` decks |
| `install_addon(path_or_name, source_dir=None)` | Install packed (`.ankiaddon`) or unpacked add-ons |
| `write_addon_config(package, config, meta=None)` | Write `config.json` / `meta.json` |
| `loaded_addon(package)` | Context manager that cleans up `sys.modules` and restores hook registries on exit |
| `reset_state()` | Clear addon modules from `sys.modules` and process pending Qt events |
| `run_in_thread_and_wait(target, timeout=15000)` | Run a function in the Qt event loop with timeout |
| `set_timeout(callback, delay_ms)` | Schedule a callback on the Qt event loop |
| `run_with_chrome_driver(webview_type, handler)` | Attach Selenium ChromeDriver to Anki webviews |
| `update_anki_state(updates: AnkiStateUpdate)` | Pre-set `col.conf`, `pm.profile`, `pm.meta` |

### `AnkiStateUpdate`

Dataclass for pre-configuring Anki object state:

- `colconf_storage: Optional[Dict]` — `mw.col.conf` updates
- `profile_storage: Optional[Dict]` — `mw.pm.profile` updates
- `meta_storage: Optional[Dict]` — `mw.pm.meta` updates (applied before add-on load)

### `AnkiWebViewType`

Enum: `main_webview`, `top_toolbar`, `bottom_toolbar`, `previewer`, `browser_card_info`, `card_layout`, etc.

### `AnkiSessionError`

Exception raised on session errors (e.g., timeout, profile load failures).

### `PathLike`

`Union[str, Path]` — type alias for path arguments in the public API.

### `UnpackedAddon`

`Tuple[str, PathLike]` — type alias for (package_name, addon_source_path).

### `ConfigPaths`

`NamedTuple(default_config: Optional[Path], user_config: Optional[Path])` — paths returned by `create_addon_config()`.

---

## CLI Options

| Flag | Effect |
|---|---|
| `--anki-no-fork` | Disable per-test forking (shares single Anki process) |

## pytest ini options

| Key | Type | Default | Description |
|---|---|---|---|
| `anki_force_fork` | `bool` | `true` | Fork each test into a subprocess |

## pytest markers

| Marker | Description |
|---|---|
| `@pytest.mark.anki_session(**kwargs)` | Pass parameters to the `anki_session` fixture without indirect parametrization |
