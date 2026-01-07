"""
Central configuration for the Toolsets system.

Defines shared constants used by UI and non-UI modules:
- TOOLSETS_ROOT: base directory that contains per-user toolsets,
- ICONS_ROOT and ICONS: paths to PNG icons per toolset type,
- ACCENT_COLOR: primary UI accent color used by Qt stylesheets.

Keep this module import-light. It is imported by loaders, savers, and the UI.
"""

import os

# Absolute path that contains all user toolsets.
# NOTE: Update this path as needed for deployment.
TOOLSETS_ROOT = r"C:\Users\mgidi\Desktop\borrar\TOOLSETS"

# Ignore all users/toolsets that start with this character (e.g., _temp, _backup)
IGNORE = "_"

# Constant to represent all users (used for filtering or special cases)
ALL = "ALL"

# Path to the icons directory (relative to this file)
ICONS_ROOT = os.path.join(
    os.path.dirname(__file__),
    "icons"
)

# Dictionary mapping toolset types to their icon paths
ICONS = {
    "Nuke": os.path.join(ICONS_ROOT, "Nuke.png"),
    "Python": os.path.join(ICONS_ROOT, "Python.png"),
}

# Accent color used for certain widgets in the UI.
ACCENT_COLOR = "#9DB5E8"