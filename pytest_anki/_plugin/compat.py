import os
from typing import Any, Optional

_QT_API_MAP = {
    "qt5": "PyQt5",
    "pyqt5": "PyQt5",
    "qt6": "PyQt6",
    "pyqt6": "PyQt6",
}


def _resolve_qt_api_from_env() -> Optional[str]:
    qt_api = os.environ.get("QT_API", "").strip().lower()
    return _QT_API_MAP.get(qt_api)


def _detect_qt() -> str:
    qt_prefix = _resolve_qt_api_from_env()
    if qt_prefix is not None:
        try:
            __import__(qt_prefix)
        except ImportError:
            raise ImportError(
                f"QT_API={os.environ.get('QT_API')} but {qt_prefix} is not installed:\n"
                f"  pip install pytest-anki[{qt_prefix.lower()}]"
            )
        return qt_prefix

    for prefix in ("PyQt6", "PyQt5"):
        try:
            __import__(prefix)
            return prefix
        except ImportError:
            continue
    raise ImportError(
        "No Qt bindings found. Install PyQt6 or PyQt5:\n"
        "  pip install pytest-anki[qt6]\n"
        "  pip install pytest-anki[qt5]"
    )


_QT_PREFIX = _detect_qt()
QT_VERSION_MAJOR = 6 if _QT_PREFIX == "PyQt6" else 5
QT_PREFIX = _QT_PREFIX


def _import_qt_core() -> Any:
    if _QT_PREFIX == "PyQt6":
        from PyQt6 import QtCore
    else:
        from PyQt5 import QtCore
    return QtCore


def _import_qt_webengine() -> Any:
    if _QT_PREFIX == "PyQt6":
        from PyQt6.QtWebEngineCore import QWebEngineProfile
    else:
        from PyQt5.QtWebEngineWidgets import QWebEngineProfile
    return QWebEngineProfile


def _import_qt_widgets() -> Any:
    if _QT_PREFIX == "PyQt6":
        from PyQt6.QtWidgets import QMainWindow
    else:
        from PyQt5.QtWidgets import QMainWindow
    return QMainWindow


_core = _import_qt_core()
_WebEngineProfile = _import_qt_webengine()
_QMainWindow = _import_qt_widgets()

qInstallMessageHandler = _core.qInstallMessageHandler
QMessageLogContext = _core.QMessageLogContext
QObject = _core.QObject
QRunnable = _core.QRunnable
QtMsgType = _core.QtMsgType
pyqtSignal = _core.pyqtSignal
QThreadPool = _core.QThreadPool
QTimer = _core.QTimer
QWebEngineProfile = _WebEngineProfile
QMainWindow = _QMainWindow
