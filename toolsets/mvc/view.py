"""
Qt views composing the Toolsets interface.

- View: the main browser window with user list, toolset list, and details pane.
- AddNewToolsetView: the window used to create a new toolset.

No business logic; controllers drive behavior.
"""

from PySide2 import QtWidgets, QtCore

from toolsets.config import ACCENT_COLOR
from toolsets.mvc.widgets import ToolsetInfoWidget



class View(QtWidgets.QWidget):
    """
    Main toolsets view (main window).
    """


    def __init__(self):
        """
        Initialize the View instance.
        """
        super().__init__()
        self.setup_ui()
        self.create_widgets()
        self.create_layout()
        self.set_style()


    def setup_ui(self):
        """
        Set up the UI window properties.
        """
        self.setWindowTitle("Toolsets")
        self.setMinimumSize(QtCore.QSize(1400, 800))
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)


    def create_widgets(self):
        """
        Create widgets for the main view.
        """
        self.list_users_title = QtWidgets.QLabel("User")
        self.input_search_user = QtWidgets.QLineEdit()
        self.input_search_user.setPlaceholderText("user name")
        self.list_users = QtWidgets.QListWidget()
        self.list_toolsets_title = QtWidgets.QLabel("Toolsets")
        self.input_search_toolsets = QtWidgets.QLineEdit()
        self.input_search_toolsets.setPlaceholderText("toolset name")
        self.input_search_tags = QtWidgets.QLineEdit()
        self.input_search_tags.setPlaceholderText("tags: blur, python, key")
        self.list_toolsets = QtWidgets.QListWidget()
        self.toolset_info_widget = ToolsetInfoWidget()
        self.button_close = QtWidgets.QPushButton("Close")


    def create_layout(self):
        """
        Create layout for the main view.
        """
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_middle = QtWidgets.QHBoxLayout()
        self.layout_users = QtWidgets.QVBoxLayout()
        self.layout_toolsets = QtWidgets.QVBoxLayout()
        self.layout_users.addWidget(self.list_users_title)
        self.layout_users.addWidget(self.input_search_user)
        self.layout_users.addWidget(self.list_users)
        self.layout_toolsets.addWidget(self.list_toolsets_title)
        self.layout_toolsets.addWidget(self.input_search_toolsets)
        self.layout_toolsets.addWidget(self.input_search_tags)
        self.layout_toolsets.addWidget(self.list_toolsets)
        self.layout_middle.addLayout(self.layout_users, 1)
        self.layout_middle.addLayout(self.layout_toolsets, 1)
        self.layout_middle.addWidget(self.toolset_info_widget, 5)
        self.layout_main.addLayout(self.layout_middle)
        self.layout_main.addWidget(self.button_close)
        self.setLayout(self.layout_main)


    def set_style(self):
        """
        Set style sheet for the main view.
        """
        self.setStyleSheet("QPushButton {height: 20px}")
        self.list_users_title.setStyleSheet("font-size: 10pt")
        self.list_toolsets_title.setStyleSheet("font-size: 10pt")


    def keyPressEvent(self, event):
        """
        Override keyPressEvent to react on various key presses.

        Args:
            event (QtCore.QEvent): The event that got triggered.
        """
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()



class AddNewToolsetView(QtWidgets.QWidget):
    """
    View to add new toolset (dialog window).
    """
    def __init__(self):
        """
        Initialize the AddNewToolsetView instance.
        """
        super().__init__()
        self.setup()
        self.create_widgets()
        self.create_layouts()
        self.set_style()



    def setup(self):
        """
        Set up UI window properties.
        """
        self.setMinimumSize(QtCore.QSize(600, 300))
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)



    def create_widgets(self):
        """
        Create widgets for the add-new-toolset view.
        """
        self.input_name = QtWidgets.QLineEdit()
        self.input_tags = QtWidgets.QLineEdit()
        self.text_description = QtWidgets.QTextEdit()


        # Added dynamically in the controller for Python Toolset creation
        self.text_script = ToolsetInfoWidget.create_python_widget()

        self.button_create = QtWidgets.QPushButton("Create Toolset")
        self.button_cancel = QtWidgets.QPushButton("Cancel")


    def create_layouts(self):
        """
        Create layouts for the add-new-toolset view.
        """
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_form = QtWidgets.QFormLayout()
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_form.addRow("Name", self.input_name)
        self.layout_form.addRow("Tags", self.input_tags)
        self.layout_form.addRow("Description", self.text_description)
        self.layout_buttons.addWidget(self.button_create)
        self.layout_buttons.addWidget(self.button_cancel)
        self.layout_main.addLayout(self.layout_form)
        self.layout_main.addLayout(self.layout_buttons)
        self.setLayout(self.layout_main)



    def keyPressEvent(self, event):
        """
        Override keyPressEvent to react on various key presses.

        Args:
            event (QtCore.QEvent): The event that got triggered.
        """
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()


    def set_style(self):
        """
        Set up the stylesheet for the add-new-toolset view.
        """
        self.button_create.setStyleSheet(f"background-color: {ACCENT_COLOR};")