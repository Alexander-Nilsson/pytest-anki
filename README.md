# pytest-anki

pytest-anki is a [pytest](https://docs.pytest.org/) plugin that allows developers to write tests for their [Anki add-ons](https://addon-docs.ankiweb.net/).

At its core lies the `anki_session` fixture that provides add-on authors with the ability to create and control headless Anki sessions to test their add-ons in:

```python
from pytest_anki import AnkiSession

def test_addon_registers_deck(anki_session: AnkiSession):
    my_addon = anki_session.load_addon("my_addon")
    with anki_session.load_profile()
        with anki_session.deck_installed(deck_path) as deck_id:
            assert deck_id in my_addon.deck_ids

```

`anki_session` comes with a comprehensive API that allows developers to programmatically manipulate Anki, set up and reproduce specific configurations, simulate user interactions, and much more.

The goal is to provide add-on authors with a one-stop-shop for their functional testing needs, while also enabling them to QA their add-ons against a battery of different Anki versions, catching incompatibilities as they arise.

[![CI](https://github.com/Alexander-Nilsson/pytest-anki/actions/workflows/general.yml/badge.svg)](https://github.com/Alexander-Nilsson/pytest-anki/actions/workflows/general.yml)

## Quickstart

Install pytest-anki with your Qt backend and Anki version:

```bash
pip install pytest-anki2[qt6,anki-2509]
```

Add a minimal test file:

```python
# test_my_addon.py
from pytest_anki import AnkiSession


def test_addon_loads(anki_session: AnkiSession):
    anki_session.load_addon("my_addon")
    assert hasattr(anki_session.mw, "my_addon")


def test_with_profile(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        assert anki_session.collection is not None
```

Run with pytest:

```bash
pytest test_my_addon.py
```

If you use `pyproject.toml`, add the plugin config:

```toml
[tool.pytest.ini_options]
qt_api = "pyqt6"
```

See the [Usage](#usage) section below for the full API reference.

## Platform Support

`pytest-anki` is tested on **Linux (Ubuntu 24.04)** and **macOS** in CI. Linux runs the full matrix of Qt5/Qt6 and Anki versions; macOS runs a single latest-config entry.

The full test suite requires a Qt6 WebEngine ABI compatible with Ubuntu 24.04 (as used in CI). On other Linux distributions, use system Qt packages (`qt6-system` extra) and rely on CI for test validation. On macOS, PyPI Qt6 wheels work natively.


## Installation

### Requirements

- Python 3.9+ (3.13 and 3.14 supported in CI)
- Anki 2.1.54+ (installed automatically)
- Qt5 or Qt6 (auto-detected at runtime; see below)

### Choose your Qt backend

`pytest-anki` supports both **PyQt5** and **PyQt6**, auto-detected at import time. Choose the approach that matches your system.

---

#### Option A: Ubuntu / Debian (PyPI wheels, recommended)

PyPI wheels for `PyQt6`, `PyQt6-WebEngine`, and their bundled Qt6 runtimes are built against Ubuntu's ABI and work out of the box:

```bash
pip install pytest-anki2[qt6-pypi]
```

With uv:

```bash
uv add --dev pytest-anki2[qt6-pypi]
```

Install optional selenium support for web debugging:

```bash
pip install pytest-anki2[qt6-pypi,selenium]
```

---

#### Option B: Arch Linux (system packages)

Use your distro's pre-compiled PyQt6 packages — they link against your system's Qt6 libraries and avoid ABI incompatibilities:

```bash
sudo pacman -S python-pyqt6-webengine
pip install pytest-anki2[qt6-system]
```

With uv:

```bash
sudo pacman -S python-pyqt6-webengine
uv add --dev pytest-anki2[qt6-system]
```

---

#### Option C: Fedora (system packages)

```bash
sudo dnf install python3-pyqt6-webengine
pip install pytest-anki2[qt6-system]
```

With uv:

```bash
sudo dnf install python3-pyqt6-webengine
uv add --dev pytest-anki2[qt6-system]
```

---

#### Option D: Any Linux with system Qt5 (fallback)

If your system provides Qt5 + PyQt5:

```bash
pip install pytest-anki2[qt5]
```

---

### What's the difference between the Qt6 extras?

| Extra | Installs | Best for |
|---|---|---|
| `qt6` | `PyQt6` + `PyQt6-WebEngine` (bindings only) | Default — use if unsure |
| `qt6-system` | Same as `qt6` (alias) | Systems with Qt6 + WebEngine installed via native packages |
| `qt6-pypi` | + `PyQt6-Qt6` + `PyQt6-WebEngine-Qt6` (bundled runtimes) | Ubuntu / Debian where PyPI wheels work natively |

### Optional extras

| Extra | What it gives you |
|---|---|
| `selenium` / `web` | Web debugging via ChromeDriver |
| `recommended-plugins` | `pytest-xvfb`, `pytest-xdist` (with native forking) |

### Qt binding selection

`pytest-anki` auto-detects your installed Qt bindings at import time (PyQt6 preferred over PyQt5). To override, set the `QT_API` environment variable:

| `QT_API` value | Binding selected |
|---|---|
| `pyqt6` or `qt6` | PyQt6 |
| `pyqt5` or `qt5` | PyQt5 |

```bash
QT_API=pyqt5 pytest tests/
```

This is useful when both PyQt5 and PyQt6 are installed, or when you want to test against a specific binding in CI.


## Usage

### Basic Use

The plugin registers a single `anki_session` fixture that launches a headless Anki instance:

```python
from pytest_anki import AnkiSession

def test_my_addon(anki_session: AnkiSession):
    # Anki is running — interact with anki_session.mw, .app, etc.
    pass
```

The `anki_session` fixture yields an `AnkiSession` with these key attributes:

| Attribute | Type | Description |
|---|---|---|
| `mw` | `AnkiQt` | Anki's main window |
| `app` | `AnkiApp` | QApplication instance |
| `collection` | `Collection` | Anki collection (after profile is loaded) |
| `user` | `str` | Profile name (default: `"User 1"`) |
| `base` | `str` | Path to Anki's base directory |
| `qtbot` | `QtBot` | pytest-qt fixture for Qt signal testing |

**Profiles & collection:**

```python
def test_profile_loading(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        assert anki_session.collection
        # mw.col.conf, mw.pm.profile, etc. are available
```

**Deck management:**

```python
def test_deck_install(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        with anki_session.deck_installed("path/to/deck.apkg") as deck_id:
            assert deck_id in [d.id for d in anki_session.collection.decks.all_names_and_ids()]
```

**Loading add-ons:**

```python
def test_load_addon(anki_session: AnkiSession):
    anki_session.load_addon("my_addon_package")
    assert hasattr(anki_session.mw, "my_addon_package")
```

**Add-on config:**

```python
def test_addon_config(anki_session: AnkiSession):
    with anki_session.addon_config_created(
        package_name="my_addon",
        default_config={"key": "default"},
        user_config={"key": "overridden"},
    ) as paths:
        pass  # config written to addons21/my_addon/config.json and meta.json
```

**Pre-setting Anki state:**

```python
from pytest_anki import AnkiStateUpdate

def test_preset_state(anki_session: AnkiSession):
    anki_session.update_anki_state(AnkiStateUpdate(
        colconf_storage={"my_key": True},
        profile_storage={"my_key": True},
    ))
```

**Running tasks in the Qt event loop:**

```python
def test_threaded_task(anki_session: AnkiSession):
    result = anki_session.run_in_thread_and_wait(
        lambda: 42, timeout=5000
    )
    assert result == 42
```

### Configuring the Anki Session

Customize the session using the dedicated marker (recommended):

```python
import pytest

@pytest.mark.anki_session(
    load_profile=True,
    profile_name="CustomUser",
    lang="de_DE",
    packed_addons=["path/to/addon.ankiaddon"],
    unpacked_addons=[("my_addon", "path/to/addon/source")],
    addon_configs=[("my_addon", {"key": "value"})],
    preset_anki_state=AnkiStateUpdate(meta_storage={"key": True}),
    enable_web_debugging=False,
    skip_loading_addons=False,
)
def test_configured_session(anki_session: AnkiSession):
    assert anki_session.mw.pm.name == "CustomUser"
```

The equivalent via indirect parametrization also works:

```python
@pytest.mark.parametrize("anki_session", [dict(load_profile=True)], indirect=True)
def test_via_parametrize(anki_session: AnkiSession):
    ...
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_path` | `str` | system tempdir | Directory for Anki base folder |
| `profile_name` | `str` | `"User 1"` | User profile name |
| `lang` | `str` | `"en_US"` | Profile language |
| `load_profile` | `bool` | `False` | Pre-load profile/collection |
| `preset_anki_state` | `AnkiStateUpdate` | `None` | Pre-configure col/prof/meta storage |
| `packed_addons` | `List[Path]` | `None` | `.ankiaddon` packages to install |
| `unpacked_addons` | `List[Tuple[str, Path]]` | `None` | Source folders to install as add-ons |
| `addon_configs` | `List[Tuple[str, dict]]` | `None` | Config key/value pairs for add-ons |
| `enable_web_debugging` | `bool` | `False` | Enable remote devtools |
| `skip_loading_addons` | `bool` | `False` | Install but don't auto-load add-ons |

### Module-scoped session

For suites with many tests that don't mutate global state, use the module-scoped variant:

```python
def test_first(anki_session_module: AnkiSession):
    assert anki_session_module.mw is not None

def test_second(anki_session_module: AnkiSession):
    # Shares the same Anki process as test_first
    pass
```

`anki_session_module` accepts the same parameters as `anki_session`. Use `reset_state()` between tests to clear addon modules:

```python
def test_isolated(anki_session_module: AnkiSession):
    anki_session_module.load_addon("my_addon")
    anki_session_module.reset_state()  # clears sys.modules
```

When using module-scoped sessions, disable auto-forking with `--anki-no-fork` or `anki_force_fork = false` to share a single process.

### Isolated addon loading

The `loaded_addon` context manager restores hook registries on exit, preventing state leakage between tests when running without forks:

```python
def test_isolated_addon(anki_session: AnkiSession):
    with anki_session.loaded_addon("my_addon") as mod:
        assert mod.some_function()
    # Hook registries are restored to pre-import state
```

### Web debugging

When `enable_web_debugging=True`, you can drive Anki's web views via Selenium:

```python
from pytest_anki import AnkiWebViewType

def test_web_view(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        anki_session.run_with_chrome_driver(
            lambda driver: driver.find_element("tag name", "body"),
            target_web_view=AnkiWebViewType.main_webview,
        )
```

## Migration Guide (v1 → v2)

v2.0.0 is a major rewrite. Here's what changed:

### Breaking changes

| v1 | v2 |
|---|---|
| `pytest-anki2[qt5]` / `pytest-anki2[qt6]` | `pytest-anki2[qt5]` / `pytest-anki2[qt6]` / `pytest-anki2[qt6-system]` / `pytest-anki2[qt6-pypi]` |
| Poetry-based build | uv + hatchling |
| Python 3.7+ | Python 3.9+ |
| `pytest-forked` | xdist native forking (`pytest-xdist>=3.0`) |
| Manual forking required | Auto-forked by default (opt-out via `--anki-no-fork`) |
| PyQt5 only | PyQt6 auto-detected, PyQt5 fallback |
| Selenium always installed | Selenium optional (`[selenium]` extra) |

### What to update

1. **Switch to uv** (or keep pip — `pip install pytest-anki2[...]` still works).
2. **Specify an Anki version extra**: `pip install pytest-anki2[anki-2509,qt6]`.
3. **Remove `pytest-forked`** from your dependencies — xdist handles forking.
4. **If you used `@pytest.mark.forked` explicitly**, it's now automatic; use `--anki-no-fork` to disable.
5. **If you relied on `pytest-anki` pulling in selenium**, add `selenium` extra explicitly.

### What stayed the same

- The `anki_session` fixture API is backward-compatible.
- `AnkiSession`, `AnkiStateUpdate`, `AnkiWebViewType` are at `pytest_anki`.
- Indirect parametrization via `@pytest.mark.parametrize("anki_session", [...], indirect=True)` works as before.

## Additional Notes

### When to use pytest-anki

Running your test in an Anki environment is expensive and introduces an additional layer of confounding factors. If you can `mock` your Anki runtime dependencies away, then that should always be your first tool of choice.

Where `anki_session` comes in handy is further towards the upper levels of the test pyramid, i.e. functional tests, end-to-end tests, and UI tests. Additionally the plugin can provide you with a convenient way to automate testing for incompatibilities with Anki and other add-ons.

### The importance of forking your tests

Since v2.0.0, all tests using this plugin are automatically marked as `forked` (via `pytest_collection_modifyitems`). This is because, while the plugin does attempt to tear down Anki sessions as cleanly as possible on exit, this process is never quite perfect, especially for add-ons that monkey-patch Anki.

With unforked test runs, factors like that can lead to unexpected behavior, or worse still, your tests crashing. Forking a new subprocess for each test bypasses these limitations.

When running without forks, the `loaded_addon()` context manager now also snapshots and restores `aqt.gui_hooks` and `anki.hooks` registries, preventing addon hook registrations from leaking between tests.

To opt out of automatic forking, set `anki_force_fork = false` in your `pyproject.toml`:

```toml
[tool.pytest.ini_options]
anki_force_fork = false
```

Or pass `--anki-no-fork` on the command line:

```bash
pytest --anki-no-fork tests/
```

Disabling forking can speed up test suites that share a single Anki process, but may cause instability if add-ons mutate global state.

### Automated Testing

`pytest-anki` is designed to work well with continuous integration systems such as GitHub actions. For an example see `pytest-anki`'s own [GitHub workflows](./.github/workflows/).


### Troubleshooting

#### Qt6 ABI incompatibility

PyPI wheels for `PyQt6-WebEngine` ship Qt6 libraries compiled against Ubuntu's ABI. On Arch, Fedora, or other non-Ubuntu distros:

```bash
# Use system Qt packages
sudo pacman -S python-pyqt6-webengine   # Arch
sudo dnf install python3-pyqt6-webengine # Fedora
pip install pytest-anki2[qt6-system]
```

If you cannot run the full suite locally, CI (GitHub Actions) is the authoritative validation. You can always run lint and type checks:

```bash
make lint
make check
```

#### pytest hangs when using xvfb

Blocking non-dismissable prompts from your add-on code can cause hangs. Bypass xvfb temporarily:

```bash
pytest --no-xvfb tests/
```

#### ImportError: No Qt bindings found

Install a Qt backend:

```bash
pip install pytest-anki2[qt6]
# or for PyQt5:
pip install pytest-anki2[qt5]
```

If you have Qt installed but the wrong one is selected, set `QT_API`:

```bash
QT_API=pyqt5 pytest tests/
```

#### Tests fail with "Failed to import add-on"

Ensure your add-on is in Anki's `addons21` directory, or use `unpacked_addons` to point to a source folder during session setup:

```python
@pytest.mark.parametrize("anki_session", [dict(
    unpacked_addons=[("my_addon", "/path/to/source")],
)], indirect=True)
def test_with_addon(anki_session: AnkiSession):
    anki_session.load_addon("my_addon")
```

## Contributing

Contributions are welcome! To set up `pytest-anki` for development, please first make sure you have Python 3.9+ and [uv](https://docs.astral.sh/uv/) installed, then run the following steps:

```
$ git clone https://github.com/Alexander-Nilsson/pytest-anki.git

$ cd pytest-anki

$ make install
```

Before submitting any changes, please make sure that `pytest-anki`'s checks and tests pass:

```bash
make lint
make check
make test      # requires Ubuntu-compatible Qt6 ABI; CI runs the full matrix
# or use Docker to match the CI environment:
make test-docker
# or run just the unit tests (no Qt6 ABI needed):
make test-light
```

This project uses `ruff` to enforce a consistent code style. To auto-format your code you can use:

```bash
make format
```

## License and Credits

*pytest-anki* is

*Copyright © 2026 Alexander Nilsson*

*Copyright © 2019-2025 Aristotelis P. (Glutanimate) and [contributors](./CONTRIBUTORS)*

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing)*

*Copyright © 2017-2021 [Ankitects Pty Ltd and contributors](https://github.com/ankitects/)*


All credits for the original idea for creating a context manager to test Anki add-ons with go to Michal. _pytest-anki_ would not exist without his [anki_testing](https://github.com/krassowski/anki_testing) project.

I would also like to extend a heartfelt thanks to [AMBOSS](https://github.com/amboss-mededu/) for their major part in supporting the development of this plugin! Most of the recent feature additions leading up to v1.0.0 of the plugin were implemented as part of my work on the [AMBOSS add-on](https://www.amboss.com/us/anki-amboss).

_pytest-anki_ is free and open-source software. Its source-code is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [license file](./LICENSE) that accompanies this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Please see the license file for more details.
