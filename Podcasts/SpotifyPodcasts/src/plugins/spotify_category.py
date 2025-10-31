"""Spotify Category source plugin for scraping podcasts by category.

This plugin uses the Spotify Web API (via Spotipy) to scrape podcasts from
specific categories.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class SpotifyCategoryPlugin(SourcePlugin):
    """Plugin for scraping podcast episodes from specific categories on Spotify."""
    
    def __init__(self, config):
        """Initialize Spotify category plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if credentials are configured
        if not self.config.spotify_client_id or not self.config.spotify_client_secret:
            raise ValueError(
                "Spotify credentials not configured. "
                "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file. "
                "Get them from https://developer.spotify.com/dashboard"
            )
        
        # Initialize Spotify client
        self.sp = self._init_spotify_client()
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "spotify_category"
    
    def _init_spotify_client(self) -> spotipy.Spotify:
        """Initialize Spotify API client.
        
        Returns:
            Spotipy client instance
        """
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.config.spotify_client_id,
            client_secret=self.config.spotify_client_secret
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def scrape(self, category: str, top_n: Optional[int] = None, market: str = "US") -> List[Dict[str, Any]]:
        """Scrape podcast episodes from a specific category.
        
        Args:
            category: Category name (e.g., "business", "comedy", "true crime")
            top_n: Number of episodes to scrape (optional, uses config if not provided)
            market: Market/region code (default: "US")
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'spotify_category_max_episodes', 10)
        
        print(f"Scraping podcast episodes from category: {category}")
        
        try:
            # Search for shows in this category
            results = self.sp.search(
                q=f'"{category}"',
                type='show',
                market=market,
                limit=10  # Get top 10 shows
            )
            
            if results and 'shows' in results and results['shows']['items']:
                shows = results['shows']['items']
                episodes_per_show = max(1, top_n // len(shows))
                
                for show in shows:
                    # Get episodes from this show
                    show_id = show['id']
                    show_episodes = self.sp.show_episodes(
                        show_id,
                        market=market,
                        limit=episodes_per_show
                    )
                    
                    if show_episodes and 'items' in show_episodes:
                        for episode in show_episodes['items']:
                            # Enrich episode with show data
                            episode['show'] = {
                                'name': show['name'],
                                'publisher': show['publisher'],
                                'total_episodes': show.get('total_episodes', 0)
                            }
                            
                            idea = self._episode_to_idea(episode, category)
                            if idea:
                                ideas.append(idea)
                            
                            if len(ideas) >= top_n:
                                return ideas[:top_n]
        
        except Exception as e:
            print(f"Error scraping category '{category}': {e}")
        
        return ideas[:top_n]
    
    def _episode_to_idea(self, episode: Dict[str, Any], category: str = "") -> Optional[Dict[str, Any]]:
        """Convert Spotify episode data to idea format.
        
        Args:
            episode: Spotify episode data
            category: Category name
        
        Returns:
            Idea dictionary or None if conversion fails
        """
        try:
            # Extract basic information
            episode_id = episode.get('id')
            title = episode.get('name', 'Untitled Episode')
            description = episode.get('description', '')
            
            # Extract tags from show and episode
            tags = []
            
            if category:
                tags.append(category)
            
            if 'show' in episode:
                show = episode['show']
                tags.append(show.get('name', ''))
                tags.append(show.get('publisher', ''))
            
            # Build idea dictionary
            idea = {
                'source': 'spotify_podcasts',
                'source_id': episode_id,
                'title': title,
                'description': description,
                'tags': tags,
                'show': episode.get('show', {}),
                'metrics': {
                    'duration_ms': episode.get('duration_ms', 0),
                    'release_date': episode.get('release_date', ''),
                    'language': episode.get('language', ''),
                    'explicit': episode.get('explicit', False)
                },
                'universal_metrics': {
                    'engagement_estimate': 5.0  # Base estimate
                }
            }
            
            return idea
        
        except Exception as e:
            print(f"Error converting episode to idea: {e}")
            return None
