"""Processor for transforming Twitch Clips data to IdeaInspiration model.

This module provides functionality to transform TwitchClipsSource database
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
        """Convert to dictionary representation."""
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
    """Processes Twitch Clips data into IdeaInspiration format.
    
    Follows the Single Responsibility Principle (SRP) by handling only
    the transformation of Twitch data to IdeaInspiration model.
    """
    
    @staticmethod
    def process_clip(clip_data: Dict[str, Any], score_dict: Optional[Dict[str, Any]] = None) -> IdeaInspiration:
        """Transform Twitch clip data to IdeaInspiration format.
        
        Args:
            clip_data: Twitch clip metadata
            score_dict: Optional score dictionary with engagement metrics
            
        Returns:
            IdeaInspiration object
        """
        # Extract basic information
        title = clip_data.get('title', 'Untitled Clip')
        clip_id = clip_data.get('id', '')
        url = clip_data.get('url', '')
        
        # Build description from context
        broadcaster_name = clip_data.get('broadcaster_name', 'Unknown')
        game_name = clip_data.get('game_name', 'Unknown Game')
        creator_name = clip_data.get('creator_name', 'Unknown')
        
        description = f"Twitch clip from {broadcaster_name}'s stream of {game_name}"
        if creator_name and creator_name != 'Unknown':
            description += f", clipped by {creator_name}"
        
        # Extract keywords from tags and game
        keywords = []
        if game_name and game_name != 'Unknown Game':
            keywords.append(game_name)
        keywords.append('twitch')
        keywords.append('clip')
        keywords.append('gaming')
        
        # Add language if available
        language = clip_data.get('language')
        if language:
            keywords.append(language)
        
        # Build metadata
        metadata = {
            'platform': 'twitch',
            'content_type': 'clip',
            'broadcaster_name': broadcaster_name,
            'game_name': game_name,
            'language': language or 'unknown',
            'duration': str(clip_data.get('duration', 0)),
        }
        
        # Add view count if available
        view_count = clip_data.get('view_count', 0)
        if view_count:
            metadata['view_count'] = str(view_count)
        
        # Add VOD offset if available
        vod_offset = clip_data.get('vod_offset')
        if vod_offset is not None:
            metadata['vod_offset'] = str(vod_offset)
        
        # Calculate score from engagement metrics
        score = 0
        if score_dict:
            # Use views_per_day as primary score metric
            views_per_day = score_dict.get('views_per_day', 0)
            if views_per_day:
                score = int(views_per_day)
            else:
                # Fallback to view count
                score = view_count
        else:
            score = view_count
        
        # Category is the game
        category = game_name if game_name != 'Unknown Game' else None
        
        # Create IdeaInspiration object
        return IdeaInspiration(
            title=title,
            description=description,
            content="",  # Twitch clips don't have transcripts in base API
            keywords=keywords,
            source_type=ContentType.VIDEO,
            metadata=metadata,
            source_id=f"twitch_clip_{clip_id}",
            source_url=url,
            source_created_by=broadcaster_name,
            source_created_at=clip_data.get('created_at'),
            score=score,
            category=category,
        )
    
    @staticmethod
    def process_database_record(db_record: Dict[str, Any]) -> IdeaInspiration:
        """Transform database record to IdeaInspiration format.
        
        Args:
            db_record: Database record from TwitchClipsSource table
            
        Returns:
            IdeaInspiration object
        """
        # Parse score dictionary if it exists
        score_dict = None
        score_dictionary_str = db_record.get('score_dictionary')
        if score_dictionary_str:
            try:
                score_dict = json.loads(score_dictionary_str)
            except json.JSONDecodeError:
                pass
        
        # Extract keywords from tags
        keywords = []
        tags_str = db_record.get('tags', '')
        if tags_str:
            keywords = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Build metadata from database fields
        metadata = {
            'platform': 'twitch',
            'source': db_record.get('source', 'twitch_clips'),
            'database_id': str(db_record.get('id', '')),
            'processed': str(db_record.get('processed', False)),
        }
        
        # Create IdeaInspiration object
        return IdeaInspiration(
            title=db_record.get('title', 'Untitled'),
            description=db_record.get('description', ''),
            content="",
            keywords=keywords,
            source_type=ContentType.VIDEO,
            metadata=metadata,
            source_id=db_record.get('source_id'),
            source_url=None,  # Not stored in database
            source_created_by=None,  # Would need to parse from description
            source_created_at=None,  # Not stored in database
            score=int(db_record.get('score', 0)) if db_record.get('score') else 0,
            category=None,
        )
