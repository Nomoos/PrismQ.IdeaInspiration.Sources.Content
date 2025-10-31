"""Base plugin interface for Reddit source scrapers."""

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
                - source_id: Reddit post ID
                - title: Post title
                - description: Post selftext
                - tags: Comma-separated tags (subreddit, flair, keywords)
                - metrics: Dictionary of metrics for scoring
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'reddit_trending', 'reddit_subreddit')
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


# Will be imported after concrete implementations are defined
__all__ = ["SourcePlugin"]
