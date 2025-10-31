"""Tests for Config class."""

import pytest
import os
from pathlib import Path
from src.core.config import Config


class TestConfig:
    """Test Config class."""
    
    def test_config_initialization_non_interactive(self, tmp_path):
        """Test config initialization in non-interactive mode."""
        env_file = tmp_path / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        
        assert config.env_file == str(env_file)
        assert config.database_path is not None
        assert config.instagram_max_reels > 0
    
    def test_config_default_values(self, tmp_path):
        """Test config default values."""
        env_file = tmp_path / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        
        assert config.instagram_max_reels == 50
        assert config.instagram_explore_max_reels == 50
        assert config.instagram_hashtag_max_reels == 50
        assert config.instagram_creator_max_reels == 50
        assert config.max_reel_duration == 90
    
    def test_config_creates_env_file(self, tmp_path):
        """Test that config creates .env file if it doesn't exist."""
        env_file = tmp_path / ".env"
        assert not env_file.exists()
        
        config = Config(env_file=str(env_file), interactive=False)
        
        assert env_file.exists()
