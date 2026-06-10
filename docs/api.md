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

#### Fixture Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_path` | `str` | system tempdir | Directory for Anki base folder |
| `base_name` | `str` | `"anki_base"` | Base folder name |
| `profile_name` | `str` | `"User 1"` | User profile name |
| `lang` | `str` | `"en_US"` | Profile language |
| `load_profile` | `bool` | `False` | Pre-load profile/collection |
| `preset_anki_state` | `AnkiStateUpdate` | `None` | Pre-configure col/prof/meta storage |
| `packed_addons` | `List[Path]` | `None` | `.ankiaddon` packages to install |
| `unpacked_addons` | `List[Tuple[str, Path]]` | `None` | Source folders to install as add-ons |
| `addon_configs` | `List[Tuple[str, dict]]` | `None` | Config key/value pairs for add-ons |
| `enable_web_debugging` | `bool` | `False` | Enable remote devtools |
| `skip_loading_addons` | `bool` | `False` | Install but don't auto-load add-ons |

### `anki_session_module`

Module-scoped variant of `anki_session`. Starts Anki once per module and reuses the same session for all tests. Accepts the same parameters as `anki_session`.

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

#### Properties

| Property | Type | Description |
|---|---|---|
| `app` | `AnkiApp` | Anki's current QApplication instance |
| `mw` | `AnkiQt` | Anki's current main window instance |
| `user` | `str` | The current user profile name (e.g. `"User 1"`) |
| `base` | `str` | Path to Anki base directory |
| `qtbot` | `QtBot` | pytest-qt QtBot fixture |
| `collection` | `Collection` | Current Anki collection (after profile is loaded) |
| `chromium_version` | `str` | Chromium version string from QtWebEngine user agent |
| `web_debugging_port` | `Optional[int]` | Port used for remote web debugging (if enabled) |

#### Methods

| Method | Returns | Description |
|---|---|---|
| `load_profile()` | `Collection` | Load Anki user profile, returning the collection |
| `unload_profile(on_profile_unloaded=None)` | `None` | Unload current profile |
| `install_deck(path)` | `int` | Install deck from `.apkg` file, returning deck ID |
| `remove_deck(deck_id)` | `None` | Remove deck by ID |
| `load_addon(package_name)` | `ModuleType` | Dynamically import an add-on by package name |
| `create_addon_config(package_name, default_config=None, user_config=None)` | `ConfigPaths` | Create and populate add-on `config.json` / `meta.json` |
| `update_anki_state(anki_state_update)` | `None` | Pre-set `mw.col.conf`, `mw.pm.profile`, `mw.pm.meta` |
| `reset_state()` | `None` | Clear addon modules from `sys.modules` and reset hooks |
| `run_in_thread_and_wait(task, task_args=None, task_kwargs=None, timeout=5000)` | `Any` | Run a function in the Qt thread pool with timeout |
| `set_timeout(task, delay)` | `None` | Schedule a callback on the Qt event loop after `delay` ms |
| `run_with_chrome_driver(test_function, target_web_view=None, timeout=5000)` | `Optional[bool]` | Attach Selenium ChromeDriver to Anki webviews |
| `reset_chrome_driver()` | `None` | Quit and clear the current ChromeDriver instance |

#### Context Managers

| Context manager | Yields | Description |
|---|---|---|
| `profile_loaded()` | `Iterator[Collection]` | Load profile on enter, unload on exit |
| `deck_installed(path)` | `Iterator[int]` | Install deck on enter, remove on exit |
| `loaded_addon(package_name)` | `Iterator[ModuleType]` | Import add-on on enter, clean `sys.modules` and restore hooks on exit |
| `addon_config_created(package_name, default_config=None, user_config=None)` | `Iterator[ConfigPaths]` | Create config files on enter, delete on exit |

### `AnkiStateUpdate`

Dataclass for pre-configuring Anki object state:

- `colconf_storage: Optional[Dict]` — `mw.col.conf` updates
- `profile_storage: Optional[Dict]` — `mw.pm.profile` updates
- `meta_storage: Optional[Dict]` — `mw.pm.meta` updates (applied before add-on load)

### `AnkiWebViewType`

Enum identifying Anki web views for Selenium ChromeDriver:

- `main_webview`, `top_toolbar`, `bottom_toolbar`, `legacy_deck_stats`
- `previewer`, `browser_card_info`, `card_layout`, `change_notetype`
- `find_duplicates`, `empty_cards`

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
