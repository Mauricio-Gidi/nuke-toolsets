def execute():
    import nuke
    import os
    import re
    import glob

    reads = nuke.allNodes("Read")
    if not reads:
        nuke.message("No Read nodes found.")
        return

    missing = []
    for r in reads:
        try:
            path = r["file"].value()
        except Exception:
            continue

        if not path:
            missing.append((r.name(), "Empty file path"))
            continue

        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            missing.append((r.name(), "Missing folder: " + folder))
            continue

        # Handle sequences roughly: %04d or ####
        if "%0" in path or "####" in path:
            pat = path
            pat = re.sub(r"%0\dd", "*", pat)
            pat = pat.replace("####", "*")
            matches = glob.glob(pat)
            if not matches:
                missing.append((r.name(), "No sequence frames found for pattern: " + os.path.basename(path)))
        else:
            if not os.path.exists(path):
                missing.append((r.name(), "Missing file: " + os.path.basename(path)))

    if not missing:
        nuke.message("Read validation OK: no missing paths detected.")
        return

    lines = ["Missing Read sources:"]
    lines.append("")
    for node_name, reason in missing[:80]:
        lines.append("- {}: {}".format(node_name, reason))
    if len(missing) > 80:
        lines.append("")
        lines.append("(+{} more)".format(len(missing) - 80))

    nuke.message("\n".join(lines))
