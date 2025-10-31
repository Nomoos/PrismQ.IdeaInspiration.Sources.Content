"""Universal metrics schema for Instagram Reels content analysis.

This module extends the universal metrics structure for Instagram-specific metrics.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class UniversalMetrics:
    """Universal metrics schema for Instagram Reels content analysis.
    
    This schema standardizes metrics to enable consistent analysis
    and cross-platform comparison.
    """
    
    # === Core Engagement Metrics ===
    plays_count: int = 0           # Instagram Reels plays
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    save_count: int = 0            # Instagram saves
    
    # === Engagement Ratios ===
    engagement_rate: Optional[float] = None      # (likes + comments + saves + shares) / plays
    like_to_plays_ratio: Optional[float] = None   # likes / plays
    comment_to_plays_ratio: Optional[float] = None # comments / plays
    share_to_plays_ratio: Optional[float] = None  # shares / plays
    save_to_plays_ratio: Optional[float] = None   # saves / plays
    
    # === Performance Metrics ===
    plays_per_day: Optional[float] = None
    plays_per_hour: Optional[float] = None
    days_since_upload: Optional[int] = None
    viral_velocity: Optional[float] = None  # Rate of growth
    
    # === Content Metadata ===
    duration_seconds: Optional[int] = None
    caption_length: Optional[int] = None
    hashtag_count: Optional[int] = None
    
    # === Quality Indicators ===
    has_audio: bool = False
    has_original_audio: bool = False
    audio_name: Optional[str] = None
    has_location: bool = False
    location_name: Optional[str] = None
    filter_names: List[str] = field(default_factory=list)
    effect_names: List[str] = field(default_factory=list)
    
    # === Platform Context ===
    platform: str = "instagram_reels"
    content_type: str = "reel"
    
    # === Creator/Author Metrics ===
    author_username: Optional[str] = None
    author_follower_count: Optional[int] = None
    author_verification: bool = False
    
    # === Additional Context ===
    upload_date: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Engagement rate: (likes + comments + saves + shares) / plays * 100
        if self.plays_count > 0:
            total_engagement = (
                self.like_count + 
                self.comment_count + 
                self.save_count + 
                self.share_count
            )
            self.engagement_rate = (total_engagement / self.plays_count) * 100
            
            # Individual ratios
            self.like_to_plays_ratio = (self.like_count / self.plays_count) * 100
            self.comment_to_plays_ratio = (self.comment_count / self.plays_count) * 100
            self.share_to_plays_ratio = (self.share_count / self.plays_count) * 100
            self.save_to_plays_ratio = (self.save_count / self.plays_count) * 100
        
        # Performance metrics
        if self.days_since_upload and self.days_since_upload > 0:
            self.plays_per_day = self.plays_count / self.days_since_upload
            if self.plays_per_day:
                self.plays_per_hour = self.plays_per_day / 24
        
        # Viral velocity (simplified: plays per hour)
        if self.plays_per_hour:
            self.viral_velocity = self.plays_per_hour
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of metrics
        """
        return asdict(self)
    
    @classmethod
    def from_instagram(cls, reel_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Instagram reel data.
        
        Args:
            reel_data: Instagram reel data dictionary
            
        Returns:
            UniversalMetrics instance
        """
        metrics_data = reel_data.get('metrics', {})
        creator_data = reel_data.get('creator', {})
        reel_info = reel_data.get('reel', {})
        
        # Extract engagement metrics
        plays = metrics_data.get('plays', 0)
        likes = metrics_data.get('likes', 0)
        comments = metrics_data.get('comments', 0)
        shares = metrics_data.get('shares', 0)
        saves = metrics_data.get('saves', 0)
        
        # Calculate days since upload
        days_since = None
        upload_date_str = reel_data.get('upload_date')
        if upload_date_str:
            try:
                # Try parsing ISO format
                upload_date = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
                days_since = (datetime.now() - upload_date).days
            except Exception:
                pass
        
        # Extract hashtags
        hashtags = reel_data.get('tags', [])
        if isinstance(hashtags, str):
            hashtags = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
        
        # Create metrics instance
        metrics = cls(
            plays_count=plays,
            like_count=likes,
            comment_count=comments,
            share_count=shares,
            save_count=saves,
            duration_seconds=reel_info.get('duration'),
            caption_length=len(reel_data.get('description', '')),
            hashtag_count=len(hashtags),
            has_audio=bool(reel_info.get('audio')),
            has_original_audio='Original audio' in str(reel_info.get('audio', '')),
            audio_name=reel_info.get('audio'),
            has_location=bool(reel_info.get('location')),
            location_name=reel_info.get('location'),
            filter_names=reel_info.get('filters', []),
            effect_names=reel_info.get('effects', []),
            author_username=creator_data.get('username'),
            author_follower_count=creator_data.get('followers'),
            author_verification=creator_data.get('verified', False),
            upload_date=upload_date_str,
            hashtags=hashtags,
            days_since_upload=days_since,
            platform_specific=reel_data
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from dictionary.
        
        Args:
            data: Dictionary with metric data
            
        Returns:
            UniversalMetrics instance
        """
        return cls(**data)
