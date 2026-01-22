"""
Models for listing, loading, and saving toolsets.

- Model: read-only operations for the main browser window, plus light
  edit-time validation for Nuke toolsets.
- AddNewToolsetModel: write-path wrapper that delegates to saver classes.
"""

from toolsets import loader, config, saver


class Model:
    def get_filtered_users(self, search_string):
        """
        Return users matching the search string.
        """
        users = self.get_all_users()
        return [user for user in users if search_string.lower() in user.lower()]

    def get_filtered_toolsets(self, user, search_string, tags=None):
        """
        Return toolsets matching the user and search string.
        """
        toolsets = self.toolsets_loader.get_toolset_by(
            name=search_string or "",
            tags=tags or [],
            user=user,
        )
        return toolsets

    def update_toolset(self, toolset, description, tags, toolset_data):
        """
        Update the metadata of a toolset.
        """
        toolset.update_meta(description, tags)
        toolset.update_toolset_data(toolset_data)
        

    def validate(self, toolset, name, description, tags, toolset_data):
        """
        Edit-time validation:
        - For Nuke toolsets, ensure there is a current selection in Nuke.
        - For Python toolsets, no additional checks (updates can be empty).
        Creation-time validation is handled elsewhere (AddNewToolsetModel).
        """
        if toolset.toolset_type() == "Nuke":
            try:
                import nuke  # available in Nuke's environment
            except Exception:
                # If we're not in Nuke, don't block edit-time metadata updates
                return
            if not nuke.selectedNodes():
                raise ValueError("No nodes selected in Nuke.")
            return

        # Python: no edit-time validation needed
        return




    def __init__(self):
        """
        Initialize the Model instance.
        """
        self.toolsets_loader = loader.ToolsetsLoader()


    def get_all_users(self):
        """
        Get all toolset users.

        Returns:
            list[str]: Sequence of all users (including ALL constant).
        """
        return [config.ALL] + self.toolsets_loader.get_users()


    def get_all_toolsets(self):
        """
        Get all toolsets of all users.

        Returns:
            list[toolset.toolset.ToolsetBase]: Sequence of all toolsets of all users.
        """
        return self.toolsets_loader.get_toolset_by()


    def get_scan_warnings(self):
        """Return warnings collected during the last scan."""
        return self.toolsets_loader.get_warnings()

    
    def get_toolset_source(self, toolset):
        """
        Return the text to show in the editor for the selected toolset.
        - Python toolsets: raw source
        - Nuke toolsets: classic text block summary (header + class histogram)
        """
        from toolsets.toolset import ToolsetPY, ToolsetNK

        if isinstance(toolset, ToolsetPY):
            return toolset.get_source()
        if isinstance(toolset, ToolsetNK):
            return toolset.get_summary_text()
        return ""




class AddNewToolsetModel:
    """
    Data store to add new toolset via the API.
    """
    def __init__(self, toolset_saver):
        """
        Initialize the AddNewToolsetModel instance.

        Args:
            toolset_saver (toolsets.toolset.saver.BaseToolsetSaver): The toolset saver to use for saving a new toolset.
        """
        self.toolset_saver = toolset_saver

    def save_toolset(self, name, description="", tags="", toolset_data=None):
        """
        Save a toolset under the given name.

        Args:
            name (str): The name to use for the toolset.
            description (str, optional): The description to use in the metadata file.
            tags (list[str], optional): Sequence of tags to associate the toolset with.
            toolset_data (any, optional): The data to save as a toolset. The actual data to save as a toolset data depends on the concrete saver implementation.
        """
        self.toolset_saver.save(name, description, tags, toolset_data)