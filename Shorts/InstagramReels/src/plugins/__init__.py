"""Base plugin interface for Instagram Reels source scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Abstract base class for Instagram Reels scraper plugins.
    
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
        """Scrape reels from Instagram.
        
        Returns:
            List of reel dictionaries with keys:
                - source_id: Unique identifier (reel ID)
                - title: Reel caption
                - description: Full caption with hashtags
                - tags: Tags or hashtags
                - metrics: Dictionary of metrics for scoring
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'instagram_reels_explore')
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


# Export the base class
__all__ = ["SourcePlugin"]
