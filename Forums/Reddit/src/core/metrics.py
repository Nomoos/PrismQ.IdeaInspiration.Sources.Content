"""Universal metrics schema for cross-platform idea collection.

This module extends the UniversalMetrics from YouTube implementation
to support Reddit-specific metrics.
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
    
    # === Reddit-Specific Metrics ===
    award_count: Optional[int] = None
    award_types: List[str] = field(default_factory=list)
    viral_velocity: Optional[float] = None
    award_density: Optional[float] = None
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Engagement rate: (likes + comments + shares) / views * 100
        if self.view_count > 0:
            total_engagement = self.like_count + self.comment_count + self.share_count
            self.engagement_rate = (total_engagement / self.view_count) * 100
            
            # Individual ratios
            self.like_to_view_ratio = (self.like_count / self.view_count) * 100
            self.comment_to_view_ratio = (self.comment_count / self.view_count) * 100
            if self.share_count > 0:
                self.share_to_view_ratio = (self.share_count / self.view_count) * 100
        
        # Performance metrics
        if self.days_since_upload and self.days_since_upload > 0:
            self.views_per_day = self.view_count / self.days_since_upload
            if self.views_per_day:
                self.views_per_hour = self.views_per_day / 24
            
            # Reddit-specific: score per hour for viral velocity
            if self.like_count > 0:
                score_per_day = self.like_count / self.days_since_upload
                self.score_per_hour = score_per_day / 24
                # Viral velocity combines score growth with engagement
                if self.engagement_rate:
                    self.viral_velocity = (self.score_per_hour * self.engagement_rate) / 10
        
        # Award density (awards per 1000 upvotes)
        if self.award_count and self.upvote_count and self.upvote_count > 0:
            self.award_density = (self.award_count / self.upvote_count) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_reddit(cls, post_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Reddit post data.
        
        Args:
            post_data: Reddit post data (from PRAW or dict)
            
        Returns:
            UniversalMetrics instance
        """
        # Handle both PRAW objects and dictionaries
        if hasattr(post_data, '__dict__'):
            # PRAW object - extract attributes
            view_count = getattr(post_data, 'num_views', 0) or 0
            score = getattr(post_data, 'score', 0)
            ups = getattr(post_data, 'ups', 0)
            num_comments = getattr(post_data, 'num_comments', 0)
            upvote_ratio = getattr(post_data, 'upvote_ratio', 0)
            title = getattr(post_data, 'title', '')
            selftext = getattr(post_data, 'selftext', '')
            created_utc = getattr(post_data, 'created_utc', None)
            total_awards = getattr(post_data, 'total_awards_received', 0)
            all_awardings = getattr(post_data, 'all_awardings', [])
        else:
            # Dictionary - use get method
            view_count = post_data.get('num_views', 0) or 0
            score = post_data.get('score', 0)
            ups = post_data.get('ups', 0)
            num_comments = post_data.get('num_comments', 0)
            upvote_ratio = post_data.get('upvote_ratio', 0)
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            created_utc = post_data.get('created_utc', None)
            total_awards = post_data.get('total_awards_received', 0)
            all_awardings = post_data.get('all_awardings', [])
        
        # Calculate days since upload
        days_since = None
        if created_utc:
            created_dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            days_since = (now - created_dt).days or 1  # Minimum 1 day
        
        # Extract award types
        award_types = [award.get('name', 'Unknown') if isinstance(award, dict) else str(award) 
                      for award in all_awardings[:5]]  # Top 5 award types
        
        metrics = cls(
            platform="reddit",
            view_count=view_count,
            like_count=score,  # Reddit score as "likes"
            upvote_count=ups,
            comment_count=num_comments,
            upvote_ratio=upvote_ratio,
            award_count=total_awards,
            award_types=award_types,
            
            # Content metadata
            title_length=len(title),
            description_length=len(selftext),
            days_since_upload=days_since,
            
            # Store full data
            platform_specific={
                'score': score,
                'ups': ups,
                'upvote_ratio': upvote_ratio,
                'total_awards': total_awards,
                'created_utc': created_utc,
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
