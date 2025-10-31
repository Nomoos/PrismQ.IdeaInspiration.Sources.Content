"""Medium Author plugin for scraping articles by author.

This plugin scrapes articles from specific Medium authors.
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from . import SourcePlugin
from .medium_trending import MediumTrendingPlugin


class MediumAuthorPlugin(SourcePlugin):
    """Plugin for scraping articles by author from Medium."""
    
    def __init__(self, config):
        """Initialize Medium author plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Reuse trending plugin's scraping logic
        self._trending_plugin = MediumTrendingPlugin(config)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "medium_author"
    
    def scrape(self, author: Optional[str] = None, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape articles by author from Medium.
        
        Args:
            author: Author username (with or without @) or profile URL (required)
            top_n: Number of articles to scrape (optional, uses config if not provided)
        
        Returns:
            List of idea dictionaries
        """
        if not author:
            print("Error: Author is required for author-based scraping")
            return []
        
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'medium_author_max_articles', 10)
        
        print(f"Scraping Medium articles from author: '{author}'...")
        
        try:
            # Build author URL
            if author.startswith('http'):
                url = author
            else:
                # Ensure @ prefix
                if not author.startswith('@'):
                    author = f'@{author}'
                url = f"https://medium.com/{author}"
            
            response = self._trending_plugin.session.get(url, timeout=self._trending_plugin.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract article links
            article_links = self._trending_plugin._extract_article_links(soup, top_n)
            
            # Scrape each article
            for i, article_url in enumerate(article_links, 1):
                print(f"  [{i}/{len(article_links)}] Scraping: {article_url}")
                
                # Add delay between requests
                if i > 1:
                    time.sleep(self._trending_plugin.delay)
                
                article_data = self._trending_plugin._scrape_article(article_url)
                if article_data:
                    # Ensure author is set
                    if not article_data.get('author', {}).get('username'):
                        article_data['author'] = {'username': author.lstrip('@'), 'followers': None}
                    ideas.append(article_data)
            
            print(f"Successfully scraped {len(ideas)} articles from author '{author}'")
            
        except requests.RequestException as e:
            print(f"Error scraping Medium author '{author}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return ideas
