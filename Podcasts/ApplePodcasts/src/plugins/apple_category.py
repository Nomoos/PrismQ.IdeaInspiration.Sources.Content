"""Apple Podcasts Category plugin for scraping podcasts by category.

This plugin scrapes podcasts from specific categories using iTunes Search API.
"""

import requests
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class AppleCategoryPlugin(SourcePlugin):
    """Plugin for scraping podcasts from Apple Podcasts by category."""
    
    # iTunes Search API endpoints
    ITUNES_SEARCH_API = "https://itunes.apple.com/search"
    ITUNES_LOOKUP_API = "https://itunes.apple.com/lookup"
    
    def __init__(self, config):
        """Initialize Apple Category plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.region = getattr(config, 'apple_podcasts_region', 'us')
        self.max_shows = getattr(config, 'apple_podcasts_max_shows', 20)
        self.max_episodes = getattr(config, 'apple_podcasts_max_episodes', 10)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "apple_podcasts_category"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape podcasts from a specific category.
        
        Keyword Args:
            category: Category name (required)
            top_n: Number of shows to scrape
        
        Returns:
            List of idea dictionaries
        """
        category = kwargs.get('category')
        if not category:
            raise ValueError("Category is required")
        
        top_n = kwargs.get('top_n', self.max_shows)
        
        return self.scrape_category(category=category, top_n=top_n)
    
    def scrape_category(self, category: str, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape podcasts from a specific category.
        
        Args:
            category: Category name or ID
            top_n: Number of shows to scrape (default: config value)
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if top_n is None:
            top_n = self.max_shows
        
        print(f"Scraping Apple Podcasts category: {category} (region: {self.region})...")
        
        # Search for podcasts in the category
        podcasts = self._search_category(category=category, limit=top_n)
        
        if not podcasts:
            print(f"No podcasts found for category: {category}")
            return ideas
        
        print(f"Found {len(podcasts)} podcasts in category")
        
        # For each podcast, get episodes
        for i, podcast in enumerate(podcasts, 1):
            print(f"  [{i}/{len(podcasts)}] Processing: {podcast.get('collectionName', 'Unknown')}")
            
            collection_id = podcast.get('collectionId')
            if not collection_id:
                continue
            
            # Get episodes for this podcast
            episodes = self._get_podcast_episodes(collection_id, limit=self.max_episodes)
            
            # Convert episodes to idea format
            for episode in episodes:
                idea = self._episode_to_idea(episode, podcast)
                if idea:
                    ideas.append(idea)
        
        print(f"Total episodes scraped: {len(ideas)}")
        return ideas
    
    def _search_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for podcasts in a category using iTunes Search API.
        
        Args:
            category: Category name or term
            limit: Maximum number of results
            
        Returns:
            List of podcast dictionaries
        """
        params = {
            'term': category,
            'media': 'podcast',
            'entity': 'podcast',
            'country': self.region,
            'limit': min(limit, 200)  # iTunes API max is 200
        }
        
        try:
            response = requests.get(self.ITUNES_SEARCH_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('results', [])
        except requests.RequestException as e:
            print(f"Error searching category: {e}")
            return []
    
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
