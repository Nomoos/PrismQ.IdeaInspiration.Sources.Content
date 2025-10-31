"""Universal metrics schema for cross-platform idea collection.

This module extends the UniversalMetrics to support HackerNews-specific metrics.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


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
    
    # === Performance Metrics ===
    views_per_day: Optional[float] = None
    views_per_hour: Optional[float] = None
    score_per_hour: Optional[float] = None
    days_since_upload: Optional[int] = None
    
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
    
    # === HackerNews-Specific Metrics ===
    descendants_count: Optional[int] = None  # Total comment tree size
    viral_velocity: Optional[float] = None
    points_per_hour: Optional[float] = None
    hours_since_post: Optional[float] = None
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Engagement rate: comments / score * 100 (for HN)
        if self.like_count > 0:
            self.engagement_rate = (self.comment_count / self.like_count) * 100
        
        # Performance metrics based on time since post
        if self.hours_since_post and self.hours_since_post > 0:
            # Points per hour
            if self.like_count > 0:
                self.points_per_hour = self.like_count / self.hours_since_post
                
                # Viral velocity: combines point velocity with engagement
                if self.engagement_rate:
                    self.viral_velocity = (self.points_per_hour * self.engagement_rate) / 10
        
        # Calculate days since upload from hours
        if self.hours_since_post:
            self.days_since_upload = int(self.hours_since_post / 24) or 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_hackernews(cls, item_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from HackerNews item data.
        
        Args:
            item_data: HackerNews item data from API
            
        Returns:
            UniversalMetrics instance
        """
        # Extract data from HN item
        score = item_data.get('score', 0) or 0
        descendants = item_data.get('descendants', 0) or 0
        title = item_data.get('title', '')
        text = item_data.get('text', '')
        item_type = item_data.get('type', 'story')
        created_time = item_data.get('time', None)
        
        # Calculate hours since post
        hours_since = None
        if created_time:
            now = datetime.now(timezone.utc)
            created_dt = datetime.fromtimestamp(created_time, tz=timezone.utc)
            hours_since = (now - created_dt).total_seconds() / 3600
            if hours_since < 0.1:  # Minimum 0.1 hours
                hours_since = 0.1
        
        metrics = cls(
            platform="hackernews",
            content_type=item_type,
            like_count=score,  # HN score as "likes"
            comment_count=descendants,  # Total descendants (all comments)
            descendants_count=descendants,
            
            # Content metadata
            title_length=len(title),
            description_length=len(text) if text else 0,
            hours_since_post=hours_since,
            
            # Store full data
            platform_specific={
                'score': score,
                'descendants': descendants,
                'type': item_type,
                'time': created_time,
                'by': item_data.get('by', ''),
                'url': item_data.get('url', ''),
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
