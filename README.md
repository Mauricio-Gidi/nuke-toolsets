# Toolsets Package for Nuke

## Overview

The `toolsets` package is a modular extension for Foundry Nuke, designed to integrate custom toolsets into Nuke's UI. It provides a graphical user interface (GUI) for managing, creating, and saving toolsets, supporting both Nuke and Python types. The package follows the Model-View-Controller (MVC) design pattern for maintainability and scalability.

## Features

- **Custom Nuke Menu Integration**: Adds a "Toolsets" submenu under "Scripts" in Nuke's main menu bar.
- **GUI for Toolset Management**: Launches a PySide2-based GUI for browsing, creating, and saving toolsets.
- **Toolset Types**: Supports creation of both Nuke and Python toolsets.
- **MVC Architecture**: Separates logic into model, view, and controller modules for clarity and extensibility.
- **Configurable**: Uses a configuration file for persistent settings.
- **Icon Support**: Includes icons for visual distinction in the UI.

## Directory Structure

```
toolsets/
│
├── menu.py
│
└── toolsets/
    ├── config.py
    ├── loader.py
    ├── saver.py
    ├── toolset.py
    │
    ├── icons/
    │   ├── Nuke.png
    │   └── Python.png
    │
    └── mvc/
        ├── controller.py
        ├── main.py
        ├── model.py
        ├── view.py
        └── widgets.py

```

## Usage

### 1. Integration with Nuke

The package is designed to be loaded as a Nuke menu extension. The main integration script is `menu.py`:

- Adds "Toolsets" under "Scripts" in the Nuke menu bar.
- Provides commands to show the main GUI and create new toolsets.

**Example:**
```python
from toolsets.mvc import main; main.show()
```

### 2. Launching the GUI

- Select "Scripts > Toolsets > Show" in Nuke to open the main Toolsets GUI.
- Use "Scripts > Toolsets > New Toolset > Nuke" or "Python" to create new toolsets of the respective type.

### 3. Creating and Saving Toolsets

- The GUI allows users to create new toolsets, edit existing ones, and save them using the `saver.py` logic.
- Toolsets can be loaded from disk using `loader.py`.

### 4. Configuration

- Persistent settings are managed via `config.py`.
- Icons for toolsets are stored in `icons/` and referenced in the UI.

## Modules

### `config.py`
Handles reading and writing configuration settings for the toolsets package.

### `loader.py`
Implements logic to load toolsets from disk or other sources.

### `saver.py`
Provides functionality to save toolsets to disk.

### `toolset.py`
Defines the data structure and operations for individual toolsets.

### `mvc/`
Implements the Model-View-Controller pattern:
- **controller.py**: Handles user actions and coordinates between model and view.
- **main.py**: Entry point for launching the GUI.
- **model.py**: Defines data models for toolsets.
- **view.py**: Contains GUI layout and components.
- **widgets.py**: Custom widgets for enhanced UI functionality.

## Requirements

- **Nuke**: The package is intended for use within Foundry Nuke.
- **PySide2**: Required for GUI components. Install via:
  ```powershell
  pip install PySide2
  ```

## Installation

1. Place the `toolsets` directory in your Nuke plugin path.
2. Ensure `menu.py` is loaded at Nuke startup (e.g., via your `menu.py` or `init.py`).
3. Install `PySide2` in your Python environment.

## Customization

- Add new icons to the `icons/` directory for additional toolset types.
- Extend the MVC modules to support new features or toolset types.
- Modify `config.py` for custom configuration options.

## Troubleshooting

- If the GUI does not launch, ensure `PySide2` is installed and available in your Python environment.
- Check Nuke's script editor for error messages related to menu integration or module imports.

## License

Specify your license here (e.g., MIT, GPL, proprietary).

## Authors

- [Your Name]
- [Contributors]

## Contact

For support or feature requests, contact [your email or GitHub].
