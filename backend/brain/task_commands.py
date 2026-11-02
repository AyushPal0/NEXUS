"""Normalize planner output without executing arbitrary model text."""
import re

COMMANDS = frozenset({
    "open_chrome", "open_youtube", "create_folder",
    "take_screenshot", "take_photo", "stop",
})

def normalize_task(task):
    if not isinstance(task, str):
        return None
    task = re.sub(r"^\s*(?:[-*]\s+|\d+[.)]\s+)", "", task).strip()
    task = task.strip("`'\" ,[]")
    return task if task in COMMANDS else None

def folder_name(command):
    match = re.search(r"\bcreate folder\s+called\s+(.+)$", command, re.IGNORECASE)
    if not match:
        return "NewFolder"
    name = match.group(1).strip().strip("\"'")
    # Spoken folder creation accepts one directory name, never a path.
    if not name or name in {".", ".."} or any(c in name for c in '<>:"/\\|?*'):
        raise ValueError("Please provide a single valid folder name.")
    return name
