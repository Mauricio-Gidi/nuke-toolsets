"""
Central configuration for the Toolsets system.

- TOOLSETS_ROOT: base directory that contains per-user toolsets.
  Override with NUKE_TOOLSETS_ROOT.
- ICONS: paths to icons used by the UI.
"""

import os


ENV_TOOLSETS_ROOT = "NUKE_TOOLSETS_ROOT"


def _default_toolsets_root() -> str:
    """Default to a per-user folder under ~/.nuke that does not clash with plugin install paths."""
    return os.path.join(os.path.expanduser("~"), ".nuke", "toolsets_data")


# Absolute path that contains all user toolsets.
TOOLSETS_ROOT = os.path.normpath(os.environ.get(ENV_TOOLSETS_ROOT) or _default_toolsets_root())

# Ignore users/toolsets folders that start with these prefixes (e.g. _temp, .cache).
IGNORE_PREFIXES = ("_", ".")

# Constant to represent all users (used for filtering).
ALL = "ALL"


# Path to the icons directory (relative to this file)
ICONS_ROOT = os.path.join(os.path.dirname(__file__), "icons")

# Dictionary mapping toolset types to their icon paths
ICONS = {
    "Nuke": os.path.join(ICONS_ROOT, "Nuke.png"),
    "Python": os.path.join(ICONS_ROOT, "Python.png"),
    "Warning": os.path.join(ICONS_ROOT, "Warning.png"),
}

# Accent color used for certain widgets in the UI.
ACCENT_COLOR = "#9DB5E8"
