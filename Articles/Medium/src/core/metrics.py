"""Universal metrics schema for cross-platform idea collection.

This module defines a standardized metrics structure that works across
multiple platforms: YouTube, Reddit, Medium, TikTok, etc.

Inspired by comprehensive analytics tools like VidIQ and TubeBuddy.
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
    # These are the primary metrics available on most platforms
    view_count: int = 0
    like_count: int = 0  # Claps for Medium
    comment_count: int = 0  # Responses for Medium
    share_count: int = 0
    
    # === Platform-Specific Engagement ===
    dislike_count: Optional[int] = None  # YouTube (often hidden)
    upvote_count: Optional[int] = None   # Reddit ups
    downvote_count: Optional[int] = None # Reddit downs
    favorite_count: Optional[int] = None # YouTube favorites
    save_count: Optional[int] = None     # Instagram saves
    repost_count: Optional[int] = None   # TikTok reposts
    
    # === Engagement Ratios ===
    # Calculated engagement metrics
    upvote_ratio: Optional[float] = None         # Reddit upvote ratio
    engagement_rate: Optional[float] = None      # (likes + comments + shares) / views
    like_to_view_ratio: Optional[float] = None   # likes / views
    comment_to_view_ratio: Optional[float] = None # comments / views
    share_to_view_ratio: Optional[float] = None  # shares / views
    
    # === Performance Metrics ===
    # Time-based performance indicators
    views_per_day: Optional[float] = None
    views_per_hour: Optional[float] = None
    days_since_upload: Optional[int] = None
    
    # === Content Metadata ===
    duration_seconds: Optional[int] = None       # Video/content duration (or reading time)
    title_length: Optional[int] = None           # Character count
    description_length: Optional[int] = None     # Character count
    tag_count: Optional[int] = None              # Number of tags/hashtags
    
    # === Quality Indicators ===
    has_subtitles: bool = False                  # Subtitle availability
    has_chapters: bool = False                   # Chapter markers
    chapter_count: Optional[int] = None
    resolution: Optional[str] = None             # Video resolution (e.g., "1920x1080")
    fps: Optional[int] = None                    # Frames per second
    aspect_ratio: Optional[str] = None           # e.g., "16:9", "9:16"
    
    # === Platform Context ===
    platform: str = "unknown"                    # youtube, reddit, medium, instagram, tiktok, facebook
    content_type: Optional[str] = None           # short, long, post, story, reel, article, etc.
    
    # === Channel/Author Metrics ===
    author_follower_count: Optional[int] = None  # Channel subscribers/followers
    author_verification: bool = False            # Verified account status
    
    # === Additional Context ===
    upload_date: Optional[str] = None            # ISO format or platform format
    categories: List[str] = field(default_factory=list)
    age_restriction: Optional[int] = None        # 0 = none, 18 = adult
    
    # === Raw Platform Data ===
    # Store platform-specific data that doesn't fit standard schema
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_medium(cls, article_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from Medium article data.
        
        Args:
            article_data: Medium article data with metrics
        """
        metrics_data = article_data.get('metrics', {})
        author_data = article_data.get('author', {})
        
        # Calculate view count estimate (if available)
        # Medium doesn't always show exact view counts
        view_count = metrics_data.get('views', 0)
        
        # Claps are Medium's "likes"
        clap_count = metrics_data.get('claps', 0)
        
        # Responses are Medium's "comments"
        response_count = metrics_data.get('responses', 0)
        
        # Reading time in minutes
        reading_time_min = metrics_data.get('reading_time_min', 0)
        reading_time_seconds = reading_time_min * 60
        
        # Calculate days since publication
        days_since_upload = None
        publish_date = article_data.get('publish_date')
        if publish_date:
            try:
                if isinstance(publish_date, str):
                    pub_dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                else:
                    pub_dt = publish_date
                days_since_upload = (datetime.now(pub_dt.tzinfo) - pub_dt).days
            except (ValueError, TypeError):
                pass
        
        metrics = cls(
            platform="medium",
            content_type="article",
            
            # Core engagement
            view_count=view_count,
            like_count=clap_count,  # Claps as likes
            comment_count=response_count,  # Responses as comments
            share_count=0,  # Medium doesn't expose share counts easily
            
            # Content metadata
            duration_seconds=reading_time_seconds,  # Reading time
            title_length=len(article_data.get('title', '')),
            description_length=len(article_data.get('description', '')),
            tag_count=len(article_data.get('tags', [])),
            
            # Author metrics
            author_follower_count=author_data.get('followers'),
            
            # Performance
            days_since_upload=days_since_upload,
            upload_date=publish_date,
            
            # Categories/tags
            categories=article_data.get('tags', []),
            
            # Store full data
            platform_specific={
                'article_id': article_data.get('source_id'),
                'author_username': author_data.get('username'),
                'reading_time_min': reading_time_min,
                'claps_per_day': metrics_data.get('claps_per_day'),
                'viral_velocity': metrics_data.get('viral_velocity'),
                'publication': article_data.get('publication'),
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        # Add Medium-specific calculated metrics
        if days_since_upload and days_since_upload > 0:
            metrics.platform_specific['claps_per_day'] = clap_count / days_since_upload
            # Viral velocity: engagement rate * claps_per_day
            if metrics.engagement_rate:
                metrics.platform_specific['viral_velocity'] = (
                    metrics.engagement_rate * (clap_count / days_since_upload)
                )
        
        return metrics
    
    @classmethod
    def from_youtube(cls, video_data: Dict[str, Any], snippet: Dict[str, Any] = None, 
                     statistics: Dict[str, Any] = None) -> 'UniversalMetrics':
        """Create UniversalMetrics from YouTube API data.
        
        Args:
            video_data: Full video data from YouTube API
            snippet: Video snippet (optional if included in video_data)
            statistics: Video statistics (optional if included in video_data)
        """
        snippet = snippet or video_data.get('snippet', {})
        statistics = statistics or video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        enhanced_metrics = video_data.get('enhanced_metrics', {})
        
        # Extract video quality metrics
        resolution = enhanced_metrics.get('resolution')
        fps = enhanced_metrics.get('fps')
        aspect_ratio = enhanced_metrics.get('aspect_ratio')
        
        metrics = cls(
            platform="youtube",
            view_count=int(statistics.get('viewCount', 0)),
            like_count=int(statistics.get('likeCount', 0)),
            comment_count=int(statistics.get('commentCount', 0)),
            dislike_count=int(statistics.get('dislikeCount', 0)) if statistics.get('dislikeCount') else None,
            favorite_count=int(statistics.get('favoriteCount', 0)),
            
            # Content metadata
            title_length=len(snippet.get('title', '')),
            description_length=len(snippet.get('description', '')),
            tag_count=len(snippet.get('tags', [])),
            
            # Video quality metrics
            resolution=resolution,
            fps=fps,
            aspect_ratio=aspect_ratio,
            has_subtitles=enhanced_metrics.get('subtitles_available', False),
            
            # Channel metrics
            author_follower_count=enhanced_metrics.get('channel_follower_count'),
            
            # Platform data
            upload_date=snippet.get('publishedAt'),
            categories=[snippet.get('categoryId')] if snippet.get('categoryId') else [],
            
            # Store full data
            platform_specific={
                'video_id': video_data.get('id'),
                'channel_id': snippet.get('channelId'),
                'channel_title': snippet.get('channelTitle'),
                'duration': content_details.get('duration'),
                'subtitle_text': enhanced_metrics.get('subtitle_text'),
            }
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
