"""Base plugin interface for article scraper plugins."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Abstract base class for article scraper plugins.
    
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
        """Scrape articles from the source.
        
        Returns:
            List of article dictionaries with keys:
                - source_id: Unique identifier from source
                - title: Article title
                - description: Article description/summary
                - tags: Tags or categories
                - metrics: Dictionary of metrics for scoring
                - content: Full article text
                - author: Author information
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'web_article', 'web_rss')
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
from .article_url import ArticleUrlPlugin
from .article_rss import ArticleRssPlugin
from .article_sitemap import ArticleSitemapPlugin

__all__ = [
    "SourcePlugin",
    "ArticleUrlPlugin",
    "ArticleRssPlugin",
    "ArticleSitemapPlugin",
]
