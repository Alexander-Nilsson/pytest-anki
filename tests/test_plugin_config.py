"""Tests for plugin configuration: QT_API env var and forking options."""

from _pytest.config.argparsing import Parser

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
    parser = Parser()
    from pytest_anki.plugin import pytest_addoption

    pytest_addoption(parser)
    args = parser.parse_known_args(["--anki-no-fork"])
    assert args.anki_no_fork is True


def test_pytest_addoption_registers_anki_force_fork_ini():
    parser = Parser()
    from pytest_anki.plugin import pytest_addoption

    pytest_addoption(parser)
    assert "anki_force_fork" in parser._ininames
