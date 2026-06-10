"""Unit tests for AnkiSession surface-level properties and helpers.

These tests mock Qt/Anki dependencies and do not require a running Anki session.
"""

import types
from unittest.mock import Mock, patch

import pytest
from packaging.version import Version

from pytest_anki._plugin.errors import AnkiSessionError
from pytest_anki._plugin.session import AnkiSession

# -- chromium_version -------------------------------------------------------


def _make_session(**kwargs):
    defaults = dict(app=Mock(), mw=Mock(), user="test", base="/tmp", qtbot=Mock())
    return AnkiSession(**{**defaults, **kwargs})


def test_chromium_version_parses_user_agent():
    mock_profile = Mock()
    mock_profile.httpUserAgent.return_value = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) QtWebEngine/6.3.1 "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    with patch(
        "pytest_anki._plugin.session.QWebEngineProfile.defaultProfile",
        return_value=mock_profile,
    ):
        session = _make_session()
        assert session.chromium_version == "122.0.0.0"


def test_chromium_version_unparseable_raises():
    mock_profile = Mock()
    mock_profile.httpUserAgent.return_value = "Totally not a browser"
    with patch(
        "pytest_anki._plugin.session.QWebEngineProfile.defaultProfile",
        return_value=mock_profile,
    ):
        session = _make_session()
        with pytest.raises(
            AnkiSessionError, match="Could not determine Chromium version"
        ):
            _ = session.chromium_version


# -- reset_chrome_driver ----------------------------------------------------


def test_reset_chrome_driver_noop_when_no_driver():
    session = _make_session()
    assert session._chrome_driver is None
    session.reset_chrome_driver()
    assert session._chrome_driver is None


def test_reset_chrome_driver_quits_existing_driver():
    mock_driver = Mock()
    session = _make_session()
    session._chrome_driver = mock_driver
    session.reset_chrome_driver()
    mock_driver.quit.assert_called_once()
    assert session._chrome_driver is None


# -- get_anki_version -------------------------------------------------------


def test_get_anki_version_smoke():
    from pytest_anki._plugin.anki import get_anki_version

    v = get_anki_version()
    assert isinstance(v, Version)


def test_get_anki_version_main_path():
    """Primary import path: from anki.buildinfo import version."""
    buildinfo = types.ModuleType("anki.buildinfo")
    buildinfo.version = "25.9"
    main = types.ModuleType("anki")
    main.version = "from_buildinfo"

    with patch.dict("sys.modules", {"anki.buildinfo": buildinfo, "anki": main}):
        from pytest_anki._plugin.anki import get_anki_version

        v = get_anki_version()
        assert v == Version("25.9")


def test_get_anki_version_fallback_when_buildinfo_missing():
    """Fallback path: from anki import version."""
    main = types.ModuleType("anki")
    main.version = "23.12"

    with patch.dict("sys.modules", {"anki.buildinfo": None, "anki": main}):
        from pytest_anki._plugin.anki import get_anki_version

        v = get_anki_version()
        assert v == Version("23.12")
