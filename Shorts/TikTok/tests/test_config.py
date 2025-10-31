"""Tests for Config class."""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_initialization(self):
        """Test that Config can be initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            assert config is not None
            assert config.env_file == str(env_file)
            assert config.working_directory == tmpdir
    
    def test_config_database_path(self):
        """Test database path configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            assert config.database_path is not None
            assert "tiktok.s3db" in config.database_path
    
    def test_config_tiktok_settings(self):
        """Test TikTok-specific configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            assert hasattr(config, 'tiktok_trending_max')
            assert hasattr(config, 'tiktok_hashtag_max')
            assert hasattr(config, 'tiktok_creator_max')
            assert hasattr(config, 'tiktok_rate_limit_delay')
            
            # Default values
            assert config.tiktok_trending_max == 10
            assert config.tiktok_hashtag_max == 10
            assert config.tiktok_creator_max == 10
            assert config.tiktok_rate_limit_delay == 2.0
