"""Unit tests for HookRegistry snapshot/restore hook isolation.

These tests mock the aqt.gui_hooks and anki.hooks modules so they
can run without a real Anki runtime.
"""

import types
from unittest.mock import patch

from pytest_anki._plugin.hooks import HookRegistry, restore, snapshot


def _make_fake_hook_modules():
    """Create fake aqt.gui_hooks and anki.hooks module trees."""

    class HookRegistry:
        def __init__(self, hooks=None):
            self._hooks = hooks or []

    gh = types.ModuleType("aqt.gui_hooks")
    gh.profile_did_open = HookRegistry([lambda: 1])  # ty: ignore[unresolved-attribute]
    gh.reviewer_did_show_question = HookRegistry(  # ty: ignore[unresolved-attribute]
        [lambda: 2, lambda: 3]
    )
    gh.card_will_show = HookRegistry([])  # ty: ignore[unresolved-attribute]
    # Non-hook attribute to make sure dir() filtering works
    gh.some_constant = 42  # ty: ignore[unresolved-attribute]

    aqt = types.ModuleType("aqt")
    aqt.gui_hooks = gh  # ty: ignore[unresolved-attribute]

    anki_hooks_mod = types.ModuleType("anki.hooks")
    anki_hooks_mod._hooks = {  # ty: ignore[unresolved-attribute]
        "test_hook": [lambda: True],
    }

    anki = types.ModuleType("anki")
    anki.hooks = anki_hooks_mod  # ty: ignore[unresolved-attribute]

    return {
        "aqt": aqt,
        "aqt.gui_hooks": gh,
        "anki": anki,
        "anki.hooks": anki_hooks_mod,
    }


def test_snapshot_captures_gui_hooks():
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        snap = snapshot()

    assert "gui_hooks.profile_did_open" in snap
    assert len(snap["gui_hooks.profile_did_open"]) == 1
    assert "gui_hooks.reviewer_did_show_question" in snap
    assert len(snap["gui_hooks.reviewer_did_show_question"]) == 2
    assert "gui_hooks.card_will_show" in snap
    assert len(snap["gui_hooks.card_will_show"]) == 0
    assert "anki_hooks._hooks" in snap
    assert "test_hook" in snap["anki_hooks._hooks"]


def test_snapshot_ignores_non_hook_attributes():
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        snap = snapshot()
    keys = [k for k in snap if "some_constant" in k]
    assert len(keys) == 0


def test_restore_reverts_gui_hooks():
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        snap = snapshot()

        gh = fake["aqt.gui_hooks"]
        gh.profile_did_open._hooks.append(lambda: 99)
        gh.reviewer_did_show_question._hooks.clear()

        restore(snap)

        assert len(gh.profile_did_open._hooks) == 1
        assert len(gh.reviewer_did_show_question._hooks) == 2


def test_restore_reverts_anki_hooks():
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        snap = snapshot()

        anki_hooks = fake["anki.hooks"]
        anki_hooks._hooks["new_hook"] = [lambda: False]
        del anki_hooks._hooks["test_hook"]

        restore(snap)

        assert "new_hook" not in anki_hooks._hooks
        assert "test_hook" in anki_hooks._hooks


def test_restore_handles_empty_snapshot():
    """Restoring an empty snapshot should not raise."""
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        restore({})


def test_double_restore_is_idempotent():
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        snap = snapshot()
        restore(snap)
        snap2 = snapshot()

    assert snap == snap2


def test_hook_registry_class_delegates():
    """HookRegistry class methods delegate to module-level functions."""
    fake = _make_fake_hook_modules()
    with patch.dict("sys.modules", fake):
        registry = HookRegistry()
        snap = registry.snapshot()
        assert "gui_hooks.profile_did_open" in snap

        gh = fake["aqt.gui_hooks"]
        gh.profile_did_open._hooks.append(lambda: 99)
        registry.restore(snap)
        assert len(gh.profile_did_open._hooks) == 1
