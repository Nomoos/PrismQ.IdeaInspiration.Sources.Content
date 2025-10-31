"""Processor for transforming Medium article data to IdeaInspiration model.

This module provides functionality to transform MediumSource database
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
    """Processor for transforming Medium article data to IdeaInspiration format.
    
    This class handles the transformation of MediumSource database records
    into the standardized IdeaInspiration model format as specified in
    PrismQ.IdeaInspiration.Model.
    """
    
    @staticmethod
    def process(medium_record: Any) -> IdeaInspiration:
        """Transform MediumSource record to IdeaInspiration.
        
        Args:
            medium_record: MediumSource database record (dict or object)
            
        Returns:
            IdeaInspiration instance
            
        Raises:
            ValueError: If required fields are missing
        """
        if not medium_record:
            raise ValueError("Record cannot be None")
        
        # Support both dict and object access patterns
        def get_field(record, field):
            if isinstance(record, dict):
                return record.get(field)
            else:
                return getattr(record, field, None)
        
        title = get_field(medium_record, 'title')
        source_id = get_field(medium_record, 'source_id')
        
        if not title:
            raise ValueError("Record must have a title")
        
        if not source_id:
            raise ValueError("Record must have a source_id")
        
        # Parse score_dictionary to extract metadata
        score_dictionary = get_field(medium_record, 'score_dictionary')
        if isinstance(medium_record, dict):
            # For dict, parse JSON if it's a string
            if isinstance(score_dictionary, str):
                try:
                    score_dict = json.loads(score_dictionary) if score_dictionary else {}
                except json.JSONDecodeError:
                    score_dict = {}
            else:
                score_dict = score_dictionary or {}
        else:
            # For ORM objects, call get_score_dict method if available
            if hasattr(medium_record, 'get_score_dict'):
                score_dict = medium_record.get_score_dict() or {}
            else:
                score_dict = {}
        
        # Extract article content from platform_specific
        content = ""
        platform_specific = score_dict.get('platform_specific', {})
        if platform_specific and platform_specific.get('article_content'):
            content = platform_specific['article_content']
        
        # Extract keywords from tags (comma-separated string)
        keywords = []
        tags = get_field(medium_record, 'tags')
        if tags:
            keywords = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Build metadata dictionary (string key-value pairs for SQLite compatibility)
        metadata = IdeaProcessor._build_metadata(medium_record, score_dict)
        
        # Extract source information
        source_url = IdeaProcessor._build_source_url(source_id, platform_specific)
        source_created_by = IdeaProcessor._extract_author_name(score_dict, platform_specific)
        source_created_at = IdeaProcessor._extract_publish_date(score_dict)
        
        # Calculate score (use existing score or convert to int)
        record_score = get_field(medium_record, 'score')
        score = None
        if record_score is not None:
            # Round to nearest integer for IdeaInspiration model
            score = int(round(record_score))
        
        description = get_field(medium_record, 'description')
        
        return IdeaInspiration(
            title=title,
            description=description or "",
            content=content,
            keywords=keywords,
            source_type=ContentType.TEXT,  # Medium articles are text content
            metadata=metadata,
            source_id=source_id,
            source_url=source_url,
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
        )
    
    @staticmethod
    def _build_metadata(record: Any, score_dict: Dict[str, Any]) -> Dict[str, str]:
        """Build metadata dictionary from record and score dictionary.
        
        Args:
            record: MediumSource record (dict or object)
            score_dict: Parsed score dictionary
            
        Returns:
            Metadata dictionary (string key-value pairs)
        """
        metadata = {}
        
        # Extract platform-specific data
        platform_specific = score_dict.get('platform_specific', {})
        if platform_specific:
            if platform_specific.get('reading_time_min') is not None:
                metadata['reading_time_min'] = str(platform_specific['reading_time_min'])
            if platform_specific.get('claps_per_day') is not None:
                metadata['claps_per_day'] = str(platform_specific['claps_per_day'])
            if platform_specific.get('viral_velocity') is not None:
                metadata['viral_velocity'] = str(platform_specific['viral_velocity'])
            if platform_specific.get('author_username'):
                metadata['author_username'] = str(platform_specific['author_username'])
            if platform_specific.get('publication'):
                metadata['publication'] = str(platform_specific['publication'])
        
        # Extract core metrics
        if score_dict.get('view_count') is not None:
            metadata['views'] = str(score_dict.get('view_count', '0'))
        if score_dict.get('like_count') is not None:
            metadata['claps'] = str(score_dict.get('like_count', '0'))
        if score_dict.get('comment_count') is not None:
            metadata['responses'] = str(score_dict.get('comment_count', '0'))
        
        # Extract engagement metrics
        if score_dict.get('engagement_rate') is not None:
            metadata['engagement_rate'] = str(score_dict['engagement_rate'])
        if score_dict.get('views_per_day') is not None:
            metadata['views_per_day'] = str(score_dict['views_per_day'])
        
        # Extract author metrics
        if score_dict.get('author_follower_count') is not None:
            metadata['author_followers'] = str(score_dict['author_follower_count'])
        
        # Add platform identifier
        metadata['platform'] = 'medium'
        metadata['source_type'] = 'article'
        
        return metadata
    
    @staticmethod
    def _build_source_url(source_id: str, platform_specific: Dict[str, Any]) -> str:
        """Build Medium article URL.
        
        Args:
            source_id: Medium article ID
            platform_specific: Platform-specific data containing URL
            
        Returns:
            Full Medium article URL
        """
        # Check if we have a full URL stored
        if platform_specific and platform_specific.get('article_url'):
            return platform_specific['article_url']
        
        # Otherwise construct from source_id
        # Medium article IDs are typically slugs or unique identifiers
        return f"https://medium.com/p/{source_id}"
    
    @staticmethod
    def _extract_author_name(score_dict: Dict[str, Any], platform_specific: Dict[str, Any]) -> Optional[str]:
        """Extract author name from score dictionary.
        
        Args:
            score_dict: Parsed score dictionary
            platform_specific: Platform-specific data
            
        Returns:
            Author name or None
        """
        if platform_specific and platform_specific.get('author_username'):
            return platform_specific['author_username']
        return None
    
    @staticmethod
    def _extract_publish_date(score_dict: Dict[str, Any]) -> Optional[str]:
        """Extract and format publish date from score dictionary.
        
        Args:
            score_dict: Parsed score dictionary
            
        Returns:
            ISO 8601 formatted date string or None
        """
        upload_date = score_dict.get('upload_date')
        
        if not upload_date:
            return None
        
        # Try to parse and convert to ISO 8601 format
        try:
            if len(upload_date) == 8 and upload_date.isdigit():
                # YYYYMMDD format
                dt = datetime.strptime(upload_date, '%Y%m%d')
                return dt.isoformat()
            else:
                # Assume it's already in ISO 8601 or similar format
                return upload_date
        except (ValueError, AttributeError):
            # If parsing fails, return as-is
            return upload_date if isinstance(upload_date, str) else None
    
    @staticmethod
    def process_batch(records: List[Any]) -> List[IdeaInspiration]:
        """Process multiple Medium article records in batch.
        
        Args:
            records: List of MediumSource records
            
        Returns:
            List of IdeaInspiration instances
        """
        results = []
        for record in records:
            try:
                idea = IdeaProcessor.process(record)
                results.append(idea)
            except ValueError as e:
                # Log error but continue processing
                print(f"Warning: Failed to process record: {e}")
                continue
        return results
