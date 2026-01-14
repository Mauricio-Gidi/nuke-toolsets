"""
Discovery and query utilities for on-disk toolsets.

`ToolsetsLoader` scans `TOOLSETS_ROOT`, builds Toolset objects with
`ToolsetFactory`, and exposes helpers to:
- list users,
- filter toolsets by name, tags, description, and user,
- fetch a user's toolset by exact name.

No Nuke API calls here. Pure filesystem and Python logic.
"""

import os

from .config import TOOLSETS_ROOT, IGNORE, ALL
from .toolset import ToolsetFactory


class ToolsetsLoader:
    """
    Load and filter toolsets from disk.

    This class provides functionality to load toolsets from a directory structure,
    organize them by user, and filter them based on various criteria such as name,
    tags, and description.
    """


    def __init__(self, toolsets_root=None):
        """
        Initialize the ToolsetsLoader instance.

        Args:
            toolsets_root (str, optional): Absolute path of the directory that contains all user toolsets. If not given, uses the configured TOOLSETS_ROOT.
        """
        self.toolsets_root = toolsets_root or TOOLSETS_ROOT
        self._toolsets = {}
        self._toolsets_factory = ToolsetFactory()
        self.load()


    def load(self):
        self._toolsets = {}
        self._load_errors = []
        if not os.path.isdir(self.toolsets_root):
            return
    
        for user_name in os.listdir(self.toolsets_root):
            user_root = os.path.join(self.toolsets_root, user_name)
            if not os.path.isdir(user_root) or user_name.startswith(IGNORE) or user_name == ".DS_Store":
                continue
            self._toolsets[user_name] = []
            for toolset_name in os.listdir(user_root):
                toolset_root = os.path.join(user_root, toolset_name)
                if (not os.path.isdir(toolset_root) or toolset_name.startswith(IGNORE) or toolset_name == ".DS_Store"):
                    continue
                try:
                    toolset = self._toolsets_factory.create(toolset_root)
                except Exception as e:
                    self._load_errors.append((toolset_root, str(e)))
                    continue
                self._toolsets[user_name].append(toolset)



    def reload(self):
        """
        Reload toolsets from disk.
        Calls load() to refresh the in-memory toolset list.
        """
        self.load()


    def get_users(self):
        """
        Get all users from the toolsets root.

        Returns:
            list[str]: Sequence of user names in the toolsets root directory.
        """
        return list(self._toolsets.keys())


    def get_load_errors(self):
        """Return errors encountered during load() as a list of (toolset_root, message)."""
        return list(self._load_errors)


    def get_toolset_by(self, name = "", tags = None, description = "", user=ALL):

        if tags is None:
            tags = []
        else:
            tags = list(tags)

        # validate
        if (
            not isinstance(name, str)
            or not isinstance(tags, list)
            or not all(isinstance(t, str) for t in tags)
            or not isinstance(description, str)
            or (user != ALL and not isinstance(user, str))
        ):
            raise ValueError(
                "Filter parameters: name (str), tags (list[str]), description (str), user (str or ALL)"
            )

        all_users = self.get_users()
        if user == ALL:
            users_to_search = all_users
        else:
            if user not in all_users:
                raise KeyError(f"No such user '{user}'. Choose from: {all_users}")
            users_to_search = [user]

        normalized_name = name.strip().lower()
        normalized_description = description.strip().lower()
        normalized_tags = {t.strip().lower() for t in tags if t and t.strip()}

        matching_toolsets = []

        for user_name in users_to_search:
            for toolset in self._toolsets.get(user_name, []):

                meta = getattr(toolset, "meta", {}) or {}

                # name
                toolset_name = (getattr(toolset, "name", "") or "").lower()
                if normalized_name and normalized_name not in toolset_name:
                    continue

                # normalize toolset tags to a lowercase set of tokens
                raw_tags = getattr(toolset, "meta", {}).get("tags", [])

                toolset_tags = [tag.strip().lower() for tag in raw_tags if isinstance(tag, str) and tag.strip()]
                # each requested tag must be a substring of some toolset tag
                if normalized_tags and not all(any(req in have for have in toolset_tags) for req in normalized_tags):
                    continue

                toolset_description = str(meta.get("description", "")).lower()    
                if normalized_description and normalized_description not in toolset_description:
                    continue

                matching_toolsets.append(toolset)

        return matching_toolsets



    def get_toolset(self, user_name, toolset_name):
        """
        Get a single toolset by user and toolset name.
        """
        # Normalize inputs (tolerate stray whitespace / case)
        user = (user_name or "").strip()
        target = (toolset_name or "").strip().casefold()

        # This raises KeyError itself if the user doesn't exist — that's fine for now.
        user_toolsets = self.get_toolset_by(user=user)

        for ts in user_toolsets:
            if (ts.name or "").strip().casefold() == target:
                return ts

        # Toolset not found for an existing user
        raise KeyError(
            f"No such toolset: '{toolset_name}' for '{user_name}'. "
            f"Choose from toolsets: {[t.name for t in user_toolsets]}"
        )