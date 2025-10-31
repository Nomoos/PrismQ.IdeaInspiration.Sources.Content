"""Universal metrics schema for podcast content analysis.

This module defines a standardized metrics structure for podcast episodes
across different platforms: Apple Podcasts, Spotify, etc.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class UniversalMetrics:
    """Universal metrics schema for cross-platform podcast analysis.
    
    This schema standardizes metrics across different podcast platforms to enable
    consistent analysis and comparison.
    """
    
    # === Core Engagement Metrics ===
    rating: Optional[float] = None  # Average rating (e.g., 4.8/5.0)
    rating_count: Optional[int] = None  # Number of ratings
    review_count: Optional[int] = None  # Number of reviews
    
    # === Content Metadata ===
    duration_ms: Optional[int] = None  # Episode duration in milliseconds
    duration_seconds: Optional[int] = None  # Episode duration in seconds
    release_date: Optional[str] = None  # ISO format release date
    
    # === Episode Information ===
    episode_number: Optional[int] = None  # Episode number in series
    season_number: Optional[int] = None  # Season number
    episode_type: Optional[str] = None  # full, trailer, bonus
    
    # === Show Metrics ===
    show_name: Optional[str] = None  # Podcast show name
    show_artist: Optional[str] = None  # Creator/artist name
    show_rating: Optional[float] = None  # Show average rating
    show_rating_count: Optional[int] = None  # Show rating count
    
    # === Quality Indicators ===
    has_transcript: bool = False  # Transcript availability
    explicit_content: bool = False  # Explicit content flag
    
    # === Platform Context ===
    platform: str = "unknown"  # apple_podcasts, spotify, etc.
    content_type: str = "audio"  # audio (default for podcasts)
    
    # === Categories and Tags ===
    categories: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    
    # === Additional Context ===
    language: Optional[str] = None  # Episode language
    country: Optional[str] = None  # Country/region
    
    # === Calculated Metrics ===
    engagement_estimate: Optional[float] = None  # Calculated engagement score
    
    # === Raw Platform Data ===
    # Store platform-specific data that doesn't fit standard schema
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_engagement_estimate(self):
        """Calculate engagement estimate from available metrics.
        
        For podcasts, we primarily use ratings as the engagement indicator.
        Engagement estimate = (rating / 5.0) * 100 to normalize to 0-100 scale.
        """
        if self.rating and self.rating > 0:
            # Normalize rating to 0-100 scale
            self.engagement_estimate = (self.rating / 5.0) * 100
        elif self.show_rating and self.show_rating > 0:
            # Fallback to show rating if episode rating not available
            self.engagement_estimate = (self.show_rating / 5.0) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_apple_podcasts(cls, episode_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Apple Podcasts episode data.
        
        Args:
            episode_data: Episode data from iTunes Search API or podcast index
        """
        # Extract show information
        show_info = episode_data.get('show', {})
        
        # Calculate duration in both formats
        duration_ms = episode_data.get('duration_ms') or episode_data.get('trackTimeMillis')
        duration_seconds = None
        if duration_ms:
            duration_seconds = duration_ms // 1000
        
        metrics = cls(
            platform="apple_podcasts",
            content_type="audio",
            
            # Episode metrics
            rating=episode_data.get('rating'),
            rating_count=episode_data.get('rating_count'),
            review_count=episode_data.get('review_count'),
            
            # Duration
            duration_ms=duration_ms,
            duration_seconds=duration_seconds,
            
            # Release date
            release_date=episode_data.get('release_date') or episode_data.get('releaseDate'),
            
            # Episode details
            episode_number=episode_data.get('episode_number'),
            season_number=episode_data.get('season_number'),
            episode_type=episode_data.get('episode_type'),
            
            # Show information
            show_name=show_info.get('name') or episode_data.get('collectionName'),
            show_artist=show_info.get('artist') or episode_data.get('artistName'),
            show_rating=show_info.get('rating'),
            show_rating_count=show_info.get('rating_count'),
            
            # Quality indicators
            explicit_content=episode_data.get('contentAdvisoryRating') == 'Explicit',
            
            # Categories
            categories=episode_data.get('genres', []) or [],
            
            # Language and country
            language=episode_data.get('language'),
            country=episode_data.get('country'),
            
            # Store full data for reference
            platform_specific={
                'track_id': episode_data.get('trackId'),
                'collection_id': episode_data.get('collectionId'),
                'artist_id': episode_data.get('artistId'),
                'feed_url': episode_data.get('feedUrl'),
                'artwork_url': episode_data.get('artworkUrl600') or episode_data.get('artworkUrl100'),
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_engagement_estimate()
        
        return metrics
    
    @classmethod
    def from_spotify(cls, episode_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Spotify podcast episode data.
        
        Args:
            episode_data: Episode data from Spotify API
        """
        # Extract show information
        show_info = episode_data.get('show', {})
        
        metrics = cls(
            platform="spotify",
            content_type="audio",
            
            # Duration
            duration_ms=episode_data.get('duration_ms'),
            duration_seconds=episode_data.get('duration_ms') // 1000 if episode_data.get('duration_ms') else None,
            
            # Release date
            release_date=episode_data.get('release_date'),
            
            # Show information
            show_name=show_info.get('name'),
            show_artist=show_info.get('publisher'),
            
            # Quality indicators
            explicit_content=episode_data.get('explicit', False),
            
            # Language
            language=episode_data.get('language') or episode_data.get('languages', [None])[0],
            
            # Store full data
            platform_specific={
                'id': episode_data.get('id'),
                'show_id': show_info.get('id'),
                'external_urls': episode_data.get('external_urls', {}),
                'images': episode_data.get('images', []),
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_engagement_estimate()
        
        return metrics
