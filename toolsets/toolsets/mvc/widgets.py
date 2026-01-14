"""
Custom Qt widgets used by the Toolsets UI.

Currently includes `ToolsetInfoWidget`, which renders toolset metadata,
a code/ASCII preview area, and action buttons for Insert, Edit, Save, and Cancel.
"""

from toolsets.qt_compat import QtWidgets, QtCore, QtGui, QShortcut, make_save_sequence, make_escape_sequence
from toolsets.config import ACCENT_COLOR


class ToolsetInfoWidget(QtWidgets.QWidget):
    """
    Display information for a given toolset.
    """
    save_requested = QtCore.Signal()
    cancel_requested = QtCore.Signal()


    def __init__(self):
        """
        Initialize the ToolsetInfoWidget instance.
        """
        super().__init__()
        self.create_widgets()
        self.create_layouts()
        self.set_style()
        self._create_shortcuts()


    def create_widgets(self):
        """
        Create widgets for the toolset info display.
        """
        self.label_title = QtWidgets.QLabel()
        self.label_user = QtWidgets.QLabel()

        self.label_tags = QtWidgets.QLabel()
        self.label_tags_edit = QtWidgets.QLineEdit()
        self.label_tags_edit.hide()  # Becomes visible when edit mode.

        self.text_info = QtWidgets.QTextEdit()
        self.text_info.setReadOnly(True)  # Switches in edit mode

        self.text_script = self.create_python_widget()
        self.text_script.hide()

        self.button_insert = QtWidgets.QPushButton("Insert")
        self.button_edit_save = QtWidgets.QPushButton("Edit")
        self.button_edit_save.setMaximumWidth(100)
        self.button_cancel_save = QtWidgets.QPushButton("Cancel")
        self.button_cancel_save.setMaximumWidth(100)
        self.button_cancel_save.hide()


    def create_layouts(self):
        """
        Create layout for the toolset info widget.
        """
        self.layout_top = QtWidgets.QHBoxLayout()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_bottom = QtWidgets.QHBoxLayout()

        self.layout_top.addWidget(self.label_title)
        self.layout_top.addStretch()
        self.layout_top.addWidget(self.label_user)

        self.layout_bottom.addWidget(self.button_insert)
        self.layout_bottom.addWidget(self.button_edit_save)
        self.layout_bottom.addWidget(self.button_cancel_save)

        self.layout_main.addLayout(self.layout_top)
        self.layout_main.addWidget(self.label_tags)
        self.layout_main.addWidget(self.label_tags_edit)
        self.layout_main.addWidget(self.text_info)
        self.layout_main.addWidget(self.text_script)
        self.layout_main.addLayout(self.layout_bottom)

        self.setLayout(self.layout_main)


    def set_style(self):
        """
        Set stylesheet for widgets.
        """
        self.label_title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.button_insert.setStyleSheet(f"background-color: {ACCENT_COLOR};")

    def _create_shortcuts(self):
        # Ctrl+S -> Save (use standard Save key sequence)
        shortcut_save = QShortcut(make_save_sequence(), self)
        shortcut_save.activated.connect(lambda: self.save_requested.emit())

        # Esc -> Cancel
        shortcut_escape = QShortcut(make_escape_sequence(), self)
        shortcut_escape.activated.connect(lambda: self.cancel_requested.emit())

    def enter_edit_mode(self):
        self.label_tags.hide()
        self.label_tags_edit.show()
        self.button_cancel_save.show()
        self.text_script.show()
        self.text_info.setReadOnly(False)
        self.button_edit_save.setText("Save")

    def exit_edit_mode(self):
        self.label_tags.show()
        self.label_tags_edit.hide()
        self.button_cancel_save.hide()
        self.text_script.hide()
        self.text_info.setReadOnly(True)
        self.button_edit_save.setText("Edit")

    @staticmethod
    def create_python_widget():
        """
        Create and return a QTextEdit configured for editing Python code
        (and also for showing ASCII previews for Nuke toolsets).
        """
        text_script = QtWidgets.QTextEdit()

        text_script.setTabStopDistance(text_script.fontMetrics().horizontalAdvance(" ") * 4)
        #text_script.setTabStopDistance(13)  # 2nd option

        # Keep ASCII art aligned
        text_script.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        # Monospace font for code/ascii tree
        text_script.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        text_script.setPlainText('def execute():\n    """The main entry point to execute."""\n    ')
        return text_script

