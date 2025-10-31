"""Processor for transforming Instagram Reels data to IdeaInspiration model.

This module provides functionality to transform InstagramReelsSource database
records into the standardized IdeaInspiration format.
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
    """Standardized IdeaInspiration model (matching PrismQ.IdeaInspiration.Model)."""
    
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
            title: Content title (caption)
            description: Brief description
            content: Main text content
            keywords: List of keywords (hashtags)
            source_type: Type of content (video for reels)
            metadata: Additional metadata
            source_id: Instagram reel ID
            source_url: URL to original reel
            source_created_by: Creator username
            source_created_at: Creation timestamp
            score: Numerical score
            category: Primary category
            subcategory_relevance: Relevance scores for subcategories
            contextual_category_scores: Contextual scores
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
            Dictionary representation
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
            'contextual_category_scores': self.contextual_category_scores
        }


class IdeaProcessor:
    """Processor for transforming Instagram Reels data to IdeaInspiration format."""
    
    @staticmethod
    def process_record(record: Dict[str, Any]) -> IdeaInspiration:
        """Transform a database record to IdeaInspiration format.
        
        Args:
            record: Database record dictionary
            
        Returns:
            IdeaInspiration instance
        """
        # Parse score_dictionary if available
        score_dict = {}
        if record.get('score_dictionary'):
            try:
                score_dict = json.loads(record['score_dictionary'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Extract keywords from tags
        tags = record.get('tags', '')
        keywords = []
        if tags:
            keywords = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Extract creator from score_dictionary if available
        creator = None
        if 'author_username' in score_dict:
            creator = score_dict['author_username']
        elif 'creator' in score_dict and isinstance(score_dict['creator'], dict):
            creator = score_dict['creator'].get('username')
        
        # Extract upload date
        upload_date = None
        if 'upload_date' in score_dict:
            upload_date = score_dict['upload_date']
        elif 'created_at' in record:
            upload_date = str(record['created_at'])
        
        # Construct metadata
        metadata = {
            'source_platform': record.get('source', 'instagram_reels'),
            'engagement_rate': str(score_dict.get('engagement_rate', 0)),
            'plays_count': str(score_dict.get('plays_count', 0)),
            'like_count': str(score_dict.get('like_count', 0)),
            'comment_count': str(score_dict.get('comment_count', 0))
        }
        
        # Add audio info if available
        if score_dict.get('audio_name'):
            metadata['audio'] = score_dict['audio_name']
        
        # Add location if available
        if score_dict.get('location_name'):
            metadata['location'] = score_dict['location_name']
        
        # Construct Instagram reel URL
        source_url = None
        if record.get('source_id'):
            source_url = f"https://www.instagram.com/reel/{record['source_id']}/"
        
        return IdeaInspiration(
            title=record.get('title', ''),
            description=record.get('description', ''),
            content=record.get('description', ''),  # Use caption as content
            keywords=keywords,
            source_type=ContentType.VIDEO,
            metadata=metadata,
            source_id=record.get('source_id'),
            source_url=source_url,
            source_created_by=creator,
            source_created_at=upload_date,
            score=int(record.get('score', 0)) if record.get('score') else None
        )
    
    @staticmethod
    def process_records(records: List[Dict[str, Any]]) -> List[IdeaInspiration]:
        """Transform multiple database records to IdeaInspiration format.
        
        Args:
            records: List of database record dictionaries
            
        Returns:
            List of IdeaInspiration instances
        """
        return [IdeaProcessor.process_record(record) for record in records]
    
    @staticmethod
    def to_json(ideas: List[IdeaInspiration]) -> str:
        """Convert list of IdeaInspiration instances to JSON.
        
        Args:
            ideas: List of IdeaInspiration instances
            
        Returns:
            JSON string
        """
        return json.dumps(
            [idea.to_dict() for idea in ideas],
            indent=2,
            ensure_ascii=False
        )
