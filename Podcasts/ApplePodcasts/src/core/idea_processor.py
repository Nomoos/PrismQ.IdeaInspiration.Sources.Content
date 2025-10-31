"""Processor for transforming Apple Podcasts data to IdeaInspiration model.

This module provides functionality to transform ApplePodcastsSource database
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
            content: Main text content (transcript for audio)
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
    """Processor for transforming Apple Podcasts data to IdeaInspiration format.
    
    This class handles the transformation of ApplePodcastsSource database records
    into the standardized IdeaInspiration model format as specified in
    PrismQ.IdeaInspiration.Model.
    """
    
    @staticmethod
    def process(apple_podcasts_record: Any) -> IdeaInspiration:
        """Transform ApplePodcastsSource record to IdeaInspiration.
        
        Args:
            apple_podcasts_record: ApplePodcastsSource database record (dict or object)
            
        Returns:
            IdeaInspiration instance
            
        Raises:
            ValueError: If required fields are missing
        """
        if not apple_podcasts_record:
            raise ValueError("Record cannot be None")
        
        # Support both dict and object access patterns
        def get_field(record, field):
            if isinstance(record, dict):
                return record.get(field)
            else:
                return getattr(record, field, None)
        
        title = get_field(apple_podcasts_record, 'title')
        source_id = get_field(apple_podcasts_record, 'source_id')
        
        if not title:
            raise ValueError("Record must have a title")
        
        if not source_id:
            raise ValueError("Record must have a source_id")
        
        # Parse score_dictionary to extract metadata
        score_dictionary = get_field(apple_podcasts_record, 'score_dictionary')
        if isinstance(apple_podcasts_record, dict):
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
            if hasattr(apple_podcasts_record, 'get_score_dict'):
                score_dict = apple_podcasts_record.get_score_dict() or {}
            else:
                score_dict = {}
        
        # Extract transcript text if available
        content = ""
        if score_dict.get('transcript'):
            content = score_dict['transcript']
        
        # Extract keywords from tags (comma-separated string)
        keywords = []
        tags = get_field(apple_podcasts_record, 'tags')
        if tags:
            keywords = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Build metadata dictionary (string key-value pairs for SQLite compatibility)
        metadata = IdeaProcessor._build_metadata(apple_podcasts_record, score_dict)
        
        # Extract source information
        source_url = IdeaProcessor._build_source_url(score_dict)
        source_created_by = IdeaProcessor._extract_artist_name(score_dict)
        source_created_at = IdeaProcessor._extract_release_date(score_dict)
        
        # Calculate score (use existing score or convert to int)
        record_score = get_field(apple_podcasts_record, 'score')
        score = None
        if record_score is not None:
            # Round to nearest integer for IdeaInspiration model
            score = int(round(record_score))
        
        description = get_field(apple_podcasts_record, 'description')
        
        return IdeaInspiration(
            title=title,
            description=description or "",
            content=content,
            keywords=keywords,
            source_type=ContentType.AUDIO,  # Apple Podcasts are audio content
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
            record: ApplePodcastsSource record (dict or object)
            score_dict: Parsed score dictionary
            
        Returns:
            Metadata dictionary (string key-value pairs)
        """
        metadata = {}
        
        # Extract metrics
        if score_dict.get('rating') is not None:
            metadata['rating'] = str(score_dict['rating'])
        if score_dict.get('rating_count') is not None:
            metadata['rating_count'] = str(score_dict['rating_count'])
        if score_dict.get('review_count') is not None:
            metadata['review_count'] = str(score_dict['review_count'])
        
        # Extract duration
        if score_dict.get('duration_ms') is not None:
            metadata['duration_ms'] = str(score_dict['duration_ms'])
        if score_dict.get('duration_seconds') is not None:
            metadata['duration_seconds'] = str(score_dict['duration_seconds'])
        
        # Extract episode information
        if score_dict.get('episode_number') is not None:
            metadata['episode_number'] = str(score_dict['episode_number'])
        if score_dict.get('season_number') is not None:
            metadata['season_number'] = str(score_dict['season_number'])
        if score_dict.get('episode_type'):
            metadata['episode_type'] = str(score_dict['episode_type'])
        
        # Extract show information
        show_info = score_dict.get('show', {})
        if show_info.get('name'):
            metadata['show_name'] = str(show_info['name'])
        if show_info.get('artist'):
            metadata['show_artist'] = str(show_info['artist'])
        if show_info.get('rating') is not None:
            metadata['show_rating'] = str(show_info['rating'])
        
        # Extract categories
        genres = score_dict.get('genres', [])
        if genres:
            metadata['genres'] = ','.join(genres)
        
        # Extract language and country
        if score_dict.get('language'):
            metadata['language'] = str(score_dict['language'])
        if score_dict.get('country'):
            metadata['country'] = str(score_dict['country'])
        
        # Extract platform-specific data
        platform_specific = score_dict.get('platform_specific', {})
        if platform_specific.get('track_id'):
            metadata['track_id'] = str(platform_specific['track_id'])
        if platform_specific.get('collection_id'):
            metadata['collection_id'] = str(platform_specific['collection_id'])
        if platform_specific.get('feed_url'):
            metadata['feed_url'] = str(platform_specific['feed_url'])
        
        # Add platform identifier
        metadata['platform'] = 'apple_podcasts'
        metadata['source_type'] = 'audio'
        
        return metadata
    
    @staticmethod
    def _build_source_url(score_dict: Dict[str, Any]) -> Optional[str]:
        """Build episode URL from score dictionary.
        
        Args:
            score_dict: Parsed score dictionary
            
        Returns:
            Episode URL or None
        """
        platform_specific = score_dict.get('platform_specific', {})
        track_id = platform_specific.get('track_id')
        
        if track_id:
            return f"https://podcasts.apple.com/podcast/id{track_id}"
        
        return None
    
    @staticmethod
    def _extract_artist_name(score_dict: Dict[str, Any]) -> Optional[str]:
        """Extract artist/creator name from score dictionary.
        
        Args:
            score_dict: Parsed score dictionary
            
        Returns:
            Artist name or None
        """
        show_info = score_dict.get('show', {})
        return show_info.get('artist')
    
    @staticmethod
    def _extract_release_date(score_dict: Dict[str, Any]) -> Optional[str]:
        """Extract and format release date from score dictionary.
        
        Args:
            score_dict: Parsed score dictionary
            
        Returns:
            ISO 8601 formatted date string or None
        """
        release_date = score_dict.get('release_date')
        
        if not release_date:
            return None
        
        # Try to parse and convert to ISO 8601 format
        try:
            if len(release_date) == 8 and release_date.isdigit():
                # YYYYMMDD format
                dt = datetime.strptime(release_date, '%Y%m%d')
                return dt.isoformat()
            else:
                # Assume it's already in ISO 8601 or similar format
                return release_date
        except ValueError:
            # If parsing fails, return as-is
            return release_date
    
    @staticmethod
    def process_batch(records: List[Any]) -> List[IdeaInspiration]:
        """Process multiple Apple Podcasts records in batch.
        
        Args:
            records: List of ApplePodcastsSource records
            
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
                print(f"Warning: Failed to process record {record.get('id', 'unknown')}: {e}")
                continue
        return results
