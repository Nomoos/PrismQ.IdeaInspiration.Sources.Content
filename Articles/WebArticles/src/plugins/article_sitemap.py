"""Article Sitemap source plugin for scraping articles from XML sitemaps.

This plugin parses XML sitemaps to discover article URLs, then uses 
ArticleUrlPlugin to extract full content from each URL.
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin


class ArticleSitemapPlugin(SourcePlugin):
    """Plugin for scraping articles from XML sitemaps."""
    
    def __init__(self, config):
        """Initialize article sitemap plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Import ArticleUrlPlugin for content extraction
        from .article_url import ArticleUrlPlugin
        self.url_plugin = ArticleUrlPlugin(config)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "web_article_sitemap"
    
    def scrape(self, sitemap_urls: Optional[List[str]] = None, max_articles: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape articles from XML sitemaps.
        
        Args:
            sitemap_urls: List of XML sitemap URLs
            max_articles: Maximum articles to scrape per sitemap (uses config if not provided)
        
        Returns:
            List of article dictionaries
        """
        if not sitemap_urls:
            print("No sitemap URLs provided")
            return []
        
        if max_articles is None:
            max_articles = getattr(self.config, 'web_article_max_articles', 10)
        
        all_articles = []
        
        for i, sitemap_url in enumerate(sitemap_urls, 1):
            print(f"  [{i}/{len(sitemap_urls)}] Parsing sitemap: {sitemap_url}")
            
            try:
                article_urls = self._parse_sitemap(sitemap_url, max_articles)
                print(f"    ✓ Found {len(article_urls)} article URLs")
                
                # Extract content from each URL
                articles = self.url_plugin.scrape(article_urls)
                all_articles.extend(articles)
                
            except Exception as e:
                print(f"    ✗ Error parsing sitemap: {e}")
        
        return all_articles
    
    def _parse_sitemap(self, sitemap_url: str, max_articles: int) -> List[str]:
        """Parse XML sitemap and extract article URLs.
        
        Args:
            sitemap_url: XML sitemap URL
            max_articles: Maximum URLs to extract
            
        Returns:
            List of article URLs
        """
        import requests
        import xml.etree.ElementTree as ET
        
        # Fetch sitemap
        timeout = getattr(self.config, 'web_article_timeout', 30)
        user_agent = getattr(self.config, 'user_agent', 'Mozilla/5.0')
        
        headers = {'User-Agent': user_agent}
        response = requests.get(sitemap_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Handle namespaces
        namespaces = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'news': 'http://www.google.com/schemas/sitemap-news/0.9'
        }
        
        urls = []
        
        # Check if this is a sitemap index (contains other sitemaps)
        sitemap_elements = root.findall('.//sm:sitemap', namespaces)
        if sitemap_elements:
            # This is a sitemap index, recursively parse child sitemaps
            for sitemap_elem in sitemap_elements[:max_articles]:
                loc_elem = sitemap_elem.find('sm:loc', namespaces)
                if loc_elem is not None and loc_elem.text:
                    child_urls = self._parse_sitemap(loc_elem.text, max_articles)
                    urls.extend(child_urls)
                    if len(urls) >= max_articles:
                        break
        else:
            # This is a regular sitemap with URLs
            url_elements = root.findall('.//sm:url', namespaces)
            for url_elem in url_elements[:max_articles]:
                loc_elem = url_elem.find('sm:loc', namespaces)
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text)
        
        return urls[:max_articles]
