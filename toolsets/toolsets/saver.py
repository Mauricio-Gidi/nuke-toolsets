"""
Persistence layer for creating and updating toolsets.

Provides two concrete savers:
- Nuke `.nk` saver: captures the current Nuke selection into `toolset.nk`.
- Python `.py` saver: writes validated source code into `toolset.py`.

Validation highlights:
- `.nk` saver requires a non-empty Nuke selection.
- `.py` saver normalizes tabs to spaces and writes UTF-8 text.
- Duplicate toolset names per user are rejected.
"""

import abc
import getpass
import os
import json

try:
    import nuke
except Exception:
    nuke = None

from . import config



class BaseToolsetSaver(abc.ABC):
    """
    Abstract base class for a Toolset saver.
    Handles user/toolset root logic and metadata writing.
    """


    def __init__(self, user=None, toolsets_root=None):
        """
        Initialize the BaseToolsetSaver instance.

        Args:
            user (str, optional): The name of the user to save the toolset to.
            toolsets_root (str, optional): Absolute path of the toolsets root location to save the toolset to.
        """
        self.user = user or getpass.getuser()
        self.toolsets_root = toolsets_root or config.TOOLSETS_ROOT


    def save(self, name, description="", tags=None, toolset_data=None):
        # normalize tags to a list[str]
        if tags is None:
            tags_list = []
        elif isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        elif isinstance(tags, (list, tuple, set)):
            tags_list = [str(t).strip() for t in tags if str(t).strip()]
        else:
            raise ValueError("tags must be list[str] or comma-separated str")

        self.validate(name, description, tags_list, toolset_data)
        toolset_root = self._assemble_toolset_root(name)
        if not os.path.isdir(toolset_root):
            os.makedirs(toolset_root)
        self._write_meta(toolset_root, description, tags_list)
        self.write_toolset_data(toolset_root, toolset_data)


    def _write_meta(self, toolset_root, description, tags):
        """
        Write the toolset's metadata file (data.json).

        Args:
            toolset_root (str): Absolute path of the toolset's root directory to save the metadata file to.
            description (str): The description to use in the metadata file.
            tags (list[str]): Sequence of tags to associate the toolset with.
        """
        metadata = {
            "description": description,
            "tags": tags or []
        }
        meta_path = os.path.join(toolset_root, "data.json")
        with open(meta_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)


    def validate(self, name, description, tags, toolset_data):
        """
        Ensure the requirements to save are met.

        Args:
            name (str): The name to validate if needed.
            description (str, optional): The description to validate.
            tags (list[str], optional): Sequence of tags to validate if needed.
            toolset_data (any, optional): The data to validate.

        Raises:
            ValueError: When the user has not entered a name or if the given name already exists as a toolset.
        """
        if not name:
            raise ValueError("Please enter a name.")
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError("tags must be list[str]")
        toolset_root = self._assemble_toolset_root(name)
        if os.path.isdir(toolset_root):
            raise ValueError(f"The toolset '{name}' already exists in your account. Please choose another name")

    def _assemble_toolset_root(self, name):
        """
        Assemble the absolute path of the toolset's root directory.

        Args:
            name (str): The name of the toolset to save.

        Returns:
            str: Absolute path of the toolset's root directory.
        """
        return os.path.join(
            self.toolsets_root,
            self.user,
            name
        )

    @abc.abstractmethod
    def write_toolset_data(self, toolset_root, toolset_data):
        """Write the toolset's toolset data.

        The actual data to save as a toolset data depends on the concrete saver implementation.

        Args:
            toolset_root (str): Absolute path where to save the toolset to.
            toolset_data (any, optional): The toolset data to save.
        """
        pass



class ToolsetSaverNK(BaseToolsetSaver):
    """
    Save a .nk toolset (Nuke nodes).
    """


    def validate(self, name, description, tags, toolset_data):
        """
        Ensure the requirements to save a .nk are met.

        Args:
            name (str): The name to validate if needed.
            description (str, optional): The description to validate.
            tags (list[str], optional): Sequence of tags to validate if needed.
            toolset_data (any, optional): The data to validate.

        Raises:
            ValueError: When the user has not selected any nodes.
        """
        super().validate(name, description, tags, toolset_data)

        if nuke:
            if not nuke.selectedNodes():
                raise ValueError(
                    "Please select the nodes to export as a new toolset."
                )


    def write_toolset_data(self, toolset_root, toolset_data):
        """
        Write the toolset's toolset data (.nk file).

        Args:
            toolset_root (str): Absolute path where to save the toolset to.
            toolset_data (any, optional): The toolset data to save.
        """
        path = os.path.join(toolset_root, "toolset.nk")
        if nuke:
            nuke.nodeCopy(path)



class ToolsetSaverPY(BaseToolsetSaver):
    """
    Save a .py toolset (Python script).
    """


    def validate(self, name, description, tags, toolset_data):
        """
        Ensure the requirements to save a .py are met.

        Args:
            name (str): The name to validate if needed.
            description (str, optional): The description to validate.
            tags (list[str], optional): Sequence of tags to validate if needed.
            toolset_data (any, optional): The data to validate.

        Raises:
            ValueError: When the user has not entered any code to save to the toolset.
        """
        super().validate(name, description, tags, toolset_data)
        if not toolset_data:
            raise ValueError("Please enter a script.")


    def write_toolset_data(self, toolset_root, toolset_data):
        """
        Write the toolset's toolset data to a Python file named "toolset.py".

        This function writes the provided Python source (a text string) into a
        file called ``toolset.py`` located inside the given ``toolset_root``
        directory. The implementation performs a minimal normalization step to
        replace tab characters with four spaces before writing the file. Any
        IO-related exceptions raised by ``open``/``write`` (for example
        permission errors or full disk) are propagated to the caller.

        Notes:
        - ``toolset_data`` is expected to be a Python ``str``. Non-string inputs
          will raise an AttributeError when ``replace`` is called.
        - Converting tabs to four spaces helps avoid mixed-tab/space
          indentation which can lead to subtle syntax errors in Python.

        Args:
            toolset_root (str): Absolute path where to save the toolset to.
            toolset_data (str): The Python source code to write to disk.

        Raises:
            OSError: Propagated if the file cannot be created or written.
        """
        path = os.path.join(toolset_root, "toolset.py")
        toolset_data = toolset_data.replace("\t", "    ")  # Normalize indentation: convert tabs to 4 spaces
        with open(path, "w", encoding="utf-8") as file:
            file.write(toolset_data)