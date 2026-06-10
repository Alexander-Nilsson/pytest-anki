"""Tests for plugin configuration: QT_API env var and forking options."""

import pytest

from pytest_anki._plugin.compat import _resolve_qt_api_from_env

# -- QT_API env var -------------------------------------------------------


def test_resolve_qt_api_pyqt5(monkeypatch):
    monkeypatch.setenv("QT_API", "pyqt5")
    assert _resolve_qt_api_from_env() == "PyQt5"


def test_resolve_qt_api_qt5(monkeypatch):
    monkeypatch.setenv("QT_API", "qt5")
    assert _resolve_qt_api_from_env() == "PyQt5"


def test_resolve_qt_api_pyqt6(monkeypatch):
    monkeypatch.setenv("QT_API", "pyqt6")
    assert _resolve_qt_api_from_env() == "PyQt6"


def test_resolve_qt_api_qt6(monkeypatch):
    monkeypatch.setenv("QT_API", "qt6")
    assert _resolve_qt_api_from_env() == "PyQt6"


def test_resolve_qt_api_unset(monkeypatch):
    monkeypatch.delenv("QT_API", raising=False)
    assert _resolve_qt_api_from_env() is None


def test_resolve_qt_api_invalid(monkeypatch):
    monkeypatch.setenv("QT_API", "invalid")
    assert _resolve_qt_api_from_env() is None


def test_resolve_qt_api_empty(monkeypatch):
    monkeypatch.setenv("QT_API", "")
    assert _resolve_qt_api_from_env() is None


# -- Forking options ------------------------------------------------------


def test_pytest_addoption_registers_anki_no_fork():
    parser = pytest.Parser()
    from pytest_anki.plugin import pytest_addoption

    pytest_addoption(parser)
    args = parser.parse_known_args(["--anki-no-fork"])
    assert args.anki_no_fork is True


def test_pytest_addoption_registers_anki_force_fork_ini():
    parser = pytest.Parser()
    from pytest_anki.plugin import pytest_addoption

    pytest_addoption(parser)
    assert "anki_force_fork" in parser._ininames


# -- @pytest.mark.anki_session marker -------------------------------------


def _make_mock_metafunc(fixturenames, marker_name=None, marker_kwargs=None):
    """Build a minimal object that satisfies Metafunc's interface as used
    by ``pytest_generate_tests``."""
    import types

    marker_kwargs = marker_kwargs or {}

    class MockMarker:
        args = ()
        kwargs = marker_kwargs

    class MockDefinition:
        def get_closest_marker(self, name):
            return MockMarker() if name == marker_name else None

        def iter_markers(self, name):
            return []

    metafunc = types.SimpleNamespace(
        fixturenames=fixturenames,
        definition=MockDefinition(),
        _parametrize_calls=[],
    )
    metafunc.parametrize = lambda argnames, argvalues, **kwargs: (
        metafunc._parametrize_calls.append((argnames, argvalues, kwargs))
    )
    return metafunc


def test_pytest_configure_registers_anki_session_marker():
    """pytest_configure should not raise when registering markers."""
    config = pytest.Config.fromdictargs([], {})
    from pytest_anki.plugin import pytest_configure

    pytest_configure(config)  # smoke test: no exception


def test_pytest_generate_tests_marker_to_parametrize():
    metafunc = _make_mock_metafunc(
        fixturenames=["anki_session"],
        marker_name="anki_session",
        marker_kwargs={"load_profile": True, "lang": "de_DE"},
    )
    from pytest_anki.plugin import pytest_generate_tests

    pytest_generate_tests(metafunc)

    assert len(metafunc._parametrize_calls) == 1
    argnames, argvalues, kwargs = metafunc._parametrize_calls[0]
    assert argnames == "anki_session"
    assert argvalues == [{"load_profile": True, "lang": "de_DE"}]
    assert kwargs.get("indirect") is True


def test_pytest_generate_tests_no_marker_no_parametrize():
    metafunc = _make_mock_metafunc(
        fixturenames=["anki_session"],
        marker_name=None,
    )
    from pytest_anki.plugin import pytest_generate_tests

    pytest_generate_tests(metafunc)

    assert len(metafunc._parametrize_calls) == 0


def test_pytest_generate_tests_ignores_non_anki_session_fixture():
    metafunc = _make_mock_metafunc(
        fixturenames=["other_fixture"],
        marker_name="anki_session",
        marker_kwargs={"foo": "bar"},
    )
    from pytest_anki.plugin import pytest_generate_tests

    pytest_generate_tests(metafunc)

    assert len(metafunc._parametrize_calls) == 0


def test_pytest_generate_tests_does_not_override_existing_parametrize():
    metafunc = _make_mock_metafunc(
        fixturenames=["anki_session"],
        marker_name="anki_session",
        marker_kwargs={"load_profile": True},
    )

    class ExistingMarker:
        args = ("anki_session",)
        kwargs = {}

    class ExistingDef:
        def get_closest_marker(self, name):
            return None if name == "anki_session" else None

        def iter_markers(self, name):
            return [ExistingMarker()]

    metafunc.definition = ExistingDef()

    from pytest_anki.plugin import pytest_generate_tests

    pytest_generate_tests(metafunc)

    assert len(metafunc._parametrize_calls) == 0
