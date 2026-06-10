"""Test AnkiQt initialisation — controlled init for test isolation.

Deepens the monkey-patch firewall by replacing the closure-based
``custom_init_factory`` with a class whose methods can be tested
and overridden individually. The ``patch_anki`` context manager
remains the seam; ``TestAnkiQtInit`` is the adapter behind it.
"""

from typing import TYPE_CHECKING, Any, Callable, List

from .aniki_compat import create_flag_manager, create_task_manager, finish_ui_setup
from .compat import QMainWindow

if TYPE_CHECKING:
    from argparse import Namespace

    from anki._backend import RustBackend
    from aqt import AnkiApp
    from aqt.main import AnkiQt
    from aqt.profiles import ProfileManager as ProfileManagerType

PostUISetupCallbackType = Callable[["AnkiQt"], None]


class TestAnkiQtInit:
    """Controlled replacement for ``AnkiQt.__init__`` in tests.

    Usage::

        init = TestAnkiQtInit(post_ui_callback)
        init.run(main_window, app, pm, backend, opts, args)
    """

    def __init__(self, post_ui_callback: PostUISetupCallbackType) -> None:
        self._post_ui_callback = post_ui_callback

    def run(
        self,
        main_window: "AnkiQt",
        app: "AnkiApp",
        profile_manager: "ProfileManagerType",
        backend: "RustBackend",
        opts: "Namespace",
        args: List[Any],
        **kwargs: Any,
    ) -> None:
        QMainWindow.__init__(main_window)
        main_window.backend = backend
        main_window.state = "startup"
        main_window.opts = opts
        main_window.col = None  # type: ignore[assignment]  # ty: ignore[invalid-assignment]

        main_window.taskman = create_task_manager(main_window)
        main_window.media_syncer = self._create_media_syncer(main_window)
        main_window.flags = create_flag_manager(main_window)

        import aqt

        aqt.mw = main_window
        main_window.app = app
        main_window.pm = profile_manager
        main_window.safeMode = False
        main_window.setupUI()

        self._post_ui_callback(main_window)

        finish_ui_setup(main_window)

    @staticmethod
    def _create_media_syncer(main_window: "AnkiQt") -> Any:
        from aqt.mediasync import MediaSyncer

        return MediaSyncer(main_window)
