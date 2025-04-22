import json
import os
import tempfile
from typing import Dict, List, Optional

from facefusion import state_manager
from facefusion.filesystem import is_file, create_directory
from facefusion.typing import File

# Initialize state if not already set
if state_manager.get_item('temp_path') is None:
    state_manager.init_item('temp_path', tempfile.gettempdir())

# File history structure
# {
#   "source_files": [
#     {"path": "/path/to/file.jpg", "type": "image", "timestamp": 1234567890}
#   ],
#   "target_files": [
#     {"path": "/path/to/file.mp4", "type": "video", "timestamp": 1234567890}
#   ]
# }

def get_history_file_path() -> str:
    """Get the path to the history file"""
    # Ensure temp_path is set
    if state_manager.get_item('temp_path') is None:
        state_manager.init_item('temp_path', tempfile.gettempdir())

    history_dir = os.path.join(state_manager.get_item('temp_path'), 'facefusion', 'history')
    create_directory(history_dir)
    return os.path.join(history_dir, 'file_history.json')

def load_history() -> Dict:
    """Load file history from disk"""
    history_file = get_history_file_path()
    if is_file(history_file):
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"source_files": [], "target_files": []}
    return {"source_files": [], "target_files": []}

def save_history(history: Dict) -> None:
    """Save file history to disk"""
    history_file = get_history_file_path()
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def add_source_file(file_path: str, file_type: str) -> None:
    """Add a source file to history"""
    if not is_file(file_path):
        return

    history = load_history()

    # Check if file already exists in history
    for file in history["source_files"]:
        if file["path"] == file_path:
            # Move to top of list (most recent)
            history["source_files"].remove(file)
            history["source_files"].insert(0, file)
            save_history(history)
            return

    # Add new file to history
    import time
    history["source_files"].insert(0, {
        "path": file_path,
        "type": file_type,
        "timestamp": int(time.time())
    })

    # Limit history size to 20 items
    if len(history["source_files"]) > 20:
        history["source_files"] = history["source_files"][:20]

    save_history(history)

def add_target_file(file_path: str, file_type: str) -> None:
    """Add a target file to history"""
    if not is_file(file_path):
        return

    history = load_history()

    # Check if file already exists in history
    for file in history["target_files"]:
        if file["path"] == file_path:
            # Move to top of list (most recent)
            history["target_files"].remove(file)
            history["target_files"].insert(0, file)
            save_history(history)
            return

    # Add new file to history
    import time
    history["target_files"].insert(0, {
        "path": file_path,
        "type": file_type,
        "timestamp": int(time.time())
    })

    # Limit history size to 20 items
    if len(history["target_files"]) > 20:
        history["target_files"] = history["target_files"][:20]

    save_history(history)

def get_source_files() -> List[Dict]:
    """Get list of source files from history"""
    history = load_history()
    return history["source_files"]

def get_target_files() -> List[Dict]:
    """Get list of target files from history"""
    history = load_history()
    return history["target_files"]

def clear_history() -> None:
    """Clear all file history"""
    save_history({"source_files": [], "target_files": []})
