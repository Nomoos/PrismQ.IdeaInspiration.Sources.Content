"""Tests for configuration management."""

import pytest
import os
import tempfile
from pathlib import Path
from src.core.config import Config


def test_config_initialization():
    """Test basic configuration initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(str(env_file), interactive=False)
        
        assert config.env_file == str(env_file)
        assert config.working_directory == tmpdir
        assert Path(env_file).exists()


def test_config_database_url():
    """Test database URL configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(str(env_file), interactive=False)
        
        # Should have a default database URL
        assert config.database_url is not None
        assert config.database_url.startswith("sqlite:///")


def test_config_spotify_credentials():
    """Test Spotify credential configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        
        # Write test credentials to env file
        with open(env_file, 'w') as f:
            f.write("SPOTIFY_CLIENT_ID=test_client_id\n")
            f.write("SPOTIFY_CLIENT_SECRET=test_secret\n")
        
        config = Config(str(env_file), interactive=False)
        
        assert config.spotify_client_id == "test_client_id"
        assert config.spotify_client_secret == "test_secret"


def test_config_defaults():
    """Test default configuration values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(str(env_file), interactive=False)
        
        # Test default values
        assert config.spotify_trending_max_episodes == 10
        assert config.spotify_category_max_episodes == 10
        assert config.spotify_show_max_episodes == 10
