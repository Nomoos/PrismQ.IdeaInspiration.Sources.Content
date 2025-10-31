"""Kick Streamer clips plugin for scraping idea inspirations from streamer channels.

This plugin scrapes clips from specific Kick.com streamer channels using the unofficial API.
"""

import time
import cloudscraper
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class KickStreamerPlugin(SourcePlugin):
    """Plugin for scraping clips from Kick streamer channels."""
    
    # Kick API endpoints
    KICK_API_BASE = "https://kick.com/api/v2"
    KICK_CHANNELS_ENDPOINT = f"{KICK_API_BASE}/channels"
    
    def __init__(self, config, streamer_username: Optional[str] = None):
        """Initialize Kick streamer plugin.
        
        Args:
            config: Configuration object
            streamer_username: Streamer username to scrape
        """
        super().__init__(config)
        self.streamer_username = streamer_username
        # Use cloudscraper to bypass Cloudflare protection
        self.scraper = cloudscraper.create_scraper()
        self.request_delay = getattr(config, 'request_delay', 1.0)
        self.max_retries = getattr(config, 'max_retries', 3)
        self.request_timeout = getattr(config, 'request_timeout', 30)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "kick_streamer"
    
    def scrape(self, max_clips: Optional[int] = None, streamer_username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape clips from a specific streamer channel.
        
        Args:
            max_clips: Maximum number of clips to scrape (uses config if not provided)
            streamer_username: Streamer username to scrape (uses instance value if not provided)
            
        Returns:
            List of idea dictionaries
        """
        if max_clips is None:
            max_clips = getattr(self.config, 'kick_streamer_max_clips', 50)
        
        if streamer_username is None:
            streamer_username = self.streamer_username
        
        if not streamer_username:
            print("Error: No streamer username specified")
            return []
        
        print(f"Scraping Kick clips from streamer '{streamer_username}' (max: {max_clips})...")
        
        ideas = []
        page = 1
        per_page = 20
        
        while len(ideas) < max_clips:
            # Fetch clips from API
            clips = self._fetch_streamer_clips(streamer_username, page, per_page)
            
            if not clips:
                print(f"No more clips found on page {page}")
                break
            
            print(f"  Page {page}: Found {len(clips)} clips")
            
            # Process each clip
            for clip in clips:
                if len(ideas) >= max_clips:
                    break
                
                idea = self._clip_to_idea(clip, streamer_username)
                if idea:
                    ideas.append(idea)
            
            # Check if we have more pages
            if len(clips) < per_page:
                break
            
            page += 1
            time.sleep(self.request_delay)
        
        print(f"Successfully scraped {len(ideas)} clips from streamer '{streamer_username}'")
        return ideas
    
    def _fetch_streamer_clips(self, streamer_username: str, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """Fetch clips from a specific streamer.
        
        Args:
            streamer_username: Streamer username
            page: Page number
            per_page: Number of clips per page
            
        Returns:
            List of clip data dictionaries
        """
        url = f"{self.KICK_CHANNELS_ENDPOINT}/{streamer_username}/clips"
        params = {
            'page': page,
            'limit': per_page,
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.scraper.get(
                    url,
                    params=params,
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # API may return clips directly or in a 'data' field
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, dict) and 'clips' in data:
                        return data['clips']
                    return []
                elif response.status_code == 404:
                    # Streamer not found
                    print(f"  Streamer '{streamer_username}' not found")
                    return []
                else:
                    print(f"  Warning: API returned status {response.status_code}")
                    
            except Exception as e:
                print(f"  Error fetching clips (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.request_delay * 2)
        
        return []
    
    def _clip_to_idea(self, clip: Dict[str, Any], streamer_username: str) -> Optional[Dict[str, Any]]:
        """Convert Kick clip data to idea format.
        
        Args:
            clip: Clip data from API
            streamer_username: Streamer username
            
        Returns:
            Idea dictionary or None if invalid
        """
        try:
            # Extract clip ID
            clip_id = clip.get('id') or clip.get('clip_id')
            if not clip_id:
                return None
            
            # Extract basic info
            title = clip.get('title', 'Untitled Clip')
            
            # Build description
            description_parts = [f"Streamer: {streamer_username}"]
            if clip.get('category'):
                category_name = clip['category'].get('name') if isinstance(clip['category'], dict) else clip['category']
                description_parts.append(f"Category: {category_name}")
            
            description = " | ".join(description_parts)
            
            # Extract tags
            tags = [streamer_username]
            if clip.get('category'):
                category_name = clip['category'].get('name') if isinstance(clip['category'], dict) else clip['category']
                if category_name:
                    tags.append(category_name)
            
            # Extract metrics
            metrics = {
                'views': clip.get('views', 0),
                'likes': clip.get('likes', 0),
                'comments': 0,
                'shares': 0,
                'reactions': clip.get('likes', 0),
                'duration': clip.get('duration', 0),
                'created_at': clip.get('created_at', ''),
                'streamer_followers': 0,
                'streamer_verified': False,
            }
            
            # Extract streamer info
            if clip.get('channel'):
                channel = clip['channel']
                if isinstance(channel, dict):
                    metrics['streamer_followers'] = channel.get('followers_count', 0)
                    metrics['streamer_verified'] = channel.get('verified', False)
            
            # Build idea dictionary
            idea = {
                'source_id': str(clip_id),
                'title': title,
                'description': description,
                'tags': self.format_tags(tags),
                'metrics': metrics,
                'category': clip.get('category'),
                'streamer': {
                    'username': streamer_username,
                    'followers': metrics['streamer_followers'],
                    'verified': metrics['streamer_verified'],
                },
                'clip': {
                    'duration': clip.get('duration', 0),
                    'language': clip.get('language', 'en'),
                    'created_at': clip.get('created_at', ''),
                }
            }
            
            return idea
            
        except Exception as e:
            print(f"  Error converting clip to idea: {e}")
            return None
