"""PrismQ HackerNews Source - Collect idea inspirations from HackerNews."""

__version__ = '1.0.0'
__author__ = 'PrismQ'
__description__ = 'HackerNews source for PrismQ IdeaInspiration'

from .core import Config, Database, UniversalMetrics, IdeaProcessor
from .plugins import SourcePlugin

__all__ = [
    'Config',
    'Database',
    'UniversalMetrics',
    'IdeaProcessor',
    'SourcePlugin',
]
