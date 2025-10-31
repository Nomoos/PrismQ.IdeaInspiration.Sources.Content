"""Processor for transforming Web Article data to IdeaInspiration model.

This module provides functionality to transform WebArticleSource database
records into the standardized IdeaInspiration format as defined in
PrismQ.IdeaInspiration.Model.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime


class ContentType:
    """Type of content source (matching PrismQ.IdeaInspiration.Model)."""
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class IdeaInspiration:
    """Standardized IdeaInspiration model (matching PrismQ.IdeaInspiration.Model).
    
    This is a lightweight version for transformation purposes. The full model
    is defined in PrismQ.IdeaInspiration.Model repository.
    """
    
    def __init__(
        self,
        title: str,
        description: str = "",
        content: str = "",
        keywords: Optional[List[str]] = None,
        source_type: str = ContentType.UNKNOWN,
        metadata: Optional[Dict[str, str]] = None,
        source_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_created_by: Optional[str] = None,
        source_created_at: Optional[str] = None,
        score: Optional[int] = None,
        category: Optional[str] = None,
        subcategory_relevance: Optional[Dict[str, int]] = None,
        contextual_category_scores: Optional[Dict[str, int]] = None,
    ):
        """Initialize IdeaInspiration.
        
        Args:
            title: Content title
            description: Brief description
            content: Main text content
            keywords: List of keywords
            source_type: Type of content (text/video/audio)
            metadata: Additional metadata (string key-value pairs)
            source_id: Source platform identifier
            source_url: URL to original content
            source_created_by: Creator/author
            source_created_at: Creation timestamp (ISO 8601)
            score: Numerical score
            category: Primary category
            subcategory_relevance: Relevance scores for subcategories
            contextual_category_scores: Contextual scores by language/region/age/gender
        """
        self.title = title
        self.description = description
        self.content = content
        self.keywords = keywords or []
        self.source_type = source_type
        self.metadata = metadata or {}
        self.source_id = source_id
        self.source_url = source_url
        self.source_created_by = source_created_by
        self.source_created_at = source_created_at
        self.score = score
        self.category = category
        self.subcategory_relevance = subcategory_relevance or {}
        self.contextual_category_scores = contextual_category_scores or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary containing all fields
        """
        return {
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'keywords': self.keywords,
            'source_type': self.source_type,
            'metadata': self.metadata,
            'source_id': self.source_id,
            'source_url': self.source_url,
            'source_created_by': self.source_created_by,
            'source_created_at': self.source_created_at,
            'score': self.score,
            'category': self.category,
            'subcategory_relevance': self.subcategory_relevance,
            'contextual_category_scores': self.contextual_category_scores,
        }


class IdeaProcessor:
    """Processor for transforming Web Article data to IdeaInspiration format.
    
    This class handles the transformation of WebArticleSource database records
    into the standardized IdeaInspiration model format as specified in
    PrismQ.IdeaInspiration.Model.
    """
    
    @staticmethod
    def process(web_article_record: Any) -> IdeaInspiration:
        """Transform WebArticleSource record to IdeaInspiration.
        
        Args:
            web_article_record: WebArticleSource database record (dict or object)
            
        Returns:
            IdeaInspiration instance
            
        Raises:
            ValueError: If required fields are missing
        """
        if not web_article_record:
            raise ValueError("Record cannot be None")
        
        # Support both dict and object access patterns
        def get_field(record, field):
            if isinstance(record, dict):
                return record.get(field)
            else:
                return getattr(record, field, None)
        
        title = get_field(web_article_record, 'title')
        source_id = get_field(web_article_record, 'source_id')
        
        if not title:
            raise ValueError("Record must have a title")
        
        if not source_id:
            raise ValueError("Record must have a source_id")
        
        # Parse score_dictionary to extract metadata
        score_dictionary = get_field(web_article_record, 'score_dictionary')
        if isinstance(web_article_record, dict):
            # For dict, parse JSON if it's a string
            if isinstance(score_dictionary, str):
                try:
                    score_dict = json.loads(score_dictionary) if score_dictionary else {}
                except json.JSONDecodeError:
                    score_dict = {}
            else:
                score_dict = score_dictionary or {}
        else:
            # For object, assume it's already parsed or None
            score_dict = score_dictionary or {}
        
        # Extract metadata
        description = get_field(web_article_record, 'description') or ""
        content = get_field(web_article_record, 'content') or ""
        tags_str = get_field(web_article_record, 'tags') or ""
        keywords = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []
        
        author = get_field(web_article_record, 'author')
        url = get_field(web_article_record, 'url')
        published_at = get_field(web_article_record, 'published_at')
        score = get_field(web_article_record, 'score')
        
        # Convert published_at to ISO string if it's a datetime
        if published_at and isinstance(published_at, datetime):
            published_at = published_at.isoformat()
        
        # Build metadata dictionary
        metadata = {
            'source': get_field(web_article_record, 'source') or 'web_article',
            'word_count': str(score_dict.get('word_count', 0)),
            'reading_time_min': str(score_dict.get('reading_time_min', 0)),
            'domain': score_dict.get('domain', ''),
            'publication': score_dict.get('publication', ''),
        }
        
        # Add quality scores to metadata
        if 'quality_score' in score_dict:
            metadata['quality_score'] = str(score_dict.get('quality_score'))
        if 'freshness_score' in score_dict:
            metadata['freshness_score'] = str(score_dict.get('freshness_score'))
        if 'engagement_rate' in score_dict:
            metadata['engagement_rate'] = str(score_dict.get('engagement_rate'))
        
        # Create IdeaInspiration instance
        idea = IdeaInspiration(
            title=title,
            description=description,
            content=content,
            keywords=keywords,
            source_type=ContentType.TEXT,  # Web articles are text content
            metadata=metadata,
            source_id=source_id,
            source_url=url,
            source_created_by=author,
            source_created_at=published_at,
            score=int(score) if score is not None else None,
        )
        
        return idea
