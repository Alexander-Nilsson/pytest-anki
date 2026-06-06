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

## Platform Support

`pytest-anki` has only been confirmed to work on Linux so far. The full test suite requires a Qt6 WebEngine ABI compatible with Ubuntu 24.04 (as used in CI). On other distributions, use system Qt packages and rely on CI for test validation.


## Installation

### Requirements

- Python 3.9+ (3.13 supported)
- Anki 2.1.54+ (installed automatically)
- Qt5 or Qt6 (auto-detected at runtime; see below)

### Choose your Qt backend

`pytest-anki` supports both **PyQt5** and **PyQt6**, auto-detected at import time. Choose the approach that matches your system.

---

#### Option A: Ubuntu / Debian (PyPI wheels, recommended)

PyPI wheels for `PyQt6`, `PyQt6-WebEngine`, and their bundled Qt6 runtimes are built against Ubuntu's ABI and work out of the box:

```bash
pip install pytest-anki[qt6-pypi]
```

With uv:

```bash
uv add --dev pytest-anki[qt6-pypi]
```

Install optional selenium support for web debugging:

```bash
pip install pytest-anki[qt6-pypi,selenium]
```

---

#### Option B: Arch Linux (system packages)

Use your distro's pre-compiled PyQt6 packages — they link against your system's Qt6 libraries and avoid ABI incompatibilities:

```bash
sudo pacman -S python-pyqt6-webengine
pip install pytest-anki[qt6-system]
```

With uv:

```bash
sudo pacman -S python-pyqt6-webengine
uv add --dev pytest-anki[qt6-system]
```

---

#### Option C: Fedora (system packages)

```bash
sudo dnf install python3-pyqt6-webengine
pip install pytest-anki[qt6-system]
```

With uv:

```bash
sudo dnf install python3-pyqt6-webengine
uv add --dev pytest-anki[qt6-system]
```

---

#### Option D: Any Linux with system Qt5 (fallback)

If your system provides Qt5 + PyQt5:

```bash
pip install pytest-anki[qt5]
```

---

### What's the difference between `qt6-system` and `qt6-pypi`?

| Extra | Installs | Best for |
|---|---|---|
| `qt6-system` | `PyQt6` + `PyQt6-WebEngine` (bindings only) | Systems with Qt6 + WebEngine installed via native packages |
| `qt6-pypi` | `PyQt6` + `PyQt6-WebEngine` + `PyQt6-Qt6` + `PyQt6-WebEngine-Qt6` (bundled runtimes) | Ubuntu / Debian where PyPI wheels work natively |

### Optional extras

| Extra | What it gives you |
|---|---|
| `selenium` / `web` | Web debugging via ChromeDriver |
| `recommended-plugins` | `pytest-xvfb`, `pytest-xdist` (with native forking) |


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

Customize the session via indirect parametrization:

```python
import pytest

@pytest.mark.parametrize("anki_session", [dict(
    load_profile=True,
    profile_name="CustomUser",
    lang="de_DE",
    packed_addons=["path/to/addon.ankiaddon"],
    unpacked_addons=[("my_addon", "path/to/addon/source")],
    addon_configs=[("my_addon", {"key": "value"})],
    preset_anki_state=AnkiStateUpdate(meta_storage={"key": True}),
    enable_web_debugging=False,
    skip_loading_addons=False,
)], indirect=True)
def test_configured_session(anki_session: AnkiSession):
    assert anki_session.mw.pm.name == "CustomUser"
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

## Additional Notes

### When to use pytest-anki

Running your test in an Anki environment is expensive and introduces an additional layer of confounding factors. If you can `mock` your Anki runtime dependencies away, then that should always be your first tool of choice.

Where `anki_session` comes in handy is further towards the upper levels of the test pyramid, i.e. functional tests, end-to-end tests, and UI tests. Additionally the plugin can provide you with a convenient way to automate testing for incompatibilities with Anki and other add-ons.

### The importance of forking your tests

Since v2.0.0, all tests using this plugin are automatically marked as `forked` (via `pytest_collection_modifyitems`). This is because, while the plugin does attempt to tear down Anki sessions as cleanly as possible on exit, this process is never quite perfect, especially for add-ons that monkey-patch Anki.

With unforked test runs, factors like that can lead to unexpected behavior, or worse still, your tests crashing. Forking a new subprocess for each test bypasses these limitations.

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

#### Local testing limitations (Qt6 ABI)

`pytest-anki`'s full test suite requires launching a real Anki process with Qt/WebEngine. PyPI wheels for `PyQt6-WebEngine` ship Qt6 libraries compiled against Ubuntu's ABI, which cannot run on distros like Arch Linux or Fedora. On those systems, use system packages:

```bash
# Arch
sudo pacman -S python-pyqt6-webengine
# Fedora
sudo dnf install python3-pyqt6-webengine
```

If you cannot run the full suite locally, CI (GitHub Actions) is the authoritative validation — it runs the full matrix on Ubuntu 24.04. You can also run lint and type checks locally without Qt:

```bash
make lint
make check
```

#### pytest hanging when using xvfb

Especially if you run your tests headlessly with `xvfb`, you might run into cases where pytest will sometimes appear to hang. Oftentimes this is due to blocking non-dismissable prompts that your add-on code might invoke in some scenarios. If you suspect that might be the case, my advice would be to temporarily bypass `xvfb` locally via `pytest --no-xvfb` to show the UI and manually debug the issue.

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
```

This project uses `ruff` to enforce a consistent code style. To auto-format your code you can use:

```bash
make format
```

## License and Credits

*pytest-anki* is

*Copyright © 2019-2025 Aristotelis P. (Glutanimate) and [contributors](./CONTRIBUTORS)*

*Copyright © 2017-2019 [Michal Krassowski](https://github.com/krassowski/anki_testing)*

*Copyright © 2017-2021 [Ankitects Pty Ltd and contributors](https://github.com/ankitects/)*


All credits for the original idea for creating a context manager to test Anki add-ons with go to Michal. _pytest-anki_ would not exist without his [anki_testing](https://github.com/krassowski/anki_testing) project.

I would also like to extend a heartfelt thanks to [AMBOSS](https://github.com/amboss-mededu/) for their major part in supporting the development of this plugin! Most of the recent feature additions leading up to v1.0.0 of the plugin were implemented as part of my work on the [AMBOSS add-on](https://www.amboss.com/us/anki-amboss).

_pytest-anki_ is free and open-source software. Its source-code is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [license file](./LICENSE) that accompanies this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. Please see the license file for more details.