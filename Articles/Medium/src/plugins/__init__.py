"""Base plugin interface for source scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Abstract base class for source scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all source plugins must implement.
    """

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape ideas from the source.
        
        Returns:
            List of idea dictionaries with keys:
                - source_id: Unique identifier from source
                - title: Idea title
                - description: Idea description
                - tags: Tags or categories
                - metrics: Dictionary of metrics for scoring
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'medium', 'medium_trending')
        """
        pass

    def format_tags(self, tags: List[str]) -> str:
        """Format a list of tags into a comma-separated string.
        
        Args:
            tags: List of tag strings
            
        Returns:
            Comma-separated tag string
        """
        return ",".join(tag.strip() for tag in tags if tag.strip())


# Export the base class and concrete implementations
from .medium_trending import MediumTrendingPlugin
from .medium_tag import MediumTagPlugin
from .medium_publication import MediumPublicationPlugin
from .medium_author import MediumAuthorPlugin

__all__ = [
    "SourcePlugin",
    "MediumTrendingPlugin",
    "MediumTagPlugin",
    "MediumPublicationPlugin",
    "MediumAuthorPlugin",
]
