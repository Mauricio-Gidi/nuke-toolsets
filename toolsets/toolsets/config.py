"""toolsets.config

Central configuration for the Toolsets system.

Defines shared constants used by UI and non-UI modules:
- TOOLSETS_ROOT: base directory that contains per-user toolsets (storage for data.json + toolset files),
- ICONS_ROOT and ICONS: paths to PNG icons per toolset type,
- ACCENT_COLOR: primary UI accent color used by Qt stylesheets.

Configuration notes:
- You can override TOOLSETS_ROOT with the environment variable NUKE_TOOLSETS_ROOT.
- The default TOOLSETS_ROOT is ~/.nuke/toolsets_data (separate from the plugin install folder).
"""

from __future__ import annotations

import os


ENV_TOOLSETS_ROOT = "NUKE_TOOLSETS_ROOT"


def _default_toolsets_root() -> str:
    return os.path.join(os.path.expanduser("~"), ".nuke", "toolsets_data")


# Absolute path that contains all user toolsets.
# Priority:
# 1) NUKE_TOOLSETS_ROOT env var
# 2) Default: ~/.nuke/toolsets_data
TOOLSETS_ROOT = os.path.normpath(os.environ.get(ENV_TOOLSETS_ROOT) or _default_toolsets_root())


# Folder/file name prefixes to ignore while scanning TOOLSETS_ROOT.
# str.startswith() accepts a tuple of prefixes.
IGNORE = (".", "_")

# Special value for "all users" filter.
ALL = "ALL"


# Path to the icons directory (relative to this file)
ICONS_ROOT = os.path.join(os.path.dirname(__file__), "icons")

# Dictionary mapping toolset types to their icon paths
ICONS = {
    "Nuke": os.path.join(ICONS_ROOT, "Nuke.png"),
    "Python": os.path.join(ICONS_ROOT, "Python.png"),
}

# Accent color used for certain widgets in the UI.
ACCENT_COLOR = "#9DB5E8"
