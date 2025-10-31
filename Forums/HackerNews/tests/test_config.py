"""Tests for config module."""

import os
import tempfile
import pytest
from pathlib import Path
from src.core.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_initialization_with_defaults(self):
        """Test that Config initializes with default values."""
        config = Config(interactive=False)
        
        assert config.hn_api_base_url == "https://hacker-news.firebaseio.com/v0"
        assert config.hn_request_timeout == 10
        assert config.hn_frontpage_max_posts == 10
        assert config.hn_new_max_posts == 10
        assert config.hn_best_max_posts == 10
        assert config.hn_type_max_posts == 10
        assert config.database_url is not None
    
    def test_config_with_custom_env_file(self):
        """Test Config with custom environment file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("HN_FRONTPAGE_MAX_POSTS=20\n")
            f.write("HN_API_BASE_URL=https://test.api.com/v0\n")
            f.write("HN_REQUEST_TIMEOUT=15\n")
            env_file = f.name
        
        try:
            config = Config(env_file=env_file, interactive=False)
            assert config.hn_frontpage_max_posts == 20
            assert config.hn_api_base_url == "https://test.api.com/v0"
            assert config.hn_request_timeout == 15
        finally:
            os.unlink(env_file)
    
    def test_config_database_url(self):
        """Test that database URL is properly constructed."""
        config = Config(interactive=False)
        
        assert config.database_url.startswith("sqlite:///")
        assert config.database_path.endswith(".s3db")
    
    def test_config_working_directory(self):
        """Test that working directory is set."""
        config = Config(interactive=False)
        
        assert config.working_directory is not None
        assert isinstance(config.working_directory, str)
