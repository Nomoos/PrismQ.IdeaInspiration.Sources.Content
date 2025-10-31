"""Instagram Reels Source Module for PrismQ.IdeaInspiration."""

from .core import Config, Database, UniversalMetrics, IdeaProcessor
from .plugins import SourcePlugin

__version__ = "1.0.0"

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "IdeaProcessor",
    "SourcePlugin",
]
