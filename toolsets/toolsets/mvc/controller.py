"""
Controllers that wire the UI to the models.

- Controller: drives the main browser (population, filtering, selection,
  insert/edit/save/cancel flows, and icon management).
- AddNewToolsetViewController: drives the "New Toolset" dialog, validates input,
  and calls the appropriate saver, with simple user feedback.
"""

from toolsets.qt_compat import QtWidgets, QtGui, msgbox_yes_no
from toolsets import config
import os

try:
    import nuke
except Exception:
    nuke = None


class Controller:
    """
    Drive a toolsets main view.
    Handles user interaction, filtering, and toolset insertion.
    """


    def __init__(self, view, model):
        """
        Initialize the controller instance.

        Args:
            view (toolsets.mvc.view.View): The view to drive.
            model (toolsets.mvc.model.Model): The data store that holds all toolsets.
        """
        self.view = view
        self.model = model
        self.edit_mode = False
        if not os.path.isdir(config.TOOLSETS_ROOT):
            QtWidgets.QMessageBox.information(
                self.view,
                "Toolsets",
                "Toolsets root folder was not found.\n\n"
                f"Path: {config.TOOLSETS_ROOT}\n\n"
                "Set NUKE_TOOLSETS_ROOT to override.",
            )
        self.populate_user_list()
        self.populate_toolsets_list()
        self.load_toolset_info()
        self.create_signals()


    @property
    def selected_toolset(self):
        """
        Get the currently selected toolset.

        Returns:
            Optional[toolsets.toolset.ToolsetBase]
        """
        return getattr(self.view.list_toolsets.currentItem(), "toolset", None)


    @property
    def selected_user(self):
        """
        Get the name of the currently selected user.

        Returns:
            str: The name of the currently selected user.
        """
        item = self.view.list_users.currentItem()
        return item.text() if item is not None else None



    def populate_user_list(self):
        """
        Populate the user list with all users.
        """
        self.view.list_users.addItems(self.model.get_all_users())
        self.view.list_users.setCurrentRow(0)


    def populate_toolsets_list(self):
        """
        Populate the toolsets list with all toolsets.
        """
        for toolset in self.model.get_all_toolsets():
            item = QtWidgets.QListWidgetItem(toolset.name)
            icon = config.ICONS.get(toolset.toolset_type(), config.ICONS.get('Nuke'))
            item.setIcon(QtGui.QIcon(icon))
            self.view.list_toolsets.addItem(item)
            item.toolset = toolset  # Attach toolset object to item
        if self.view.list_toolsets.count():
            self.view.list_toolsets.setCurrentRow(0)
        self.update_warnings_button()
        




    def update_warnings_button(self):
        """Update the Warnings button label + enabled state based on last scan warnings."""
        warnings = self.model.get_scan_warnings()
        count = len(warnings)
        if count:
            self.view.button_warnings.setEnabled(True)
            self.view.button_warnings.setText(f"Warnings ({count})")
        else:
            self.view.button_warnings.setEnabled(False)
            self.view.button_warnings.setText("Warnings")


    def show_warnings(self):
        """Show a one-time popup listing warnings from the last scan."""
        warnings = self.model.get_scan_warnings()
        if not warnings:
            QtWidgets.QMessageBox.information(self.view, "Toolsets - Warnings", "No warnings from the last scan.")
            return

        # Keep it readable: one warning per line.
        text = "\n".join(f"- {w}" for w in warnings)
        QtWidgets.QMessageBox.information(self.view, "Toolsets - Warnings", text)


    def _format_tags(self, tags) -> str:
        """Return tags as a clean comma-separated string."""
        if not tags:
            return ""
        if isinstance(tags, str):
            parts = [p.strip() for p in tags.split(",") if p.strip()]
            return ", ".join(parts)
        try:
            parts = [str(t).strip() for t in tags if str(t).strip()]
            return ", ".join(parts)
        except TypeError:
            return str(tags).strip()

    def load_toolset_info(self):
        """
        Load and display toolset info for the currently active toolset.
        """
        toolset = self.selected_toolset
        if toolset == None:
            return
        
        self.view.toolset_info_widget.label_title.setText(toolset.name)
        self.view.toolset_info_widget.label_user.setText(toolset.user)
        self.view.toolset_info_widget.label_tags.setText(self._format_tags(toolset.meta.get("tags")))
        self.view.toolset_info_widget.text_info.setText(toolset.meta.get("description", ""))


    def create_signals(self):
        """
        Connect UI signals to controller methods.
        """
        self.view.button_close.clicked.connect(self.view.close)
        self.view.button_warnings.clicked.connect(self.show_warnings)
        self.view.toolset_info_widget.button_insert.clicked.connect(lambda: self.insert_toolset())
        self.view.toolset_info_widget.button_edit_save.clicked.connect(lambda: self.on_edit_save_clicked())
        self.view.toolset_info_widget.save_requested.connect(self.on_edit_save_clicked)  # Shortcut
        self.view.toolset_info_widget.button_cancel_save.clicked.connect(lambda: self.on_cancel_save_clicked())
        self.view.toolset_info_widget.cancel_requested.connect(self.on_cancel_save_clicked)  # Shortcut
        # self.view.list_toolsets.clicked.connect(lambda: self.load_toolset_info())
        self.view.list_toolsets.currentItemChanged.connect(lambda: self.load_toolset_info())
        self.view.list_users.currentItemChanged.connect(lambda: self.filter_toolsets())
        self.view.list_toolsets.doubleClicked.connect(lambda: self.insert_toolset())
        self.view.input_search_user.textChanged.connect(lambda: self.filter_users())
        self.view.input_search_toolsets.textChanged.connect(lambda: self.filter_toolsets())
        self.view.input_search_tags.textChanged.connect(lambda: self.filter_toolsets())




    def filter_users(self):
        """
        Filter users by current user search string using model.
        """
        search = self.view.input_search_user.text().lower()
        filtered_users = self.model.get_filtered_users(search)
        for row in range(self.view.list_users.count()):
            item = self.view.list_users.item(row)
            item.setHidden(item.text() not in filtered_users)


    def insert_toolset(self):
        """Insert/Execute the currently selected toolset."""
        toolset = self.selected_toolset
        if toolset is None:
            QtWidgets.QMessageBox.information(self.view, "Toolsets", "Select a toolset first.")
            return

        try:
            toolset.execute()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.view,
                "Toolset error",
                f"Failed to run '{toolset.name}' ({toolset.toolset_type()}):\n{e}",
            )

    def on_edit_save_clicked(self):
        if not self.edit_mode:
            toolset = self.selected_toolset
            if not toolset:
                return
            self.begin_edit(toolset)

        elif self.edit_mode:

            try:
                self.attempt_save()
            except ValueError as e:
                QtWidgets.QMessageBox.critical(self.view, "Save error", f"{e}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.view,
                    "Save error",
                    f"Unexpected error while saving:\n{e}",
                )
            
        

    def begin_edit(self, toolset):
        toolset_info_widget = self.view.toolset_info_widget

        toolset_info_widget.enter_edit_mode()

        if (toolset.toolset_type() == "Python"):
            toolset_info_widget.text_script.setPlainText(self.model.get_toolset_source(toolset))
            toolset_info_widget.text_script.setReadOnly(False)
        elif (toolset.toolset_type() == "Nuke"):
            toolset_info_widget.text_script.setPlainText(self.model.get_toolset_source(toolset))
            toolset_info_widget.text_script.setReadOnly(True)
        elif (toolset.toolset_type() == "Warning"):
            # Surface why this toolset is broken; still allow metadata edits.
            msg = getattr(toolset, "error_message", None) or "No toolset file."
            toolset_info_widget.text_script.setPlainText(msg)
            toolset_info_widget.text_script.setReadOnly(True)

        toolset_info_widget.label_tags_edit.setText(", ".join(toolset.meta.get("tags", [])))
        self.edit_mode = True

        self.focus_on_widget(toolset_info_widget, True)


    def focus_on_widget(self, widget, state):
        keep_enable_widgets = set(widget.findChildren(QtWidgets.QWidget))
        keep_enable_widgets.update(self.get_parents(widget))

        for w in self.view.findChildren(QtWidgets.QWidget):
            if w not in keep_enable_widgets:
                w.setEnabled(not state)
                


    def get_parents(self, widget):
        parents = []
        current = widget
        while current:
            parents.append(current)
            current = current.parentWidget()
        return parents


    def restore_view_after_edit(self, toolset):
        toolset_info_widget = self.view.toolset_info_widget

        toolset_info_widget.exit_edit_mode()

        self.load_toolset_info()
        self.edit_mode = False
        if not os.path.isdir(config.TOOLSETS_ROOT):
            QtWidgets.QMessageBox.information(
                self.view,
                "Toolsets",
                "Toolsets root folder was not found.\n\n"
                f"Path: {config.TOOLSETS_ROOT}\n\n"
                "Set NUKE_TOOLSETS_ROOT to override.",
            )

        self.focus_on_widget(toolset_info_widget, False)


    def on_cancel_save_clicked(self):
        self.restore_view_after_edit(self.selected_toolset)


    def attempt_save(self):
        
        toolset = self.selected_toolset
        
        new_tags_string = self.view.toolset_info_widget.label_tags_edit.text().strip()
        new_tags_list = [tag.strip() for tag in new_tags_string.split(",") if tag.strip()]
        new_description = self.view.toolset_info_widget.text_info.toPlainText().strip()

        if (toolset.toolset_type() == "Python"):
            new_toolset_data = self.view.toolset_info_widget.text_script.toPlainText().strip()
        elif (toolset.toolset_type() == "Warning"):
            # No toolset file to overwrite; allow saving metadata only.
            new_toolset_data = None
        elif (toolset.toolset_type() == "Nuke"):
            new_toolset_data = None
            # Let model.validate raise with the real reason (e.g., no selection)
            self.model.validate(toolset, toolset.name, new_description, new_tags_list, new_toolset_data)

            from collections import Counter  # keep local if you prefer

            nodes = nuke.selectedNodes() if nuke else []
            if not nodes:
                return

            # Build list of non-empty class names and count them.
            class_names = [getattr(n, "Class", lambda: "")().strip() for n in nodes]
            class_names = [c for c in class_names if c]
            counts = Counter(class_names)

            # Deterministic order (A–Z). For count-desc order, use:
            # classes = [k for k, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
            classes = sorted(counts.keys())

            # "2 Merge, 5 Blur, 1 Defocus"
            names_text = ", ".join(f"{counts[c]} {c}" for c in classes)

            # Use total node count for singular/plural.
            total = sum(counts.values())
            noun = "node" if total == 1 else "nodes"

            YES, NO = msgbox_yes_no()
            res = QtWidgets.QMessageBox.question(
                self.view,
                "Confirm Add",
                f"Overriding toolset with the next {noun}:\n\n{names_text}",
                YES | NO,
                NO,
            )
            if res != YES:
                return




        try:
            self.model.update_toolset(toolset, new_description, new_tags_list, new_toolset_data)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.view,
                "Save error",
                f"Failed to save '{toolset.name}':\n{e}",
            )
            return

        self.restore_view_after_edit(toolset)
        


    def filter_toolsets(self):
        """
        Filter the toolsets list by the given search string or the active user using model.
        """
        search = self.view.input_search_toolsets.text().lower()
        user = self.selected_user
        if user is None:
            return
        
        raw_tags = self.view.input_search_tags.text()
        # split on comma/semicolon/space; remove empties
        import re
        tags = [t.strip() for t in re.split(r"[;, ]+", raw_tags) if t.strip()]

        filtered_toolsets = self.model.get_filtered_toolsets(user, search, tags)
        for row in range(self.view.list_toolsets.count()):
            item = self.view.list_toolsets.item(row)
            item.setHidden(item.toolset not in filtered_toolsets)



class AddNewToolsetViewController:
    """
    Drive an AddNewToolsetView instance for creating new toolsets.
    """
    def __init__(self, view, model, saver_type):
        """
        Initialize the AddNewToolsetViewController instance.

        Args:
            view (toolsets.mvc.view.AddNewToolsetView): The view to drive.
            model (toolsets.mvc.model.AddNewToolsetModel): The data store to create a new toolset.
            saver_type (str): Type name of the toolset saver to use.
        """
        self.view = view
        self.model = model
        self.saver_type = saver_type
        self.setup()
        self.create_signals()


    def setup(self):
        """
        Set up the view depending on the used saver_type.
        """
        window_title = f"Save new toolset ({self.saver_type})"
        self.view.setWindowTitle(window_title)
        if self.saver_type == "Python":
            self.view.layout_form.addRow("Script", self.view.text_script)
            # self.view.setMinimumHeight(1000)


    def create_signals(self):
        """
        Connect UI signals to controller methods.
        """
        self.view.button_cancel.clicked.connect(lambda: self.view.close())
        self.view.button_create.clicked.connect(lambda: self.save_new_toolset())


    def save_new_toolset(self):
        """
        Collect input from the "Add New Toolset" view, validate it, persist the new
        toolset via the model, and give the user feedback.

        Behavior
        --------
        - Reads the following fields from the view:
            * name: the toolset name from `input_name` (trimmed)
            * description: free-form description from `text_description`
            * tags: parsed from `input_tags` by splitting on commas and stripping
                surrounding whitespace for each tag
            * toolset_data: optional payload (for example the script text when
                `saver_type == "Python"`) from `text_script`
        - Calls `self.model.toolset_saver.validate(...)`. If validation raises
            ValueError, shows a modal QMessageBox containing the error text and
            aborts without saving.
        - On successful validation calls `self.model.save_toolset(...)` to
            persist the new toolset, closes the view, and shows a success
            QMessageBox.

        Side effects
        ------------
        - May display modal QMessageBox dialogs for validation errors or
            successful creation.
        - Closes the Add New Toolset view on successful save.

        Errors
        ------
        - Propagates no exceptions itself; validation errors are caught and
            shown to the user as a message box. Other unexpected exceptions
            raised by the model are not explicitly handled here.
        """
        name = self.view.input_name.text().strip()
        description = self.view.text_description.toPlainText()
        tags = [tag.strip() for tag in self.view.input_tags.text().split(",")]
        toolset_data = None
        if self.saver_type == "Python":
            toolset_data = self.view.text_script.toPlainText()
        # Validation
        try:
            self.model.toolset_saver.validate(name, description, tags, toolset_data)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self.view, "Toolset validation error", f"{e}")
            return
        # Save
        try:
            self.model.save_toolset(name, description, tags, toolset_data)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.view,
                "Create error",
                f"Failed to create new toolset '{name}':\n{e}",
            )
            return

        self.view.close()
        # Feedback
        QtWidgets.QMessageBox.information(
            self.view,
            "Created",
            f"Successfully created new toolset: '{name}'",
        )
