import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""
    return {
        "max_file_size": 10 * 1024 * 1024,  # 10MB for tests
        "supported_formats": [".pdf", ".jpg", ".jpeg", ".png", ".tiff"],
        "temp_storage": True,
    }


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test"""
    yield
    
    # Clean up temp and output directories
    temp_dirs = ["temp", "output"]
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            import shutil
            try:
                shutil.rmtree(dir_name)
            except (PermissionError, OSError):
                pass  # May be in use, ignore
            
            # Recreate empty directories
            os.makedirs(dir_name, exist_ok=True)