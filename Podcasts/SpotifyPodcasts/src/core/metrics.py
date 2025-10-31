"""Universal metrics schema for cross-platform podcast episode collection.

This module defines a standardized metrics structure that works across
multiple podcast platforms: Spotify, Apple Podcasts, etc.
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
    # Estimated engagement based on available data
    engagement_estimate: float = 0.0  # Composite score (0-100)
    
    # === Content Metadata ===
    duration_ms: Optional[int] = None       # Episode duration in milliseconds
    release_date: Optional[str] = None      # Release date (ISO format)
    
    # === Show Metrics ===
    show_name: Optional[str] = None
    publisher: Optional[str] = None
    total_episodes: Optional[int] = None
    
    # === Quality Indicators ===
    has_explicit_content: bool = False
    language: Optional[str] = None
    
    # === Platform Context ===
    platform: str = "spotify"                    # spotify, apple_podcasts, etc.
    content_type: str = "podcast_episode"
    
    # === Categories/Tags ===
    categories: List[str] = field(default_factory=list)
    
    # === Raw Platform Data ===
    # Store platform-specific data that doesn't fit standard schema
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data.
        
        For podcasts, engagement estimation is based on:
        - Show popularity (follower count, rating)
        - Episode recency
        - Episode position in series
        """
        # This is a simple estimation - can be enhanced based on available data
        if self.platform_specific:
            # Extract any available engagement indicators
            if 'show_followers' in self.platform_specific:
                followers = self.platform_specific['show_followers']
                # Normalize to 0-100 scale (log scale for large numbers)
                import math
                if followers > 0:
                    self.engagement_estimate = min(100, math.log10(followers + 1) * 10)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of metrics
        """
        return asdict(self)
    
    @classmethod
    def from_spotify(cls, episode_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Spotify episode data.
        
        Args:
            episode_data: Spotify episode metadata dictionary
            
        Returns:
            UniversalMetrics instance
        """
        metrics = cls()
        
        # Extract basic metadata
        metrics.duration_ms = episode_data.get('duration_ms')
        metrics.release_date = episode_data.get('release_date')
        metrics.has_explicit_content = episode_data.get('explicit', False)
        metrics.language = episode_data.get('language')
        
        # Extract show information
        if 'show' in episode_data:
            show = episode_data['show']
            metrics.show_name = show.get('name')
            metrics.publisher = show.get('publisher')
            metrics.total_episodes = show.get('total_episodes')
        
        # Store platform-specific data
        metrics.platform_specific = {
            'episode_id': episode_data.get('id'),
            'episode_uri': episode_data.get('uri'),
            'external_urls': episode_data.get('external_urls', {}),
            'images': episode_data.get('images', []),
        }
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from dictionary.
        
        Args:
            data: Dictionary containing metrics data
            
        Returns:
            UniversalMetrics instance
        """
        # Filter to only include fields that exist in the dataclass
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
