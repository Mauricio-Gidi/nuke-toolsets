"""
Domain objects for toolsets and a simple factory.

Classes
-------
- ToolsetBase: common helpers for metadata, paths, previews, and updates.
- ToolsetNK: executes by `nuke.nodePaste()` and updates from selection.
- ToolsetPY: executes by importing and calling a top-level `execute()`.
- ToolsetFactory: inspects a directory for `toolset.nk` or `toolset.py` and
  constructs the corresponding Toolset instance.

Only the execute paths touch Nuke or Python import machinery.
"""

import abc
import importlib
import json
import os
import sys
import tokenize

try:
    import nuke
except Exception:
    nuke = None



class ToolsetBase(abc.ABC):
    """
    Abstract base class representing a toolset on disk.
    """


    def __init__(self, root):
        """
        Initialize the ToolsetBase.

        Args:
            root (str): Absolute path of the toolsets root location
        """
        self.root = root
        self.name = os.path.basename(self.root)
        self.meta_load_error = None
        self.meta_missing = False
        self.meta = self.load_meta()


    @property
    def meta_file(self):
        """
        Get the toolset's metadata file.

        Returns:
            str: Absolute path of the toolset's metadata file.
        """
        return os.path.join(self.root, "data.json")


    @property
    def toolset_file(self):
        """
        Get the toolset's toolset file (either .nk or .py).

        Returns:
            str: Absolute path of the toolset's toolset file, or empty string if not found.
        """
        nk_path = os.path.join(self.root, "toolset.nk")
        py_path = os.path.join(self.root, "toolset.py")
        if os.path.isfile(nk_path):
            return nk_path
        if os.path.isfile(py_path):
            return py_path
        return ""


    @property
    def user(self):
        """
        Get the toolset's user.

        Returns:
            str: The name of the user the toolset belongs to.
        """
        return os.path.basename(os.path.dirname(self.root))


    def load_meta(self):
        """
        Load the toolset's metadata from data.json.

        Returns:
            dict: The metadata parsed from the toolset's metadata file, or empty dict on failure.
        """
        # Missing metadata is not an error — treat as empty fields.
        if not os.path.isfile(self.meta_file):
            self.meta_missing = True
            return {}

        self.meta_missing = False

        try:
            with open(self.meta_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            # Corrupt/invalid metadata should not block the toolset from loading.
            self.meta_load_error = f"{type(e).__name__}: {e}"
            return {}
        
    def update_meta(self, description, tags):
        """
        Update the toolset's metadata with the given parameters.

        Args:
            description (str): The description to update the meta data from.
            tags (list): The tags to update the tags from.
        """
        self.meta['description'] = description
        self.meta['tags'] = tags

        with open(self.meta_file, 'w', encoding="utf-8") as f:
            json.dump(self.meta, f, indent=4)
            f.write("\n")  # ensure trailing newline
          
        # Metadata now exists and is valid JSON
        self.meta_missing = False
        self.meta_load_error = ""

  
    def get_source(self):
        """
        Return the source code of this toolset as a string.

        Returns:
            str: The contents of the toolset file, or an empty string if no file exists or it can't be read.
        """
        path = self.toolset_file
        if not path or not os.path.isfile(path):
            return ""
        try:
            with tokenize.open(path) as f:
                return f.read()
        except (OSError, UnicodeError, SyntaxError):
            # Last resort: don't crash edit mode; show something readable
            with open(path, "rb") as bf:
                return bf.read().decode("utf-8", errors="replace")


    @abc.abstractmethod
    def execute(self):
        """Execute toolset"""
        pass

    @abc.abstractmethod
    def update_toolset_data(self):
        """Update toolset data"""
        pass

    @abc.abstractmethod
    def toolset_type(self):
        """Return the toolset's type.

        Return:
            str: The type of the toolset.
        """
        pass



class ToolsetNK(ToolsetBase):
    """
    A toolset representing a .nk file (Nuke nodes).
    """


    def execute(self):
        """
        Execute the toolset by inserting it into the DAG (Nuke node graph).
        """
        if nuke:
            nuke.nodePaste(self.toolset_file)


    def toolset_type(self):
        """
        Return the toolset's type.

        Returns:
            str: The type of the toolset.
        """
        return "Nuke"
    

    def update_toolset_data(self, toolset_data=None):
        """Override the .nk toolset file"""
        if nuke:
            if nuke.selectedNodes():
                path = os.path.join(self.root, "toolset.nk")
                nuke.nodeCopy(path)

    def get_summary_text(self, top_n: int = 10) -> str:
        """
        Classic Text Block:
        ───────────────────────────────────────────────
        <toolset name>
        <N> nodes · <U> classes
        ───────────────────────────────────────────────
        Top Classes:

        <Class>   <Count>
        ...
        ───────────────────────────────────────────────
        """
        from collections import Counter

        # Read file safely
        try:
            with open(self.toolset_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return "───────────────────────────────────────────────\n" \
                "Error: Unable to read toolset .nk file.\n" \
                "───────────────────────────────────────────────"

        # Collect class names (simple & fast)
        classes = []
        for raw in lines:
            s = raw.strip()
            # Node block lines usually look like: "Blur {" or "Merge2 {"
            if s.endswith("{") and " " in s:
                cls = s.split("{", 1)[0].strip()
                if cls and cls[0].isalpha():
                    classes.append(cls)

        total_nodes = len(classes)
        counts = Counter(classes)
        unique_classes = len(counts)

        title = f"{self.name}"
        subtitle = f"{total_nodes} nodes · {unique_classes} classes"

        # Separator width based on longest header line (fixed minimum for aesthetics)
        width = max(47, len(title), len(subtitle), len("Top Classes:"))
        sep = "─" * width

        # Top-N classes by count (desc), then name (asc)
        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]

        # Column widths
        name_w = max(8, min(22, max((len(k) for k, _ in items), default=8)))
        count_w = max(2, len(str(max((v for _, v in items), default=0))))

        lines_out = [sep, title, subtitle, sep, "Top Classes:", ""]
        if not items:
            lines_out.append("(no nodes found)")
        else:
            for name, cnt in items:
                lines_out.append(f"{name.ljust(name_w)}  {str(cnt).rjust(count_w)}")
        lines_out.append(sep)

        return "\n".join(lines_out)




            



class ToolsetPY(ToolsetBase):
    """
    A toolset representing a .py file (Python script).
    """

    def update_toolset_data(self, toolset_data=None):
        """Override the .py toolset file"""
        if toolset_data is None:
            return  # allow empty script content

        if not isinstance(toolset_data, str):
            toolset_data = str(toolset_data)

        toolset_data = toolset_data.replace("\t", "    ")  # Normalize indentation: convert tabs to 4 spaces
        if not toolset_data.endswith("\n"):
            toolset_data += "\n"  # ensure trailing newline

        with open(self.toolset_file, "w", encoding="utf-8") as file:
            file.write(toolset_data)

            
    def execute(self):

        # Build a unique module name so multiple toolsets cannot collide
        # Build a safe module name so toolsets cannot collide.
        safe_name = "".join(c if c.isalnum() else "_" for c in self.name)
        unique_name = f"toolset_{safe_name}"

        # Absolute path to the Python file that defines an execute() function.
        module_path = self.toolset_file

        # Create an import spec that instructs Python to load code from module_path and bind it under unique_name.
        spec = importlib.util.spec_from_file_location(unique_name, module_path)

        # Guard against unexpected failures building the spec or its loader.
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot build spec for toolset module: {module_path}")

        # Allocate an empty module object from the spec. Still not executed.
        module = importlib.util.module_from_spec(spec)

        # Register the module under its unique name BEFORE execution.
        sys.modules[unique_name] = module

        try:
            # Execute the module's top-level code in its own namespace.
            spec.loader.exec_module(module)

            if not hasattr(module, "execute") or not callable(module.execute):
                raise AttributeError(
                    f"Python toolset '{self.name}' must define a top-level execute() function."
                )

            # Call the toolset's public entry point. This is the user's code.
            module.execute()

        finally:
            # Remove the temporary module from the cache to avoid stale reuse on subsequent runs of other toolsets with different files.
            sys.modules.pop(unique_name, None)



    def toolset_type(self):
        """
        Return the toolset's type.

        Returns:
            str: The type of the toolset.
        """
        return "Python"




class ToolsetInvalid(ToolsetBase):
    """
    A toolset folder that cannot be executed because it is missing a valid toolset file.

    This class exists so malformed folders still appear in the UI (with a warning icon),
    instead of being silently skipped.
    """

    def __init__(self, root, error_message="Missing toolset.nk or toolset.py"):
        self.error_message = error_message
        super().__init__(root)

    def execute(self):
        raise RuntimeError(self.error_message)

    def toolset_type(self):
        return "Warning"

    def update_toolset_data(self, toolset_data=None):
        # Nothing to update — there is no toolset file on disk.
        return


class ToolsetFactory:
    """
    Factory that creates Toolset instances given the toolset extensions.
    """

    def create(self, toolset_root):
        """
        Create a toolset instance for the given toolset root location.

        This looks up the given toolset's extension and creates the appropriate Toolset instance.
        Malformed folders are returned as ToolsetInvalid so they remain visible in the UI.

        Args:
            toolset_root (str): Absolute path of the toolset root location to create a Toolset instance for.

        Returns:
            toolsets.toolset.ToolsetBase: The Toolset instance for the given toolset_root location.

        Raises:
            OSError: When the given toolset_root does not exist.
        """
        if not os.path.isdir(toolset_root):
            raise OSError(f"No such toolset root: {toolset_root}")

        nk_path = os.path.join(toolset_root, "toolset.nk")
        py_path = os.path.join(toolset_root, "toolset.py")

        nk_exists = os.path.isfile(nk_path)
        py_exists = os.path.isfile(py_path)

        if nk_exists and py_exists:
            return ToolsetInvalid(
                toolset_root,
                error_message=(
                    "Multiple payload files found. "
                    "Candidates: ['toolset.nk', 'toolset.py']. "
                    "How to fix: keep only ONE payload file (delete/rename the extra)."
                ),
            )
        if nk_exists:
            return ToolsetNK(toolset_root)
        if py_exists:
            return ToolsetPY(toolset_root)


        # Case-only payload filename mismatch: may work on case-insensitive filesystems
        try:
            entries = os.listdir(toolset_root)
        except Exception:
            entries = []

        lower_entries = {e.lower() for e in entries}

        mismatches = []
        for expected in ("toolset.nk", "toolset.py"):
            if expected in lower_entries and expected not in entries:
                # find the actual casing to show in the message (first match)
                actual = next(e for e in entries if e.lower() == expected)
                mismatches.append((actual, expected))

        if mismatches:
            details = ", ".join([f"'{actual}' → '{expected}'" for actual, expected in mismatches])
            return ToolsetInvalid(
                toolset_root,
                error_message=(
                    "Payload filename case mismatch. "
                    f"Detected: {details}. "
                    "How to fix: rename the file(s) to exactly 'toolset.nk' or 'toolset.py' (lowercase). "
                ),
            )


        # If there is a toolset.* but with an unsupported extension, keep it visible as a warning.
        for file_name in os.listdir(toolset_root):
            name, extension = os.path.splitext(file_name)
            if name != "toolset":
                continue
            return ToolsetInvalid(
                toolset_root,
                error_message=(
                    f"Unsupported toolset extension '{extension}'. Expected toolset.nk or toolset.py. "
                    "How to fix: rename the payload to 'toolset.nk' or 'toolset.py' (or delete the file)."
                ),            
            )

        # No toolset file at all: keep visible as a warning item.
        return ToolsetInvalid(
            toolset_root,
            error_message=(
                "No toolset.nk or toolset.py found in this folder. "
                "How to fix: add a payload named 'toolset.nk' or 'toolset.py' (or delete the folder)."
            ),
        )