"""Apple Podcasts Show plugin for scraping episodes from specific shows.

This plugin scrapes episodes from specific podcast shows using iTunes Search API.
"""

import requests
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class AppleShowPlugin(SourcePlugin):
    """Plugin for scraping episodes from specific Apple Podcasts shows."""
    
    # iTunes Search API endpoints
    ITUNES_SEARCH_API = "https://itunes.apple.com/search"
    ITUNES_LOOKUP_API = "https://itunes.apple.com/lookup"
    
    def __init__(self, config):
        """Initialize Apple Show plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.region = getattr(config, 'apple_podcasts_region', 'us')
        self.max_episodes = getattr(config, 'apple_podcasts_max_episodes', 10)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "apple_podcasts_show"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape episodes from a specific podcast show.
        
        Keyword Args:
            show_id: iTunes collection ID (int) or show name (str)
            top_n: Number of episodes to scrape
        
        Returns:
            List of idea dictionaries
        """
        show_id = kwargs.get('show_id')
        if not show_id:
            raise ValueError("show_id is required")
        
        top_n = kwargs.get('top_n', self.max_episodes)
        
        return self.scrape_show(show_id=show_id, top_n=top_n)
    
    def scrape_show(self, show_id, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape episodes from a specific podcast show.
        
        Args:
            show_id: iTunes collection ID (int) or show name (str)
            top_n: Number of episodes to scrape (default: config value)
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if top_n is None:
            top_n = self.max_episodes
        
        # If show_id is a string, search for the show first
        if isinstance(show_id, str):
            print(f"Searching for podcast show: {show_id}")
            podcast = self._search_show(show_id)
            if not podcast:
                print(f"Show not found: {show_id}")
                return ideas
            collection_id = podcast.get('collectionId')
        else:
            collection_id = show_id
            # Lookup the show to get metadata
            podcast = self._lookup_show(collection_id)
        
        if not collection_id:
            print(f"Invalid show ID: {show_id}")
            return ideas
        
        show_name = podcast.get('collectionName', str(show_id))
        print(f"Scraping episodes from: {show_name} (ID: {collection_id})")
        
        # Get episodes for this podcast
        episodes = self._get_podcast_episodes(collection_id, limit=top_n)
        
        if not episodes:
            print(f"No episodes found for show: {show_name}")
            return ideas
        
        print(f"Found {len(episodes)} episodes")
        
        # Convert episodes to idea format
        for i, episode in enumerate(episodes, 1):
            print(f"  [{i}/{len(episodes)}] Processing: {episode.get('trackName', 'Unknown')}")
            idea = self._episode_to_idea(episode, podcast)
            if idea:
                ideas.append(idea)
        
        print(f"Total episodes scraped: {len(ideas)}")
        return ideas
    
    def _search_show(self, show_name: str) -> Optional[Dict[str, Any]]:
        """Search for a podcast show by name.
        
        Args:
            show_name: Podcast show name
            
        Returns:
            Podcast dictionary or None
        """
        params = {
            'term': show_name,
            'media': 'podcast',
            'entity': 'podcast',
            'country': self.region,
            'limit': 1
        }
        
        try:
            response = requests.get(self.ITUNES_SEARCH_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            return results[0] if results else None
        except requests.RequestException as e:
            print(f"Error searching for show: {e}")
            return None
    
    def _lookup_show(self, collection_id: int) -> Optional[Dict[str, Any]]:
        """Lookup a podcast show by collection ID.
        
        Args:
            collection_id: iTunes collection ID
            
        Returns:
            Podcast dictionary or None
        """
        params = {
            'id': collection_id,
            'entity': 'podcast'
        }
        
        try:
            response = requests.get(self.ITUNES_LOOKUP_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            # First result should be the podcast
            podcasts = [r for r in results if r.get('kind') == 'podcast']
            return podcasts[0] if podcasts else None
        except requests.RequestException as e:
            print(f"Error looking up show: {e}")
            return None
    
    def _get_podcast_episodes(self, collection_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get episodes for a specific podcast.
        
        Args:
            collection_id: iTunes collection ID
            limit: Maximum number of episodes
            
        Returns:
            List of episode dictionaries
        """
        params = {
            'id': collection_id,
            'entity': 'podcastEpisode',
            'limit': min(limit, 200)
        }
        
        try:
            response = requests.get(self.ITUNES_LOOKUP_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            # First result is usually the podcast itself, rest are episodes
            episodes = [r for r in results if r.get('kind') == 'podcast-episode']
            
            return episodes[:limit]
        except requests.RequestException as e:
            print(f"Error getting episodes for collection {collection_id}: {e}")
            return []
    
    def _episode_to_idea(self, episode: Dict[str, Any], podcast: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert episode data to idea format.
        
        Args:
            episode: Episode data from iTunes API
            podcast: Podcast data from iTunes API
            
        Returns:
            Idea dictionary or None
        """
        # Extract basic information
        track_id = episode.get('trackId')
        if not track_id:
            return None
        
        title = episode.get('trackName', '')
        description = episode.get('description', '') or episode.get('shortDescription', '')
        
        # Extract metrics
        metrics = {
            'rating': podcast.get('averageUserRating'),
            'rating_count': podcast.get('userRatingCount'),
            'duration_ms': episode.get('trackTimeMillis'),
            'release_date': episode.get('releaseDate'),
            'show': {
                'name': podcast.get('collectionName'),
                'artist': podcast.get('artistName'),
                'rating': podcast.get('averageUserRating')
            },
            'genres': episode.get('genres', []),
            'country': episode.get('country', self.region),
            'platform_specific': {
                'track_id': track_id,
                'collection_id': podcast.get('collectionId'),
                'artist_id': podcast.get('artistId'),
                'feed_url': episode.get('feedUrl') or podcast.get('feedUrl'),
                'artwork_url': episode.get('artworkUrl600') or podcast.get('artworkUrl600'),
            }
        }
        
        # Extract tags from genres and categories
        tags = []
        if episode.get('genres'):
            tags.extend(episode['genres'])
        if podcast.get('collectionName'):
            tags.append(podcast['collectionName'])
        
        return {
            'source': 'apple_podcasts',
            'source_id': str(track_id),
            'title': title,
            'description': description,
            'tags': tags,
            'metrics': metrics
        }
