"""
Integrate the Toolsets UI into Nuke's menu.

Creates a "Scripts/Toolsets" submenu and registers commands to:
- open the main Toolsets browser window,
- open the "New Toolset" dialog for Nuke or Python toolsets.

Notes
-----
This file is discovered by Nuke on startup via NUKE_PATH. Commands import the
UI entry points lazily to keep startup overhead low.
"""

import nuke


# Add a "Toolsets" submenu under "Scripts" in the Nuke menu bar
menu = nuke.menu("Nuke").addMenu("Scripts/Toolsets")


# Add a command to show the main Toolsets GUI
menu.addCommand(
    "Show",
    "from toolsets.mvc import main; main.show()"
)


# Add submenu for creating new toolsets of specific types
menu_new_toolset = menu.addMenu("New Toolset")
menu_new_toolset.addCommand(
    "Nuke",
    "from toolsets.mvc import main; main.show_add_new_toolset('Nuke')"
)
menu_new_toolset.addCommand(
    "Python",
    "from toolsets.mvc import main; main.show_add_new_toolset('Python')"
)