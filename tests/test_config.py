"""Tests for configuration module."""

import os

from src.config import Config


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    config = Config()
    assert config.app_name == os.getenv("APP_NAME", "PrismQ.ModuleName")
    assert config.app_env in ["development", "production", "testing"]
    assert isinstance(config.debug, bool)


def test_config_directories():
    """Test that configuration creates necessary directories."""
    config = Config()
    assert config.input_dir.exists()
    assert config.output_dir.exists()
    assert config.cache_dir.exists()


def test_config_api_key():
    """Test API key retrieval."""
    config = Config()
    # Should return None for non-existent keys
    assert config.get_api_key("nonexistent") is None


def test_config_python_executable():
    """Test Python executable configuration."""
    config = Config()
    # Should have a default value
    assert config.python_executable is not None
    assert isinstance(config.python_executable, str)
    # Default should be "python"
    assert config.python_executable == os.getenv("PYTHON_EXECUTABLE", "python")
