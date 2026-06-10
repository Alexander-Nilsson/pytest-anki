"""Central registry of Anki version-gated behaviour.

Every version-specific branch (try/except, Version comparison, hasattr)
lives here. Callers import a stable function instead of writing their
own version check. When a new Anki version changes an API, edit this
module — not N scattered call sites.
"""

from typing import TYPE_CHECKING, Any, List

from packaging.version import Version

if TYPE_CHECKING:
    from anki.collection import Collection
    from aqt.main import AnkiQt


def get_anki_version() -> Version:
    """Return the running Anki version."""
    try:
        from anki.buildinfo import version
    except (ImportError, ModuleNotFoundError):
        from anki import version  # type: ignore[attr-defined, no-redef]
    return Version(version)


def create_task_manager(main_window: "AnkiQt") -> Any:
    """TaskManager constructor accepted ``main_window`` from 2.1.28+."""
    from aqt.taskman import TaskManager

    try:
        return TaskManager(main_window)
    except TypeError:
        return TaskManager()  # ty: ignore[missing-argument]


def create_flag_manager(main_window: "AnkiQt") -> Any:
    """FlagManager available from 2.1.45+."""
    try:
        from aqt.flags import FlagManager

        return FlagManager(main_window)
    except (ImportError, ModuleNotFoundError):
        return None


def finish_ui_setup(main_window: "AnkiQt") -> None:
    """finish_ui_setup available on AnkiQt from 2.1.28+."""
    try:
        main_window.finish_ui_setup()
    except AttributeError:
        pass


def get_auto_update_attr() -> str:
    """Return the attribute name for auto-update setup.

    ``setupAutoUpdate`` on older Anki, ``setup_auto_update`` on newer.
    """
    from aqt.main import AnkiQt

    if hasattr(AnkiQt, "setupAutoUpdate"):
        return "setupAutoUpdate"
    return "setup_auto_update"


def create_profile_manager(base_dir: str) -> Any:
    """ProfileManager expects ``Path`` on 2.1.56+, ``str`` on older."""
    from aqt.profiles import ProfileManager

    if get_anki_version() >= Version("2.1.56"):
        from pathlib import Path

        pm = ProfileManager(base=Path(base_dir))
    else:
        pm = ProfileManager(base=base_dir)  # ty: ignore[invalid-argument-type]
    return pm


def remove_deck(collection: "Collection", deck_id: int) -> None:
    """``decks.remove`` (2.1.28+) vs ``decks.rem`` (legacy)."""
    from anki.decks import DeckId

    try:
        collection.decks.remove([deck_id])  # type: ignore[list-item]  # ty: ignore[invalid-argument-type]
    except AttributeError:
        collection.decks.rem(DeckId(deck_id), cardsToo=True)


def get_deck_ids(collection: "Collection") -> List[int]:
    """``all_names_and_ids`` (2.1.28+) vs ``allIds`` (legacy)."""
    try:
        return [d.id for d in collection.decks.all_names_and_ids()]
    except AttributeError:
        return collection.decks.allIds()  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
