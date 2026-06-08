# pytest-anki API Reference

## Fixtures

### `anki_session`

The main pytest fixture. Yields an `AnkiSession` instance.

Supports indirect parametrization via `@pytest.mark.parametrize` — pass a `dict` of keyword arguments:

```python
@pytest.mark.parametrize("anki_session", [{"profile_name": "test", "load_profile": True}], indirect=True)
def test_with_profile(anki_session: AnkiSession):
    ...
```

See `pytest_anki.plugin.anki_session` docstring for all parameters.

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
| `loaded_addon(package)` | Context manager that cleans up `sys.modules` on exit |
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

Enum: `ANKI_MAIN` or `ANKI_REVIEWER` — selects which webview ChromeDriver attaches to.

### `AnkiSessionError`

Exception raised on session errors (e.g., timeout, profile load failures).

---

## CLI Options

| Flag | Effect |
|---|---|
| `--anki-no-fork` | Disable per-test forking (shares single Anki process) |

## pytest ini options

| Key | Type | Default | Description |
|---|---|---|---|
| `anki_force_fork` | `bool` | `true` | Fork each test into a subprocess |
