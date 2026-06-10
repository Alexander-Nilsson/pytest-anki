"""Session teardown orchestration.

A single module with one public interface — everything a caller
must know is that ``TeardownManager.shutdown(...)`` cleans up
a running Anki session safely.
"""

import logging
import sys as _sys
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from aqt.main import AnkiQt

logger = logging.getLogger(__name__)


class TeardownManager:
    """Orchestrate safe teardown of an Anki test session.

    Usage::

        TeardownManager.shutdown(mw, anki_base_dir, initial_profile_hooks)
    """

    @staticmethod
    def shutdown(
        mw: "AnkiQt",
        anki_base_dir: str,
        initial_profile_hooks: Optional[List] = None,
    ) -> None:
        """Shut down an Anki session, cleaning up all resources.

        Swallows and logs non-critical errors so that later cleanup
        steps always run.
        """
        _teardown_mw(mw)
        _restore_hooks(mw, initial_profile_hooks or [])
        _cleanup_addon_modules(anki_base_dir)
        _reset_locale()


def _teardown_mw(mw: "AnkiQt") -> None:
    """Shut down the main window and its subsystems."""
    logger.debug("Starting Anki session teardown")
    try:
        mw.errorHandler.unload()
        mw.mediaServer.shutdown()
    except Exception as exc:
        logger.warning("Error during Anki session teardown: %s", exc)
    try:
        mw.backend.await_backup_completion()
    except Exception as exc:
        logger.warning("Error waiting for backup completion: %s", exc)
    mw.deleteLater()
    logger.debug("Anki session teardown complete")


def _restore_hooks(mw: "AnkiQt", initial_profile_hooks: List) -> None:
    """Restore gui_hooks and clear anki_hooks to pre-session state."""
    import aqt
    from anki import hooks as anki_hooks

    # Restore gui_hooks to pre-session state
    aqt.gui_hooks.profile_did_open._hooks[:] = initial_profile_hooks

    # Clear hooks added during app initialization
    anki_hooks._hooks = {}


def _cleanup_addon_modules(anki_base_dir: str) -> None:
    """Remove addon modules from sys.modules to prevent stale imports."""
    removed_count = 0
    for _mod_name in list(_sys.modules):
        _mod = _sys.modules[_mod_name]
        if _mod is not None and hasattr(_mod, "__file__") and _mod.__file__:
            if anki_base_dir in str(_mod.__file__):
                del _sys.modules[_mod_name]
                removed_count += 1
    if removed_count:
        logger.debug("Removed %d addon modules from sys.modules", removed_count)


def _reset_locale() -> None:
    """Reset locale — test_nextIvl will fail on some systems otherwise."""
    import locale

    locale.setlocale(locale.LC_ALL, "")
