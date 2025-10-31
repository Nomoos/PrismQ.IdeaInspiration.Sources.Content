"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path
import pytest
from src.core.config import Config


def test_config_initialization():
    """Test basic configuration initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        
        assert config.env_file == str(env_file)
        assert config.working_directory
        assert config.database_url
        assert config.web_article_max_articles == 10
        assert config.web_article_timeout == 30


def test_config_default_values():
    """Test that configuration has sensible defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        
        assert config.web_article_max_articles > 0
        assert config.web_article_timeout > 0
        assert config.user_agent
