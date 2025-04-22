from typing import List, Dict, Optional, Tuple

import gradio

from facefusion import file_history, state_manager, wording
from facefusion.filesystem import is_image, is_video
from facefusion.uis.core import register_ui_component
from facefusion.face_store import clear_reference_faces, clear_static_faces

SOURCE_FILES_GALLERY : Optional[gradio.Gallery] = None
TARGET_FILES_GALLERY : Optional[gradio.Gallery] = None
SOURCE_FILES_BUTTON : Optional[gradio.Button] = None
TARGET_FILES_BUTTON : Optional[gradio.Button] = None
CLEAR_HISTORY_BUTTON : Optional[gradio.Button] = None

def render() -> None:
    global SOURCE_FILES_GALLERY
    global TARGET_FILES_GALLERY
    global SOURCE_FILES_BUTTON
    global TARGET_FILES_BUTTON
    global CLEAR_HISTORY_BUTTON
    
    with gradio.Accordion("File History", open=False):
        with gradio.Tabs():
            with gradio.Tab("Source Files"):
                SOURCE_FILES_GALLERY = gradio.Gallery(
                    label="Source Files History",
                    columns=4,
                    rows=2,
                    height="auto",
                    object_fit="contain",
                    show_label=True,
                    visible=True,
                    elem_id="source_files_gallery"
                )
                SOURCE_FILES_BUTTON = gradio.Button("Load Selected Source File")
            
            with gradio.Tab("Target Files"):
                TARGET_FILES_GALLERY = gradio.Gallery(
                    label="Target Files History",
                    columns=4,
                    rows=2,
                    height="auto",
                    object_fit="contain",
                    show_label=True,
                    visible=True,
                    elem_id="target_files_gallery"
                )
                TARGET_FILES_BUTTON = gradio.Button("Load Selected Target File")
        
        CLEAR_HISTORY_BUTTON = gradio.Button("Clear History")
    
    register_ui_component('source_files_gallery', SOURCE_FILES_GALLERY)
    register_ui_component('target_files_gallery', TARGET_FILES_GALLERY)


def listen() -> None:
    source_image = gradio.update()
    target_image = gradio.update()
    target_video = gradio.update()
    
    # Update galleries when UI is loaded
    SOURCE_FILES_GALLERY.change(lambda: None, None, None)
    TARGET_FILES_GALLERY.change(lambda: None, None, None)
    
    # Load source file when selected
    SOURCE_FILES_BUTTON.click(
        load_source_file,
        inputs=SOURCE_FILES_GALLERY,
        outputs=[gradio.update(value=None)]
    )
    
    # Load target file when selected
    TARGET_FILES_BUTTON.click(
        load_target_file,
        inputs=TARGET_FILES_GALLERY,
        outputs=[gradio.update(value=None)]
    )
    
    # Clear history
    CLEAR_HISTORY_BUTTON.click(
        clear_history,
        inputs=None,
        outputs=[SOURCE_FILES_GALLERY, TARGET_FILES_GALLERY]
    )
    
    # Update galleries with current files
    update_galleries()


def update_galleries() -> None:
    """Update galleries with current files from history"""
    source_files = file_history.get_source_files()
    target_files = file_history.get_target_files()
    
    # Filter to only include existing files
    source_files = [f for f in source_files if is_image(f["path"])]
    target_files = [f for f in target_files if is_image(f["path"]) or is_video(f["path"])]
    
    # Update galleries
    if SOURCE_FILES_GALLERY:
        SOURCE_FILES_GALLERY.update(value=[f["path"] for f in source_files])
    
    if TARGET_FILES_GALLERY:
        TARGET_FILES_GALLERY.update(value=[f["path"] for f in target_files])


def load_source_file(selected_index: int) -> None:
    """Load selected source file"""
    if selected_index is None:
        return
    
    source_files = file_history.get_source_files()
    if 0 <= selected_index < len(source_files):
        selected_file = source_files[selected_index]
        if is_image(selected_file["path"]):
            # Set as source path
            state_manager.set_item('source_paths', [selected_file["path"]])
            
            # Move to top of history
            file_history.add_source_file(selected_file["path"], selected_file["type"])
            
            # Update UI
            from facefusion.uis.components.source import update
            update([{"name": selected_file["path"]}])


def load_target_file(selected_index: int) -> None:
    """Load selected target file"""
    if selected_index is None:
        return
    
    target_files = file_history.get_target_files()
    if 0 <= selected_index < len(target_files):
        selected_file = target_files[selected_index]
        
        # Clear faces when changing target
        clear_reference_faces()
        clear_static_faces()
        
        # Set as target path
        state_manager.set_item('target_path', selected_file["path"])
        
        # Move to top of history
        file_history.add_target_file(selected_file["path"], selected_file["type"])
        
        # Update UI
        from facefusion.uis.components.target import update
        update({"name": selected_file["path"]})


def clear_history() -> Tuple[gradio.Gallery, gradio.Gallery]:
    """Clear file history"""
    file_history.clear_history()
    return gradio.Gallery(value=None), gradio.Gallery(value=None)
