"""Tests for ApplePodcasts config module."""

import pytest
import tempfile
import os
from pathlib import Path

from core.config import Config


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        env_path = f.name
    
    yield env_path
    
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_config_initialization_with_defaults(temp_env_file):
    """Test config initialization with default values."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert config.env_file == temp_env_file
    assert config.apple_podcasts_max_episodes == 10
    assert config.apple_podcasts_max_shows == 20
    assert config.apple_podcasts_region == 'us'


def test_config_database_url_default(temp_env_file):
    """Test default database URL configuration."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert config.database_url is not None
    assert config.database_url.startswith('sqlite:///')


def test_config_working_directory(temp_env_file):
    """Test working directory is set."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert config.working_directory is not None
    assert isinstance(config.working_directory, str)


def test_config_env_file_creation(temp_env_file):
    """Test that env file is created if it doesn't exist."""
    # Remove the temp file first
    os.unlink(temp_env_file)
    
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert os.path.exists(temp_env_file)


def test_config_max_episodes_parsing(temp_env_file):
    """Test that max episodes is parsed as integer."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert isinstance(config.apple_podcasts_max_episodes, int)
    assert config.apple_podcasts_max_episodes > 0


def test_config_max_shows_parsing(temp_env_file):
    """Test that max shows is parsed as integer."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert isinstance(config.apple_podcasts_max_shows, int)
    assert config.apple_podcasts_max_shows > 0


def test_config_region_default(temp_env_file):
    """Test default region is 'us'."""
    config = Config(env_file=temp_env_file, interactive=False)
    
    assert config.apple_podcasts_region == 'us'
