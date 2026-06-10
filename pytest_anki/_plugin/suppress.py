"""Suppress noisy Anki-internal output during test sessions.

Anki's webview and toolbar emit diagnostic print statements when they
receive events after teardown (``ignored late bridge cmd``, ``ignored
late js callback``) or when JS functions haven't loaded yet
(``updateSyncColor is not defined``).  These are harmless in tests but
pollute test output.

This module monkey-patches the offending methods so they silently
return instead of printing.  Patches are applied by ``patch_anki``
and restored on context-manager exit — production code is never
affected.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _suppress_webview_prints(webview_cls: type) -> dict[str, Any]:
    """Patch ``AnkiWebView`` to swallow late-event print statements.

    Replaces ``_onBridgeCmd`` and ``_evalWithCallback`` so that
    ``_shouldIgnoreWebEvent()`` still gates execution (preserving
    Anki's event-ignoring logic) but the noisy ``print()`` calls are
    removed.

    Returns a dict of original methods keyed by attribute name.
    """
    originals: dict[str, Any] = {}
    originals["_onBridgeCmd"] = webview_cls._onBridgeCmd  # ty: ignore[unresolved-attribute]
    originals["_evalWithCallback"] = webview_cls._evalWithCallback  # ty: ignore[unresolved-attribute]

    _real_onBridgeCmd = originals["_onBridgeCmd"]
    _real_evalWithCallback = originals["_evalWithCallback"]

    def _silent_onBridgeCmd(self: Any, cmd: str) -> Any:
        if self._shouldIgnoreWebEvent():
            return
        return _real_onBridgeCmd(self, cmd)

    def _silent_evalWithCallback(self: Any, js: str, cb: Any = None) -> None:
        if cb is None:
            _real_evalWithCallback(self, js, None)
            return

        from aqt.qt import sip

        def _handler(val: Any) -> None:
            if sip.isdeleted(self) or self._shouldIgnoreWebEvent():
                return
            cb(val)

        page = self.page()
        if page is not None:
            page.runJavaScript(js, _handler)

    webview_cls._onBridgeCmd = _silent_onBridgeCmd  # ty: ignore[unresolved-attribute]
    webview_cls._evalWithCallback = _silent_evalWithCallback  # ty: ignore[unresolved-attribute]

    return originals


def _restore_webview_prints(webview_cls: type, originals: dict[str, Any]) -> None:
    """Restore original ``AnkiWebView`` methods."""
    webview_cls._onBridgeCmd = originals["_onBridgeCmd"]  # ty: ignore[unresolved-attribute]
    webview_cls._evalWithCallback = originals["_evalWithCallback"]  # ty: ignore[unresolved-attribute]


def _suppress_toolbar_sync_status(toolbar_cls: type) -> dict[str, Any]:
    """Replace ``Toolbar.set_sync_status`` with a no-op.

    In headless test mode ``toolbar.js`` (which defines
    ``updateSyncColor``) may not have loaded when
    ``set_sync_status`` evaluates the JS call, causing a console
    error.  The sync-status UI element is irrelevant in tests.

    Returns a dict containing the original method keyed by attribute name.
    """
    originals: dict[str, Any] = {}
    originals["set_sync_status"] = toolbar_cls.set_sync_status  # ty: ignore[unresolved-attribute]

    def _noop_set_sync_status(self: Any, status: Any) -> None:
        pass

    toolbar_cls.set_sync_status = _noop_set_sync_status  # ty: ignore[unresolved-attribute]
    return originals


def _restore_toolbar_sync_status(toolbar_cls: type, originals: dict[str, Any]) -> None:
    """Restore original ``Toolbar.set_sync_status``."""
    toolbar_cls.set_sync_status = originals["set_sync_status"]  # ty: ignore[unresolved-attribute]


class AnkiNoiseSuppressor:
    """Applies and reverses Anki noise-suppression patches.

    Patches three Anki internals:

    1. ``AnkiWebView._onBridgeCmd`` — silences ``ignored late bridge cmd``
    2. ``AnkiWebView._evalWithCallback`` — silences ``ignored late js callback``
    3. ``Toolbar.set_sync_status`` — prevents ``updateSyncColor`` JS errors

    All patches are reversed on ``restore()``.
    """

    def __init__(self) -> None:
        self._originals: dict[str, dict[str, Any]] = {}

    def apply(self) -> None:
        from aqt.toolbar import Toolbar
        from aqt.webview import AnkiWebView

        self._originals["webview"] = _suppress_webview_prints(AnkiWebView)
        self._originals["toolbar"] = _suppress_toolbar_sync_status(Toolbar)
        logger.debug("Applied Anki noise suppression patches")

    def restore(self) -> None:
        from aqt.toolbar import Toolbar
        from aqt.webview import AnkiWebView

        if "webview" in self._originals:
            _restore_webview_prints(AnkiWebView, self._originals["webview"])
        if "toolbar" in self._originals:
            _restore_toolbar_sync_status(Toolbar, self._originals["toolbar"])
        self._originals.clear()
        logger.debug("Restored original Anki methods")
