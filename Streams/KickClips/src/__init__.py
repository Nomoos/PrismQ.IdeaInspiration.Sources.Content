"""KickClips source module for PrismQ.IdeaInspiration."""

from .core import (
    Config,
    Database,
    UniversalMetrics,
    IdeaProcessor,
    IdeaInspiration,
    ContentType,
)
from .plugins import (
    SourcePlugin,
    KickTrendingPlugin,
    KickCategoryPlugin,
    KickStreamerPlugin,
)

__version__ = "1.0.0"

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "IdeaProcessor",
    "IdeaInspiration",
    "ContentType",
    "SourcePlugin",
    "KickTrendingPlugin",
    "KickCategoryPlugin",
    "KickStreamerPlugin",
]
