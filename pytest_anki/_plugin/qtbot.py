"""Standalone QtBot for subprocess-based tests and in-process use.

Provides ``wait_signal`` and ``wait_until`` methods equivalent to
pytest-qt's ``QtBot``, using only PyQt5/PyQt6 APIs. Fully
self-contained — avoids importing ``pytest_anki`` internals so it
can be imported from a subprocess script.
"""

import os
import time
from typing import Any, Callable, Optional, Tuple

# Qt binding detection (mirrors compat.py logic, kept self-contained
# so this module is importable from a subprocess without the full
# pytest_anki dependency chain).
_QT_API_MAP = {"qt5": "PyQt5", "pyqt5": "PyQt5", "qt6": "PyQt6", "pyqt6": "PyQt6"}
_qt_api = os.environ.get("QT_API", "").strip().lower()
_qt_prefix = _QT_API_MAP.get(_qt_api)
if _qt_prefix is None:
    for _prefix in ("PyQt6", "PyQt5"):
        try:
            __import__(_prefix)
            _qt_prefix = _prefix
            break
        except ImportError:
            continue
    else:
        raise ImportError("No Qt bindings found (PyQt5 or PyQt6)")

if _qt_prefix == "PyQt6":
    from PyQt6.QtCore import QCoreApplication, QEventLoop, Qt as _Qt, QTimer
    from PyQt6.QtWidgets import QApplication as _QApplication

    _aa_share = getattr(_Qt, "AA_ShareOpenGLContexts", None)
    if _aa_share is not None:
        QCoreApplication.setAttribute(_aa_share)
    else:
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
        except ImportError:
            pass
    _ALL_EVENTS = QEventLoop.ProcessEventsFlag.AllEvents
else:
    from PyQt5.QtCore import QCoreApplication, QEventLoop, QTimer
    from PyQt5.QtWidgets import QApplication as _QApplication

    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView  # noqa: F401
    except ImportError:
        pass
    _ALL_EVENTS = QEventLoop.AllEvents

# Ensure a QCoreApplication exists for signal waiting.
# Use QCoreApplication (not QApplication) so Anki can create its
# own QApplication without conflicts.
if not QCoreApplication.instance():
    QCoreApplication([])


class _SignalCatcher:
    """Context manager matching ``QtBot.wait_signal`` behaviour.
    Connects on entry, waits on exit, disconnects afterward.
    """

    def __init__(self, signal: Any, timeout: int = 5000) -> None:
        self.signal = signal
        self.timeout = timeout
        self.args: Optional[Tuple[Any, ...]] = None
        self._received = False

    def __enter__(self) -> "_SignalCatcher":
        self.signal.connect(self._on_signal)
        return self

    def __exit__(self, *args: Any) -> None:
        if not self._received:
            loop = QEventLoop()
            QTimer.singleShot(self.timeout, loop.quit)
            self.signal.connect(loop.quit)
            loop.exec()
            if not self._received:
                raise TimeoutError(
                    "Signal not received within {}ms".format(self.timeout)
                )
        try:
            self.signal.disconnect(self._on_signal)
        except TypeError:
            pass

    def _on_signal(self, *args: Any) -> None:
        self._received = True
        self.args = args


class StandaloneQtBot:
    """Stand-in for ``pytestqt.qtbot.QtBot`` in subprocess tests.

    Usage::

        qtbot = StandaloneQtBot()
        with qtbot.wait_signal(some_signal, timeout=3000):
            trigger_async_work()
    """

    @staticmethod
    def wait_signal(signal: Any, timeout: int = 5000) -> _SignalCatcher:
        return _SignalCatcher(signal, timeout)

    @staticmethod
    def wait_until(
        callback: Callable[[], Optional[bool]], timeout: int = 15000
    ) -> None:
        deadline = time.time() + timeout / 1000.0
        while time.time() < deadline:
            try:
                result = callback()
            except AssertionError:
                pass
            else:
                if result is None or result:
                    return
            loop = QEventLoop()
            QTimer.singleShot(50, loop.quit)
            loop.exec()
        raise TimeoutError("Condition not met within {}ms".format(timeout))


_qtbot = StandaloneQtBot()
