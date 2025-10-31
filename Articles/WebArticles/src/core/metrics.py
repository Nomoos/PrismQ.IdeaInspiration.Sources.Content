"""Universal metrics schema for web article analysis.

This module defines a standardized metrics structure for web articles,
adapted from the cross-platform metrics schema.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import re


@dataclass
class UniversalMetrics:
    """Universal metrics schema for web article content analysis.
    
    This schema standardizes metrics across different article sources to enable
    consistent analysis and comparison.
    """
    
    # === Core Engagement Metrics ===
    # These are the primary metrics available on most platforms
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    # === Article-Specific Engagement ===
    clap_count: Optional[int] = None        # Medium claps
    bookmark_count: Optional[int] = None    # Article saves/bookmarks
    reading_time_min: Optional[int] = None  # Estimated reading time
    word_count: Optional[int] = None        # Article word count
    
    # === Engagement Ratios ===
    # Calculated engagement metrics
    engagement_rate: Optional[float] = None      # (likes + comments + shares) / views
    read_ratio: Optional[float] = None           # Estimated completion rate
    social_score: Optional[float] = None         # Combined social metrics
    
    # === Performance Metrics ===
    # Time-based performance indicators
    views_per_day: Optional[float] = None
    days_since_publish: Optional[int] = None
    
    # === Content Metadata ===
    title_length: Optional[int] = None           # Character count
    description_length: Optional[int] = None     # Character count
    content_length: Optional[int] = None         # Full text length
    tag_count: Optional[int] = None              # Number of tags/keywords
    has_images: bool = False                     # Contains images
    image_count: Optional[int] = None            # Number of images
    
    # === Quality Indicators ===
    freshness_score: Optional[float] = None      # Time-based relevance (0-1)
    quality_score: Optional[float] = None        # Overall quality score
    
    # === Platform Context ===
    platform: str = "web_article"                # web_article, medium, etc.
    content_type: str = "article"                # article, blog, news
    
    # === Author Metrics ===
    author_name: Optional[str] = None
    author_follower_count: Optional[int] = None  # Author followers
    author_verification: bool = False            # Verified author status
    
    # === Publication Context ===
    publish_date: Optional[str] = None           # ISO format
    domain: Optional[str] = None                 # Source domain
    publication: Optional[str] = None            # Publication name
    categories: List[str] = field(default_factory=list)
    
    # === Raw Platform Data ===
    # Store platform-specific data that doesn't fit standard schema
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Engagement rate: (likes + comments + shares) / views * 100
        if self.view_count > 0:
            total_engagement = self.like_count + self.comment_count + self.share_count
            self.engagement_rate = (total_engagement / self.view_count) * 100
        
        # Calculate social score
        self.social_score = self._calculate_social_score()
        
        # Performance metrics
        if self.days_since_publish and self.days_since_publish > 0:
            self.views_per_day = self.view_count / self.days_since_publish
        
        # Freshness score (decays over time)
        if self.days_since_publish is not None:
            # Exponential decay: score = e^(-days/30)
            # Articles lose ~50% freshness after ~21 days
            import math
            self.freshness_score = math.exp(-self.days_since_publish / 30.0)
        
        # Quality score (simple heuristic based on word count, engagement, etc.)
        self.quality_score = self._calculate_quality_score()
    
    def _calculate_social_score(self) -> float:
        """Calculate combined social engagement score.
        
        Returns:
            Normalized social score (0-10)
        """
        # Weighted combination of social signals
        score = 0.0
        
        if self.like_count > 0:
            score += min(self.like_count / 100, 3.0)  # Max 3 points
        
        if self.comment_count > 0:
            score += min(self.comment_count / 20, 3.0)  # Max 3 points
        
        if self.share_count > 0:
            score += min(self.share_count / 10, 4.0)  # Max 4 points
        
        return min(score, 10.0)
    
    def _calculate_quality_score(self) -> float:
        """Calculate content quality score.
        
        Returns:
            Quality score (0-10)
        """
        score = 0.0
        
        # Word count quality (optimal range: 800-2000 words)
        if self.word_count:
            if 800 <= self.word_count <= 2000:
                score += 3.0
            elif 500 <= self.word_count < 800 or 2000 < self.word_count <= 3000:
                score += 2.0
            elif self.word_count >= 300:
                score += 1.0
        
        # Engagement quality
        if self.engagement_rate and self.engagement_rate > 1.0:
            score += min(self.engagement_rate / 2, 3.0)
        
        # Social proof
        if self.social_score:
            score += min(self.social_score / 2, 2.0)
        
        # Content richness
        if self.has_images:
            score += 1.0
        
        # Tag quality
        if self.tag_count and 3 <= self.tag_count <= 10:
            score += 1.0
        
        return min(score, 10.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary, excluding None values."""
        result = asdict(self)
        # Remove None values for cleaner storage
        return {k: v for k, v in result.items() if v is not None and v != [] and v != {}}
    
    @classmethod
    def from_article(cls, article_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create UniversalMetrics from article data.
        
        Args:
            article_data: Article data dictionary
        """
        # Extract basic metrics
        content = article_data.get('content', {})
        if isinstance(content, str):
            content_text = content
        else:
            content_text = content.get('text', '')
        
        word_count = len(content_text.split()) if content_text else 0
        
        # Calculate reading time (average 200-250 words per minute)
        reading_time = max(1, word_count // 200) if word_count > 0 else None
        
        # Extract metadata
        metrics_data = article_data.get('metrics', {})
        source_info = article_data.get('source_info', {})
        author_info = article_data.get('author', {})
        
        # Calculate days since publish
        days_since_publish = None
        publish_date = article_data.get('published_at')
        if publish_date:
            try:
                from datetime import datetime
                if isinstance(publish_date, str):
                    pub_dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                else:
                    pub_dt = publish_date
                days_since_publish = (datetime.now(pub_dt.tzinfo or None) - pub_dt).days
            except Exception:
                pass
        
        metrics = cls(
            platform=article_data.get('source', 'web_article'),
            content_type="article",
            
            # Engagement metrics
            view_count=metrics_data.get('view_count', 0),
            like_count=metrics_data.get('like_count', 0),
            comment_count=metrics_data.get('comment_count', 0),
            share_count=metrics_data.get('share_count', metrics_data.get('social_shares', 0)),
            clap_count=metrics_data.get('clap_count'),
            bookmark_count=metrics_data.get('bookmark_count'),
            
            # Content metadata
            word_count=word_count,
            reading_time_min=reading_time,
            title_length=len(article_data.get('title', '')),
            description_length=len(article_data.get('description', '')),
            content_length=len(content_text),
            tag_count=len(article_data.get('tags', [])),
            
            # Image information
            has_images=bool(content.get('top_image') or content.get('images')),
            image_count=len(content.get('images', [])) if isinstance(content, dict) else 0,
            
            # Author info
            author_name=author_info.get('name') if isinstance(author_info, dict) else author_info,
            author_follower_count=author_info.get('follower_count') if isinstance(author_info, dict) else None,
            
            # Publication context
            publish_date=publish_date,
            days_since_publish=days_since_publish,
            domain=source_info.get('domain'),
            publication=source_info.get('publication'),
            categories=article_data.get('tags', []) if isinstance(article_data.get('tags'), list) else [],
            
            # Platform-specific data
            platform_specific=metrics_data.get('platform_specific', {})
        )
        
        # Calculate derived metrics
        metrics.calculate_derived_metrics()
        
        return metrics
    
    @staticmethod
    def generate_article_id(url: str) -> str:
        """Generate a unique article ID from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Unique hash-based ID
        """
        return hashlib.sha256(url.encode()).hexdigest()[:16]
