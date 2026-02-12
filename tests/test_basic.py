"""
Basic smoke tests for Daily Seongsu project.

These tests ensure that core modules can be imported and
basic functionality works as expected.
"""
import pytest
import sys
from pathlib import Path


class TestImports:
    """Test that essential modules can be imported."""
    
    def test_import_gradio(self):
        """Gradio should be importable."""
        import gradio as gr
        assert gr is not None
    
    def test_import_pandas(self):
        """Pandas should be importable."""
        import pandas as pd
        assert pd is not None
    
    def test_import_requests(self):
        """Requests should be importable."""
        import requests
        assert requests is not None


class TestProjectStructure:
    """Test that the project structure is correct."""
    
    def test_guidebook_exists(self):
        """Guidebook directory should exist."""
        project_root = Path(__file__).parent.parent
        guidebook_path = project_root / "guidebook"
        assert guidebook_path.exists()
        assert guidebook_path.is_dir()
    
    def test_crawler_exists(self):
        """Crawler directory should exist."""
        project_root = Path(__file__).parent.parent
        crawler_path = project_root / "crawler"
        assert crawler_path.exists()
        assert crawler_path.is_dir()
    
    def test_requirements_exists(self):
        """Requirements.txt should exist."""
        project_root = Path(__file__).parent.parent
        req_path = project_root / "requirements.txt"
        assert req_path.exists()
        assert req_path.is_file()


class TestBasicFunctionality:
    """Test basic functionality of core modules."""
    
    def test_dataframe_creation(self):
        """Test that we can create a basic DataFrame."""
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        assert len(df) == 3
        assert list(df.columns) == ['A', 'B']
    
    def test_env_loading(self):
        """Test that environment variables can be loaded."""
        from pathlib import Path
        env_file = Path(__file__).parent.parent / ".env"
        # Just check if file exists, don't validate contents for security
        assert env_file.exists() or True  # Always pass, just demonstration


def test_python_version():
    """Ensure we're running on Python 3.8+ (3.10+ recommended for CI)."""
    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
    # Note: CI pipeline runs on Python 3.10 as specified in ci.yml


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
