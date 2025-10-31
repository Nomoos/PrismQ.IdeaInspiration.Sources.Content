"""Processor for transforming Kick clips data to IdeaInspiration model.

This module provides functionality to transform KickClipsSource database
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
    """Processor for transforming Kick clips data to IdeaInspiration format."""
    
    @staticmethod
    def from_kick_clip(clip_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform Kick clip data to IdeaInspiration format.
        
        Args:
            clip_data: Kick clip data dictionary
            
        Returns:
            IdeaInspiration instance
        """
        # Extract basic fields
        title = clip_data.get('title', 'Untitled Clip')
        description = clip_data.get('description', '')
        
        # Build keywords from category, streamer, and tags
        keywords = []
        if 'category' in clip_data and clip_data['category']:
            if isinstance(clip_data['category'], dict):
                keywords.append(clip_data['category'].get('name', ''))
            else:
                keywords.append(str(clip_data['category']))
        
        if 'streamer' in clip_data and clip_data['streamer']:
            if isinstance(clip_data['streamer'], dict):
                keywords.append(clip_data['streamer'].get('username', ''))
            else:
                keywords.append(str(clip_data['streamer']))
        
        if 'tags' in clip_data and clip_data['tags']:
            if isinstance(clip_data['tags'], list):
                keywords.extend(clip_data['tags'])
            elif isinstance(clip_data['tags'], str):
                keywords.extend(clip_data['tags'].split(','))
        
        # Clean keywords
        keywords = [k.strip() for k in keywords if k and k.strip()]
        
        # Build metadata
        metadata = {}
        if 'clip' in clip_data:
            clip_info = clip_data['clip']
            if 'duration' in clip_info:
                metadata['duration'] = str(clip_info['duration'])
            if 'language' in clip_info:
                metadata['language'] = str(clip_info['language'])
        
        if 'metrics' in clip_data:
            metrics = clip_data['metrics']
            if 'views' in metrics:
                metadata['views'] = str(metrics['views'])
            if 'reactions' in metrics:
                metadata['reactions'] = str(metrics['reactions'])
        
        # Determine category
        category = None
        if 'category' in clip_data and clip_data['category']:
            if isinstance(clip_data['category'], dict):
                category = clip_data['category'].get('name')
            else:
                category = str(clip_data['category'])
        
        # Get score from universal_metrics
        score = None
        if 'universal_metrics' in clip_data and clip_data['universal_metrics']:
            metrics = clip_data['universal_metrics']
            score = int(metrics.get('engagement_rate', 0))
        
        # Get creator and timestamp
        source_created_by = None
        if 'streamer' in clip_data and clip_data['streamer']:
            if isinstance(clip_data['streamer'], dict):
                source_created_by = clip_data['streamer'].get('username')
            else:
                source_created_by = str(clip_data['streamer'])
        
        source_created_at = None
        if 'clip' in clip_data and clip_data['clip']:
            source_created_at = clip_data['clip'].get('created_at')
        
        return IdeaInspiration(
            title=title,
            description=description,
            content="",  # Kick clips don't have subtitles typically
            keywords=keywords,
            source_type=ContentType.VIDEO,
            metadata=metadata,
            source_id=clip_data.get('source_id'),
            source_url=f"https://kick.com/video/{clip_data.get('source_id', '')}",
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
            category=category,
        )
    
    @staticmethod
    def process_database_record(record: Dict[str, Any]) -> IdeaInspiration:
        """Process a database record to IdeaInspiration format.
        
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
        
        # Parse tags
        keywords = []
        if record.get('tags'):
            keywords = [tag.strip() for tag in record['tags'].split(',') if tag.strip()]
        
        return IdeaInspiration(
            title=record.get('title', ''),
            description=record.get('description', ''),
            content="",
            keywords=keywords,
            source_type=ContentType.VIDEO,
            metadata=score_dict,
            source_id=record.get('source_id'),
            source_url=f"https://kick.com/video/{record.get('source_id', '')}",
            score=int(record.get('score', 0)) if record.get('score') else None,
        )
