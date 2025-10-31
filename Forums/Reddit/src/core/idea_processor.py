"""Processor for transforming Reddit post data to IdeaInspiration model.

This module provides functionality to transform RedditSource database
records into the standardized IdeaInspiration format as defined in
PrismQ.IdeaInspiration.Model.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime


# Constants
MAX_DESCRIPTION_LENGTH = 500  # Maximum characters for description field


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
        """Initialize IdeaInspiration."""
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
    """Processes Reddit posts into IdeaInspiration format.
    
    Follows Single Responsibility Principle (SRP) by focusing only on
    data transformation.
    """
    
    @staticmethod
    def process(record: Dict[str, Any]) -> IdeaInspiration:
        """Transform RedditSource record to IdeaInspiration.
        
        Args:
            record: Database record from RedditSource table
            
        Returns:
            IdeaInspiration object
        """
        # Parse score dictionary
        score_dict = {}
        if record.get('score_dictionary'):
            try:
                if isinstance(record['score_dictionary'], str):
                    score_dict = json.loads(record['score_dictionary'])
                else:
                    score_dict = record['score_dictionary']
            except json.JSONDecodeError:
                score_dict = {}
        
        # Extract keywords from tags
        tags = record.get('tags', '')
        keywords = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Build metadata dictionary (must be string values)
        metadata = {
            'source': record.get('source', 'reddit'),
            'reddit_post_id': record.get('source_id', ''),
            'created_at': str(record.get('created_at', '')),
        }
        
        # Add score metrics to metadata as strings
        if score_dict:
            # Add key metrics as metadata
            if 'score' in score_dict:
                metadata['reddit_score'] = str(score_dict['score'])
            if 'upvote_ratio' in score_dict:
                metadata['upvote_ratio'] = str(score_dict['upvote_ratio'])
            if 'num_comments' in score_dict:
                metadata['num_comments'] = str(score_dict['num_comments'])
            if 'engagement_rate' in score_dict:
                metadata['engagement_rate'] = str(score_dict['engagement_rate'])
            if 'viral_velocity' in score_dict:
                metadata['viral_velocity'] = str(score_dict['viral_velocity'])
        
        # Extract author and subreddit info from score_dict
        author_name = None
        if score_dict.get('author'):
            author_info = score_dict['author']
            if isinstance(author_info, dict):
                author_name = author_info.get('name')
                if author_info.get('link_karma'):
                    metadata['author_link_karma'] = str(author_info['link_karma'])
                if author_info.get('comment_karma'):
                    metadata['author_comment_karma'] = str(author_info['comment_karma'])
        
        if score_dict.get('subreddit'):
            subreddit_info = score_dict['subreddit']
            if isinstance(subreddit_info, dict):
                metadata['subreddit'] = subreddit_info.get('name', '')
                if subreddit_info.get('subscribers'):
                    metadata['subreddit_subscribers'] = str(subreddit_info['subscribers'])
        
        # Build source URL
        source_url = None
        if record.get('source_id'):
            source_url = f"https://reddit.com/comments/{record['source_id']}"
        
        # Extract creation timestamp from score_dict
        source_created_at = None
        if score_dict.get('created_utc'):
            try:
                dt = datetime.fromtimestamp(score_dict['created_utc'])
                source_created_at = dt.isoformat()
            except (ValueError, TypeError):
                pass
        
        # Determine content type (Reddit posts are primarily text)
        content_type = ContentType.TEXT
        if score_dict.get('content', {}).get('type') == 'link':
            # Could be video/image link
            url = score_dict.get('content', {}).get('url', '')
            if any(domain in url for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
                content_type = ContentType.VIDEO
        
        # Create IdeaInspiration object
        return IdeaInspiration(
            title=record.get('title', ''),
            description=record.get('description', '')[:MAX_DESCRIPTION_LENGTH],
            content=record.get('description', ''),  # Full text as content
            keywords=keywords,
            source_type=content_type,
            metadata=metadata,
            source_id=record.get('source_id'),
            source_url=source_url,
            source_created_by=author_name,
            source_created_at=source_created_at,
            score=int(record.get('score', 0)) if record.get('score') else None,
            category='reddit',  # Default category
        )
