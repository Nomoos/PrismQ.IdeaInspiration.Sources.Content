"""Twitch Trending source plugin for scraping trending clips.

This plugin uses the Twitch Helix API to scrape trending clips,
providing comprehensive metadata extraction.
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from . import SourcePlugin


class TwitchTrendingPlugin(SourcePlugin):
    """Plugin for scraping trending clips from Twitch using Helix API."""
    
    # Twitch API endpoints
    OAUTH_URL = "https://id.twitch.tv/oauth2/token"
    CLIPS_URL = "https://api.twitch.tv/helix/clips"
    
    def __init__(self, config):
        """Initialize Twitch trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if credentials are configured
        if not self.config.twitch_client_id or not self.config.twitch_client_secret:
            raise ValueError(
                "Twitch credentials not configured. "
                "Please set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in your .env file. "
                "Get them from https://dev.twitch.tv/console/apps"
            )
        
        self.access_token = None
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "twitch_trending"
    
    def _get_access_token(self) -> str:
        """Get OAuth access token from Twitch.
        
        Returns:
            Access token
        """
        if self.access_token:
            return self.access_token
        
        # Request OAuth token
        response = requests.post(
            self.OAUTH_URL,
            params={
                'client_id': self.config.twitch_client_id,
                'client_secret': self.config.twitch_client_secret,
                'grant_type': 'client_credentials'
            }
        )
        
        if response.status_code != 200:
            raise ValueError(f"Failed to get Twitch access token: {response.text}")
        
        data = response.json()
        self.access_token = data['access_token']
        return self.access_token
    
    def _make_api_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated API request to Twitch.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Response JSON data
        """
        access_token = self._get_access_token()
        
        headers = {
            'Client-ID': self.config.twitch_client_id,
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise ValueError(f"API request failed: {response.text}")
        
        return response.json()
    
    def scrape(self, top_n: Optional[int] = None, started_at: Optional[str] = None,
               ended_at: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape trending clips from Twitch.
        
        Args:
            top_n: Number of clips to scrape (optional, uses config if not provided)
            started_at: Start date for clip range (RFC3339 format)
            ended_at: End date for clip range (RFC3339 format)
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'twitch_trending_max_clips', 10)
        
        # Default to last 24 hours if no date range provided
        if not started_at:
            # Twitch API requires started_at to be within the last 7 days
            started_at = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
        
        print(f"Scraping {top_n} trending Twitch clips...")
        
        # Get trending clips (sorted by view count by default)
        clips = self._get_clips(first=top_n, started_at=started_at, ended_at=ended_at)
        
        if not clips:
            print("No clips found")
            return ideas
        
        print(f"Found {len(clips)} clips")
        
        # Convert clips to idea format
        for i, clip in enumerate(clips, 1):
            print(f"  [{i}/{len(clips)}] Processing: {clip.get('title', 'Untitled')}")
            
            idea = self._convert_clip_to_idea(clip)
            if idea:
                ideas.append(idea)
        
        return ideas
    
    def _get_clips(self, first: int = 20, started_at: Optional[str] = None,
                   ended_at: Optional[str] = None, game_id: Optional[str] = None,
                   broadcaster_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get clips from Twitch API.
        
        Args:
            first: Number of clips to retrieve (max 100)
            started_at: Start date (RFC3339)
            ended_at: End date (RFC3339)
            game_id: Filter by game ID
            broadcaster_id: Filter by broadcaster ID
            
        Returns:
            List of clip data dictionaries
        """
        params = {
            'first': min(first, 100)  # Twitch max is 100
        }
        
        if started_at:
            params['started_at'] = started_at
        if ended_at:
            params['ended_at'] = ended_at
        if game_id:
            params['game_id'] = game_id
        if broadcaster_id:
            params['broadcaster_id'] = broadcaster_id
        
        try:
            data = self._make_api_request(self.CLIPS_URL, params)
            return data.get('data', [])
        except Exception as e:
            print(f"Error fetching clips: {e}")
            return []
    
    def _convert_clip_to_idea(self, clip: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Twitch clip data to idea format.
        
        Args:
            clip: Clip data from Twitch API
            
        Returns:
            Idea dictionary or None if conversion fails
        """
        try:
            # Extract basic information
            clip_id = clip.get('id', '')
            title = clip.get('title', 'Untitled Clip')
            
            # Build tags from game, broadcaster, and category
            tags = []
            game_name = clip.get('game_name')
            if game_name:
                tags.append(game_name)
            
            broadcaster_name = clip.get('broadcaster_name')
            if broadcaster_name:
                tags.append(broadcaster_name)
            
            tags.extend(['twitch', 'clip', 'gaming'])
            
            # Build description
            description = f"Twitch clip from {broadcaster_name}'s stream"
            if game_name:
                description += f" of {game_name}"
            
            creator_name = clip.get('creator_name')
            if creator_name:
                description += f", clipped by {creator_name}"
            
            # Build metrics dictionary
            metrics = {
                'view_count': clip.get('view_count', 0),
                'duration': clip.get('duration', 0),
                'created_at': clip.get('created_at', ''),
                'broadcaster_name': broadcaster_name,
                'game_name': game_name,
                'language': clip.get('language', 'en'),
            }
            
            # Add VOD offset if available
            vod_offset = clip.get('vod_offset')
            if vod_offset is not None:
                metrics['vod_offset'] = vod_offset
            
            return {
                'source_id': clip_id,
                'title': title,
                'description': description,
                'tags': self.format_tags(tags),
                'metrics': metrics,
                'raw_data': clip  # Store raw clip data for reference
            }
        except Exception as e:
            print(f"Error converting clip to idea: {e}")
            return None
