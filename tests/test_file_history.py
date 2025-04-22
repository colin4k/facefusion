import os
import tempfile

import pytest

from facefusion import file_history, state_manager

@pytest.fixture(scope = 'module', autouse = True)
def before_all() -> None:
    state_manager.init_item('temp_path', tempfile.gettempdir())

def test_get_history_file_path() -> None:
    history_file_path = file_history.get_history_file_path()
    assert history_file_path.endswith('file_history.json')
    assert 'facefusion' in history_file_path
    assert 'history' in history_file_path

def test_load_save_history() -> None:
    # Test with empty history
    file_history.clear_history()
    history = file_history.load_history()
    assert 'source_files' in history
    assert 'target_files' in history
    assert len(history['source_files']) == 0
    assert len(history['target_files']) == 0
    
    # Test saving and loading history
    test_history = {
        'source_files': [
            {'path': '/test/path1.jpg', 'type': 'image', 'timestamp': 123456789}
        ],
        'target_files': [
            {'path': '/test/path2.mp4', 'type': 'video', 'timestamp': 987654321}
        ]
    }
    file_history.save_history(test_history)
    loaded_history = file_history.load_history()
    assert loaded_history == test_history
    
    # Clean up
    file_history.clear_history()

def test_add_source_file() -> None:
    # Clear history first
    file_history.clear_history()
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.close()
    
    try:
        # Add file to history
        file_history.add_source_file(temp_file.name, 'image')
        
        # Check if file was added
        history = file_history.load_history()
        assert len(history['source_files']) == 1
        assert history['source_files'][0]['path'] == temp_file.name
        assert history['source_files'][0]['type'] == 'image'
        
        # Add same file again (should not duplicate)
        file_history.add_source_file(temp_file.name, 'image')
        history = file_history.load_history()
        assert len(history['source_files']) == 1
        
        # Clean up
        file_history.clear_history()
    finally:
        # Remove temporary file
        os.unlink(temp_file.name)

def test_add_target_file() -> None:
    # Clear history first
    file_history.clear_history()
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()
    
    try:
        # Add file to history
        file_history.add_target_file(temp_file.name, 'video')
        
        # Check if file was added
        history = file_history.load_history()
        assert len(history['target_files']) == 1
        assert history['target_files'][0]['path'] == temp_file.name
        assert history['target_files'][0]['type'] == 'video'
        
        # Add same file again (should not duplicate)
        file_history.add_target_file(temp_file.name, 'video')
        history = file_history.load_history()
        assert len(history['target_files']) == 1
        
        # Clean up
        file_history.clear_history()
    finally:
        # Remove temporary file
        os.unlink(temp_file.name)

def test_history_limit() -> None:
    # Clear history first
    file_history.clear_history()
    
    # Add more than the limit (20) files
    for i in range(25):
        fake_path = f'/test/path{i}.jpg'
        history = file_history.load_history()
        history['source_files'].append({
            'path': fake_path,
            'type': 'image',
            'timestamp': i
        })
    
    file_history.save_history(history)
    
    # Check if history is limited to 20 items
    history = file_history.load_history()
    assert len(history['source_files']) == 25  # We manually added 25
    
    # Now add one more through the function which should enforce the limit
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.close()
    
    try:
        file_history.add_source_file(temp_file.name, 'image')
        history = file_history.load_history()
        assert len(history['source_files']) == 20  # Should be limited to 20
        assert history['source_files'][0]['path'] == temp_file.name  # New file should be first
        
        # Clean up
        file_history.clear_history()
    finally:
        # Remove temporary file
        os.unlink(temp_file.name)
