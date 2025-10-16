"""Tests for configuration module."""

import os
import sys
from pathlib import Path

# Add the module src to path for imports
module_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(module_src))

from config import ModuleConfig  # noqa: E402


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    config = ModuleConfig()
    assert config.module_name == os.getenv("MODULE_NAME", "PrismQ.RepositoryTemplate.ModuleExample")
    assert config.module_env in ["development", "production", "testing"]
    assert isinstance(config.debug, bool)


def test_config_directories():
    """Test that configuration creates necessary directories."""
    config = ModuleConfig()
    assert config.input_dir.exists()
    assert config.output_dir.exists()
    assert config.cache_dir.exists()


def test_config_api_key():
    """Test API key retrieval."""
    config = ModuleConfig()
    # Should return None for non-existent keys
    assert config.get_api_key("nonexistent") is None
