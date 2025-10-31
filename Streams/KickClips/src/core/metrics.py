"""Universal metrics schema for cross-platform idea collection.

This module defines a standardized metrics structure that works across
multiple platforms: Kick, YouTube, Twitch, Reddit, Facebook, Instagram, TikTok, etc.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class UniversalMetrics:
    """Universal metrics schema for cross-platform content analysis.
    
    This schema standardizes metrics across different platforms to enable
    consistent analysis and comparison.
    """
    
    # === Core Engagement Metrics ===
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    # === Platform-Specific Engagement ===
    reaction_count: Optional[int] = None  # Kick reactions
    dislike_count: Optional[int] = None
    upvote_count: Optional[int] = None
    downvote_count: Optional[int] = None
    favorite_count: Optional[int] = None
    save_count: Optional[int] = None
    repost_count: Optional[int] = None
    
    # === Engagement Ratios ===
    upvote_ratio: Optional[float] = None
    engagement_rate: Optional[float] = None
    like_to_view_ratio: Optional[float] = None
    comment_to_view_ratio: Optional[float] = None
    share_to_view_ratio: Optional[float] = None
    reaction_to_view_ratio: Optional[float] = None
    
    # === Performance Metrics ===
    views_per_day: Optional[float] = None
    views_per_hour: Optional[float] = None
    days_since_upload: Optional[int] = None
    viral_velocity: Optional[float] = None  # Growth factor for newer platforms
    
    # === Content Metadata ===
    duration_seconds: Optional[int] = None
    title_length: Optional[int] = None
    description_length: Optional[int] = None
    tag_count: Optional[int] = None
    
    # === Quality Indicators ===
    has_subtitles: bool = False
    has_chapters: bool = False
    chapter_count: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    aspect_ratio: Optional[str] = None
    
    # === Platform Context ===
    platform: str = "unknown"
    content_type: Optional[str] = None
    
    # === Channel/Author Metrics ===
    author_follower_count: Optional[int] = None
    author_verification: bool = False
    
    # === Additional Context ===
    upload_date: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    age_restriction: Optional[int] = None
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Engagement rate: (likes + comments + shares + reactions) / views * 100
        if self.view_count > 0:
            total_engagement = (
                self.like_count + 
                self.comment_count + 
                self.share_count + 
                (self.reaction_count or 0)
            )
            self.engagement_rate = (total_engagement / self.view_count) * 100
            
            # Individual ratios
            self.like_to_view_ratio = (self.like_count / self.view_count) * 100
            self.comment_to_view_ratio = (self.comment_count / self.view_count) * 100
            if self.share_count > 0:
                self.share_to_view_ratio = (self.share_count / self.view_count) * 100
            if self.reaction_count:
                self.reaction_to_view_ratio = (self.reaction_count / self.view_count) * 100
        
        # Performance metrics
        if self.days_since_upload and self.days_since_upload > 0:
            self.views_per_day = self.view_count / self.days_since_upload
            if self.views_per_day:
                self.views_per_hour = self.views_per_day / 24
                # Viral velocity: higher for newer platforms like Kick
                # Formula: (views_per_hour / days_since_upload) * platform_growth_factor
                platform_growth_factor = 2.0  # Kick is a growing platform
                if self.days_since_upload > 0:
                    self.viral_velocity = (self.views_per_hour / self.days_since_upload) * platform_growth_factor
    
    @classmethod
    def from_kick(cls, metrics: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Kick clip metrics.
        
        Args:
            metrics: Kick clip metrics dictionary
            
        Returns:
            UniversalMetrics instance
        """
        instance = cls(
            view_count=metrics.get('views', 0),
            like_count=metrics.get('likes', 0),
            comment_count=metrics.get('comments', 0),
            share_count=metrics.get('shares', 0),
            reaction_count=metrics.get('reactions', 0),
            duration_seconds=metrics.get('duration', 0),
            platform='kick',
            content_type='clip',
            author_follower_count=metrics.get('streamer_followers', 0),
            author_verification=metrics.get('streamer_verified', False),
            upload_date=metrics.get('created_at'),
            platform_specific=metrics,
        )
        
        # Calculate days since upload
        if metrics.get('created_at'):
            try:
                upload_date = datetime.fromisoformat(metrics['created_at'].replace('Z', '+00:00'))
                days_since = (datetime.now(upload_date.tzinfo) - upload_date).days
                instance.days_since_upload = max(1, days_since)  # Minimum 1 day
            except (ValueError, AttributeError):
                instance.days_since_upload = 1
        
        # Calculate derived metrics
        instance.calculate_derived_metrics()
        
        return instance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary containing all fields
        """
        return asdict(self)
