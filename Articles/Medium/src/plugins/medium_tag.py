"""Medium Tag-based plugin for scraping articles by tag.

This plugin scrapes articles from specific tags on Medium.com.
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from . import SourcePlugin
from .medium_trending import MediumTrendingPlugin


class MediumTagPlugin(SourcePlugin):
    """Plugin for scraping articles by tag from Medium."""
    
    def __init__(self, config):
        """Initialize Medium tag plugin.
        
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
        return "medium_tag"
    
    def scrape(self, tag: Optional[str] = None, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape articles by tag from Medium.
        
        Args:
            tag: Tag to search for (required)
            top_n: Number of articles to scrape (optional, uses config if not provided)
        
        Returns:
            List of idea dictionaries
        """
        if not tag:
            print("Error: Tag is required for tag-based scraping")
            return []
        
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'medium_tag_max_articles', 10)
        
        print(f"Scraping Medium articles for tag: '{tag}'...")
        
        try:
            # Fetch Medium tag page
            tag_slug = tag.lower().replace(' ', '-')
            url = f"https://medium.com/tag/{tag_slug}"
            
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
                    # Add tag to article data
                    existing_tags = article_data.get('tags', '').split(',')
                    if tag not in existing_tags:
                        existing_tags.append(tag)
                    article_data['tags'] = self.format_tags(existing_tags)
                    ideas.append(article_data)
            
            print(f"Successfully scraped {len(ideas)} articles for tag '{tag}'")
            
        except requests.RequestException as e:
            print(f"Error scraping Medium tag '{tag}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return ideas
