"""Verify that the public API surface exports what users expect."""

from pytest_anki import (
    AnkiSession,
    AnkiSessionError,
    AnkiStateUpdate,
    AnkiWebViewType,
    ConfigPaths,
    PathLike,
    UnpackedAddon,
)


def test_all_exports_are_accessible():
    assert AnkiSession is not None
    assert AnkiSessionError is not None
    assert AnkiStateUpdate is not None
    assert AnkiWebViewType is not None
    assert ConfigPaths is not None
    assert PathLike is not None
    assert UnpackedAddon is not None


def test_anki_session_type():
    assert isinstance(AnkiSession, type)


def test_anki_state_update_fields():
    update = AnkiStateUpdate(
        meta_storage={"key": "val"},
        profile_storage={"key": "val"},
        colconf_storage={"key": "val"},
    )
    assert update.meta_storage == {"key": "val"}
    assert update.profile_storage == {"key": "val"}
    assert update.colconf_storage == {"key": "val"}


def test_anki_state_update_defaults():
    update = AnkiStateUpdate()
    assert update.meta_storage is None
    assert update.profile_storage is None
    assert update.colconf_storage is None


def test_anki_web_view_type_values():
    assert AnkiWebViewType.main_webview.value == "main webview"
    assert AnkiWebViewType.previewer.value == "previewer"


def test_pathlike_is_union():
    """PathLike should be a typing construct compatible with str and Path."""
    from pathlib import Path

    def accepts_pathlike(p: PathLike) -> str:
        return str(p)

    assert accepts_pathlike("/tmp/foo") == "/tmp/foo"
    assert accepts_pathlike(Path("/tmp/bar")) == "/tmp/bar"


def test_unpacked_addon_structure():
    addon: UnpackedAddon = ("my_package", "/path/to/addon")
    name, path = addon
    assert name == "my_package"
    assert path == "/path/to/addon"


def test_config_paths_structure():
    from pathlib import Path

    paths = ConfigPaths(
        default_config=Path("/cfg/defaults.json"),
        user_config=Path("/cfg/meta.json"),
    )
    assert str(paths.default_config) == "/cfg/defaults.json"
    assert str(paths.user_config) == "/cfg/meta.json"


def test_config_paths_none_defaults():
    paths = ConfigPaths(default_config=None, user_config=None)
    assert paths.default_config is None
    assert paths.user_config is None
