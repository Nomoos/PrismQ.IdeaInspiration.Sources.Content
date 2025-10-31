"""HackerNews Best Stories plugin for scraping algorithmically ranked posts."""

import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from . import SourcePlugin


class HNBestPlugin(SourcePlugin):
    """Plugin for scraping best stories from HackerNews.
    
    Uses HackerNews official Firebase API.
    Follows Open/Closed Principle (OCP) - open for extension, closed for modification.
    """
    
    def __init__(self, config):
        """Initialize HackerNews best stories plugin.
        
        Args:
            config: Configuration object with HN API settings
        """
        super().__init__(config)
        self.api_base_url = config.hn_api_base_url
        self.timeout = config.hn_request_timeout
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "hackernews_best"
    
    def _fetch_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single item from HackerNews API.
        
        Args:
            item_id: HackerNews item ID
            
        Returns:
            Item data dictionary or None if request fails
        """
        try:
            url = f"{self.api_base_url}/item/{item_id}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  ✗ Failed to fetch item {item_id}: {e}")
            return None
    
    def _item_to_idea(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert HackerNews item to idea format.
        
        Args:
            item: HackerNews item data
            
        Returns:
            Idea dictionary or None if item is invalid
        """
        if not item or item.get('deleted') or item.get('dead'):
            return None
        
        item_id = item.get('id')
        title = item.get('title', '')
        text = item.get('text', '')
        url = item.get('url', '')
        item_type = item.get('type', 'story')
        score = item.get('score', 0)
        descendants = item.get('descendants', 0)
        by = item.get('by', '')
        time = item.get('time', 0)
        
        # Build tags
        tags = [item_type, 'best']
        
        # Extract domain from URL if present
        if url:
            try:
                domain = urlparse(url).netloc
                if domain:
                    # Remove www. prefix
                    domain = domain.replace('www.', '')
                    tags.append(domain)
            except Exception:
                pass
        
        # Add type-specific tags
        if title.lower().startswith('ask hn'):
            tags.append('Ask HN')
        elif title.lower().startswith('show hn'):
            tags.append('Show HN')
        elif title.lower().startswith('tell hn'):
            tags.append('Tell HN')
        
        return {
            'source_id': str(item_id),
            'title': title,
            'description': text if text else '',
            'tags': self.format_tags(tags),
            'metrics': item  # Store full item data for metrics calculation
        }
    
    def scrape(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape best stories from HackerNews.
        
        Args:
            limit: Maximum number of stories to scrape (uses config if not provided)
            
        Returns:
            List of idea dictionaries
        """
        return self.scrape_beststories(limit=limit)
    
    def scrape_beststories(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape best stories from HackerNews.
        
        Args:
            limit: Maximum number of stories to scrape (uses config if not provided)
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.hn_best_max_posts
        
        print(f"Scraping {limit} best stories from HackerNews...")
        
        try:
            # Get best story IDs
            url = f"{self.api_base_url}/beststories.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            print(f"Found {len(story_ids)} story IDs")
            
            # Fetch each story
            for item_id in story_ids:
                item = self._fetch_item(item_id)
                if item:
                    idea = self._item_to_idea(item)
                    if idea:
                        ideas.append(idea)
                        score = item.get('score', 0)
                        print(f"  ✓ {item.get('title', '')[:60]}... (score: {score})")
            
            print(f"\nSuccessfully scraped {len(ideas)} best stories")
            
        except requests.RequestException as e:
            print(f"Error fetching best stories: {e}")
        
        return ideas
