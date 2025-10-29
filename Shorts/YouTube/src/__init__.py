"""YouTube Shorts Source - Scraping and processing YouTube Shorts content.

This module provides tools for collecting idea inspirations from YouTube Shorts
with comprehensive metadata extraction and universal metrics collection.
"""

__version__ = "1.0.0"

# Core modules
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .core.idea_processor import IdeaProcessor

# Plugins
from .plugins.youtube_plugin import YouTubePlugin
from .plugins.youtube_channel_plugin import YouTubeChannelPlugin
from .plugins.youtube_trending_plugin import YouTubeTrendingPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "IdeaProcessor",
    "YouTubePlugin",
    "YouTubeChannelPlugin",
    "YouTubeTrendingPlugin",
]
