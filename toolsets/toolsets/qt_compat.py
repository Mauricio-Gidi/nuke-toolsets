"""Qt compatibility helpers.

Support:
- Nuke 13.x (PySide2 / Qt5)
- Nuke 16+ (PySide6 / Qt6)

Keep this module small and import-safe.
"""

try:
    from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
except Exception:  # Nuke 13/14/15
    from PySide2 import QtWidgets, QtCore, QtGui  # type: ignore


# QShortcut moved from QtWidgets (Qt5) to QtGui (Qt6).
QShortcut = getattr(QtGui, "QShortcut", None) or getattr(QtWidgets, "QShortcut")


def save_keysequence():
    """Return the platform-appropriate Ctrl/Cmd+S key sequence."""
    try:  # Qt6
        return QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Save)
    except Exception:  # Qt5
        return QtGui.QKeySequence(QtGui.QKeySequence.Save)


def escape_keysequence():
    """Return an Escape key sequence (Qt5/Qt6 compatible)."""
    try:  # Qt6 enum
        key = QtCore.Qt.Key.Key_Escape
    except Exception:  # Qt5 enum
        key = QtCore.Qt.Key_Escape
    return QtGui.QKeySequence(key)

def escape_key():
    """Return the Escape key enum (Qt5/Qt6 compatible) for event.key() comparisons."""
    try:  # Qt6 enum
        return QtCore.Qt.Key.Key_Escape
    except Exception:  # Qt5 enum
        return QtCore.Qt.Key_Escape

def msgbox_yes_no():
    """Return (YES, NO) buttons compatible with Qt5/Qt6 QMessageBox APIs."""
    try:  # Qt6
        YES = QtWidgets.QMessageBox.StandardButton.Yes
        NO = QtWidgets.QMessageBox.StandardButton.No
    except Exception:  # Qt5
        YES = QtWidgets.QMessageBox.Yes
        NO = QtWidgets.QMessageBox.No
    return YES, NO
