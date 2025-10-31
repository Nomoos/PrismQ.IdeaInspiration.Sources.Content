"""Processor for transforming Spotify Podcasts data to IdeaInspiration model.

This module provides functionality to transform SpotifyPodcastsSource database
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
    """Processor for transforming Spotify Podcasts records to IdeaInspiration."""
    
    @staticmethod
    def process(record: Dict[str, Any]) -> IdeaInspiration:
        """Transform a SpotifyPodcastsSource record to IdeaInspiration.
        
        Args:
            record: Database record from SpotifyPodcastsSource table
            
        Returns:
            IdeaInspiration instance
        """
        # Parse tags into keywords
        keywords = []
        if record.get('tags'):
            keywords = [tag.strip() for tag in record['tags'].split(',') if tag.strip()]
        
        # Parse score_dictionary to extract metadata
        metadata = {}
        source_created_by = None
        source_created_at = None
        
        if record.get('score_dictionary'):
            try:
                score_dict = json.loads(record['score_dictionary']) if isinstance(record['score_dictionary'], str) else record['score_dictionary']
                
                # Extract show information
                if 'show_name' in score_dict:
                    metadata['show_name'] = str(score_dict['show_name'])
                    source_created_by = str(score_dict['show_name'])
                
                if 'publisher' in score_dict:
                    metadata['publisher'] = str(score_dict['publisher'])
                
                if 'total_episodes' in score_dict:
                    metadata['total_episodes'] = str(score_dict['total_episodes'])
                
                if 'duration_ms' in score_dict:
                    metadata['duration_ms'] = str(score_dict['duration_ms'])
                
                if 'release_date' in score_dict:
                    metadata['release_date'] = str(score_dict['release_date'])
                    source_created_at = str(score_dict['release_date'])
                
                if 'language' in score_dict:
                    metadata['language'] = str(score_dict['language'])
                
                if 'has_explicit_content' in score_dict:
                    metadata['explicit'] = str(score_dict['has_explicit_content'])
                
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        # Build source_url from source_id
        source_url = None
        if record.get('source_id'):
            source_url = f"spotify:episode:{record['source_id']}"
        
        # Create IdeaInspiration
        description = record.get('description') or ''
        idea = IdeaInspiration(
            title=record['title'],
            description=description,
            content=description,  # Use description as content for podcasts
            keywords=keywords,
            source_type=ContentType.AUDIO,  # Podcasts are audio content
            metadata=metadata,
            source_id=record.get('source_id'),
            source_url=source_url,
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=int(record['score']) if record.get('score') else None,
            category='podcast',
        )
        
        return idea
