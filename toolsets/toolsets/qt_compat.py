"""toolsets.qt_compat

Qt compatibility imports for PySide2 (Qt5) and PySide6 (Qt6).

This tool targets:
- Nuke 13.x (Python 3.7, PySide2 / Qt5)
- Nuke 16+ (Python 3.11, PySide6 / Qt6)

Import Qt modules from here instead of importing PySide2/PySide6 directly.
"""

from __future__ import annotations

try:
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
except Exception:  # pragma: no cover
    from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore


# QShortcut moved modules between Qt5/Qt6 bindings.
QShortcut = getattr(QtGui, "QShortcut", QtWidgets.QShortcut)


def make_save_sequence():
    """Return a QKeySequence for Save that works in Qt5 and Qt6."""
    try:
        return QtGui.QKeySequence(QtGui.QKeySequence.Save)
    except Exception:
        try:
            return QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Save)
        except Exception:
            return QtGui.QKeySequence("Ctrl+S")


def make_escape_sequence():
    """Return a QKeySequence for Escape that works in Qt5 and Qt6."""
    return QtGui.QKeySequence("Esc")


def _escape_key() -> int:
    # Qt5: QtCore.Qt.Key_Escape
    if hasattr(QtCore.Qt, "Key_Escape"):
        return int(QtCore.Qt.Key_Escape)
    # Qt6: QtCore.Qt.Key.Key_Escape
    return int(QtCore.Qt.Key.Key_Escape)


ESC_KEY = _escape_key()
