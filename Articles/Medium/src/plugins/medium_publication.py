"""Medium Publication plugin for scraping articles from publications.

This plugin scrapes articles from specific Medium publications.
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from . import SourcePlugin
from .medium_trending import MediumTrendingPlugin


class MediumPublicationPlugin(SourcePlugin):
    """Plugin for scraping articles from Medium publications."""
    
    def __init__(self, config):
        """Initialize Medium publication plugin.
        
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
        return "medium_publication"
    
    def scrape(self, publication: Optional[str] = None, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape articles from a Medium publication.
        
        Args:
            publication: Publication name or URL (required)
            top_n: Number of articles to scrape (optional, uses config if not provided)
        
        Returns:
            List of idea dictionaries
        """
        if not publication:
            print("Error: Publication is required for publication-based scraping")
            return []
        
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'medium_publication_max_articles', 10)
        
        print(f"Scraping Medium articles from publication: '{publication}'...")
        
        try:
            # Build publication URL
            if publication.startswith('http'):
                url = publication
            else:
                # Assume it's a publication name
                url = f"https://medium.com/{publication}"
            
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
                    # Add publication to article data
                    article_data['publication'] = publication
                    ideas.append(article_data)
            
            print(f"Successfully scraped {len(ideas)} articles from publication '{publication}'")
            
        except requests.RequestException as e:
            print(f"Error scraping Medium publication '{publication}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return ideas
