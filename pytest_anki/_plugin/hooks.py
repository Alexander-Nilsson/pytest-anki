"""Hook registry snapshot/restore for test isolation.

Encapsulates the introspection-based approach to capturing and
restoring Anki's hook registries. The public interface is two
methods — ``snapshot`` and ``restore`` — so callers don't need
to know about ``dir()``, ``_hooks`` attributes, or ``deepcopy``.
"""

import copy
from typing import Any, Dict

_HookSnapshot = Dict[str, Any]


def snapshot() -> _HookSnapshot:
    """Capture all Anki/aqt hook registries into a snapshot dict.

    Uses introspection (``dir()`` + ``_hooks`` attribute probing)
    to find every hook registry on ``aqt.gui_hooks``.
    """
    import aqt.gui_hooks as gh
    from anki import hooks as anki_hooks

    snap: _HookSnapshot = {}

    for attr_name in dir(gh):
        attr = getattr(gh, attr_name)
        hooks: Any = getattr(attr, "_hooks", None)
        if hooks is not None:
            snap[f"gui_hooks.{attr_name}"] = list(hooks)

    snap["anki_hooks._hooks"] = copy.deepcopy(anki_hooks._hooks)

    return snap


def restore(snap: _HookSnapshot) -> None:
    """Restore Anki/aqt hook registries from a snapshot.

    Only restores keys present in the snapshot — hook registries
    added after the snapshot was taken are left alone.
    """
    import aqt.gui_hooks as gh
    from anki import hooks as anki_hooks

    for attr_name in dir(gh):
        attr = getattr(gh, attr_name)
        hooks: Any = getattr(attr, "_hooks", None)
        if hooks is not None:
            key = f"gui_hooks.{attr_name}"
            if key in snap:
                attr._hooks = snap[key]

    anki_hooks._hooks = copy.deepcopy(snap.get("anki_hooks._hooks", {}))


class HookRegistry:
    """Snapshot and restore Anki hook registries at a seam.

    One adapter (introspective) exists today. An ``ExplicitHookRegistry``
    would be the second once Anki formalises its hook API.

    Usage::

        registry = HookRegistry()
        snap = registry.snapshot()
        # ... mutate hooks ...
        registry.restore(snap)
    """

    snapshot = staticmethod(snapshot)
    restore = staticmethod(restore)
