# Nuke Toolsets
Links: [Portfolio](https://mauricio-gidi.github.io) | [GitHub](https://github.com/Mauricio-Gidi) | [LinkedIn](https://www.linkedin.com/in/mauricio-gidi-29689b22a/)

Browse toolsets stored on disk in a Qt user interface: insert .nk toolsets or run .py toolsets via a standard execute() entry point.
Compatibility: The Foundry Nuke 13+; tested on Windows. macOS and Linux not yet tested.

- **Insert Nuke toolsets** (`toolset.nk`) into the nodegraph (or DAG)
- **Run Python toolsets** (`toolset.py`) by calling a top-level `execute()`

[![Demo - Nuke Toolsets MVP](media/nuke-toolsets-demo.gif)](media/nuke-toolsets-demo.gif)

### Why it matters
A consistent on-disk toolset library reduces duplication and makes reuse predictable across a team.  
This tool browses a per-user structure under `NUKE_TOOLSETS_ROOT` (local or shared storage).

### Included
- Browse users + toolsets from disk
- Filter toolsets by **name** and **tags**
- View toolset metadata (user, tags, description)
- Insert `.nk` toolsets into the DAG
- Run `.py` toolsets via `execute()`
- Create new toolsets:
  - **Nuke**: from current Nuke node selection
  - **Python**: from script text
- Edit existing toolsets:
  - Tags + description for both types
  - Script editing for Python toolsets
  - Overwrite `.nk` payload from current selection (with confirmation)

### Not included (non-goals)
- No packaging/pip installer
- No network sync / publishing workflows
- No automated test suite (manual checklist only)

---

## Compatibility

### Supported
- **Nuke**: 13.x → 16+
- **OS**: Windows / macOS / Linux

### Tested
- **Windows**: 13.0v10, 15.2v6, 16.0v8

> Note: macOS/Linux are *supported* (cross-platform paths + Qt usage) but not tested yet.

---

## Install (manual)

This repo is structured as a “drop-in” Nuke plugin folder.

1. Copy the repo’s **`toolsets/`** folder into your Nuke `.nuke` directory:

- **Windows**: `%USERPROFILE%\.nuke\toolsets\`
- **macOS/Linux**: `~/.nuke/toolsets/`

2. Add the plugin folder to Nuke’s plugin path (one-time):

- Open (or create) your Nuke init file:
  - **Windows**: `%USERPROFILE%\.nuke\init.py`
  - **macOS/Linux**: `~/.nuke/init.py`

- Add these lines:
```py
import nuke
nuke.pluginAddPath("./toolsets")  # relative to your ~/.nuke folder
```

3. Restart Nuke.
4. Use: `Scripts > Toolsets > Show`

> **Important:** There are two separate folders:
> - `~/.nuke/toolsets/` = the **plugin install** folder (this repo’s `toolsets/` folder goes here)
> - `NUKE_TOOLSETS_ROOT` (default `~/.nuke/toolsets_data/`) = where your **toolset data** lives (`<user>/<toolset_name>/...`)

---

## Quick demo (included example toolsets)

This repo includes a tiny demo pack.

Option A (recommended): point the tool to the examples folder:

- Set `NUKE_TOOLSETS_ROOT` to:
  - Windows: `<this_repo>\examples\toolsets_data`
  - macOS/Linux: `<this_repo>/examples/toolsets_data`

Option B: copy the included examples into your default data folder:

- Copy `examples/toolsets_data/Demo User/` into:
  - Windows: `%USERPROFILE%\.nuke\toolsets_data\`
  - macOS/Linux: `~/.nuke/toolsets_data/`

---

## Repo layout

```
toolsets/               # copy this folder into ~/.nuke/
  init.py               # Nuke init entry point
  menu.py               # Nuke menu entry point
  toolsets/             # Python package
    config.py
    loader.py
    saver.py
    toolset.py
    icons/
      Nuke.png
      Python.png
      Warning.png
    mvc/
      controller.py
      main.py
      model.py
      view.py
      widgets.py

examples/               # optional demo TOOLSETS_ROOT content
  toolsets_data/        # point NUKE_TOOLSETS_ROOT here OR copy into your default toolsets_data
    Demo User/
      Validate Read nodes/
        data.json
        toolset.py
      Expression nodes for despilling/
        data.json
        toolset.nk
```

---

## Toolsets storage format

### Default root
By default, toolsets are stored in:

- `~/.nuke/toolsets_data`

### Layout
```
TOOLSETS_ROOT/
  <user>/
    <toolset_name>/
      data.json
      toolset.nk   OR   toolset.py
```

### `data.json` example
```json
{
  "description": "My blur setup",
  "tags": ["blur", "utility"]
}
```

---

## Configuration

### Set toolsets root via env var
You can override the default storage location using:

- `NUKE_TOOLSETS_ROOT=/path/to/toolsets`

If the env var is not set, the tool falls back to:

- `~/.nuke/toolsets_data`

---

## Usage

### Open Toolsets browser
- `Scripts > Toolsets > Show`

### Insert/run a toolset
- Select a toolset and click **Insert**, or double-click the toolset:
  - `.nk` toolset: inserts nodes into the DAG
  - `.py` toolset: imports the file and calls `execute()`
 
> ⚠️ **Safety note (Python toolsets):** `.py` toolsets execute arbitrary Python code inside Nuke.
> Only run toolsets you trust, and review the `toolset.py` file if you didn’t create it.

### Create a new toolset
- `Scripts > Toolsets > New Toolset > Nuke`
  - Saves the current Nuke node selection to `toolset.nk`
- `Scripts > Toolsets > New Toolset > Python`
  - Saves your script to `toolset.py`

### Edit an existing toolset
- Select toolset → **Edit**
- **Save** or **Cancel**
- Nuke toolsets require a current selection to overwrite `toolset.nk`

---

## Troubleshooting

### “No toolsets showing”
- Confirm `TOOLSETS_ROOT` exists and contains user folders.
- If you set `NUKE_TOOLSETS_ROOT`, confirm it points to the correct folder.

### “Python toolset won’t run”
- Ensure `toolset.py` defines a top-level callable:
  ```py
  def execute():
      pass
  ```

### “Qt / PySide import errors” (especially on Nuke 16+)
- This tool is intended to run **inside Nuke’s bundled Python/Qt environment**.
- Nuke 13 uses PySide2; Nuke 16+ uses PySide6. The codebase must support both.

---

## Manual test checklist (Windows)

- Open UI: `Scripts > Toolsets > Show`
- User search filters list correctly
- Toolset name filter works
- Tag filter works (comma/space-separated)
- Insert `.nk` toolset inserts nodes
- Run `.py` toolset calls `execute()`
- Create Nuke toolset:
  - no selection → shows error
  - with selection → saves toolset folder + `toolset.nk`
- Create Python toolset:
  - empty script → shows error
  - valid script → saves `toolset.py`
- Edit/save/cancel:
  - metadata updates persist in `data.json`
  - Python script edits persist to disk

---

## License
MIT (see `LICENSE`).

## Author
Mauricio Gidi
