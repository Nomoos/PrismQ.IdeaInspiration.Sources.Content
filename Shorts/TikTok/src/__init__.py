"""TikTok Source Module for PrismQ.IdeaInspiration.

This module provides tools for scraping TikTok content with comprehensive
metadata extraction and universal metrics collection.
"""

from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .core.idea_processor import IdeaProcessor
from .plugins import (
    SourcePlugin,
    TikTokTrendingPlugin,
    TikTokHashtagPlugin,
    TikTokCreatorPlugin,
)

__version__ = "1.0.0"

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "IdeaProcessor",
    "SourcePlugin",
    "TikTokTrendingPlugin",
    "TikTokHashtagPlugin",
    "TikTokCreatorPlugin",
]
