"""Verifies the anki_session_module fixture is registered and module-scoped."""

from pytest_anki.plugin import anki_session_module


def test_fixture_is_callable():
    assert callable(anki_session_module)


def test_fixture_has_module_scope():
    assert anki_session_module._fixture_function_marker.scope == "module"
