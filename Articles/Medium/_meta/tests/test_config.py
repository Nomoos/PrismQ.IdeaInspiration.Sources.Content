"""Tests for Medium source configuration."""

import pytest
import os
from pathlib import Path
from src.core.config import Config


def test_config_initialization():
    """Test that config initializes with defaults."""
    # Use non-interactive mode for testing
    config = Config(interactive=False)
    
    assert config is not None
    assert hasattr(config, 'database_url')
    assert hasattr(config, 'medium_trending_max_articles')
    assert hasattr(config, 'medium_tag_max_articles')


def test_config_default_values():
    """Test that config has sensible default values."""
    config = Config(interactive=False)
    
    # Check default article limits
    assert config.medium_trending_max_articles == 10
    assert config.medium_tag_max_articles == 10
    assert config.medium_author_max_articles == 10
    assert config.medium_publication_max_articles == 10
    
    # Check request settings
    assert config.request_timeout == 30
    assert config.request_delay >= 1.0


def test_config_database_url():
    """Test that database URL is properly set."""
    config = Config(interactive=False)
    
    # Should have a database URL
    assert config.database_url is not None
    assert 'sqlite:///' in config.database_url
    assert config.database_path is not None
