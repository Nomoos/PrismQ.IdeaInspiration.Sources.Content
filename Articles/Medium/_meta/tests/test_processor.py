"""Tests for Medium source idea processor."""

import pytest
import json
from src.core.idea_processor import IdeaProcessor, ContentType


def test_process_medium_record():
    """Test processing a Medium record to IdeaInspiration format.
    
    Note: The URL structure used here (https://medium.com/p/) is a simplified 
    fallback. Actual Medium articles may have various URL patterns including 
    custom domains and publication-specific paths. The processor uses the 
    actual URL from platform_specific data when available.
    """
    # Create a mock Medium record
    record = {
        'id': 1,
        'source': 'medium_trending',
        'source_id': 'test-article-123',
        'title': 'Understanding AI',
        'description': 'A comprehensive guide to AI',
        'tags': 'ai,machine-learning,python',
        'score': 8.5,
        'score_dictionary': json.dumps({
            'platform': 'medium',
            'view_count': 5000,
            'like_count': 250,
            'comment_count': 30,
            'platform_specific': {
                'article_url': 'https://medium.com/p/test-article-123',
                'author_username': 'aiexpert',
                'reading_time_min': 8,
                'article_content': 'This is the article content...'
            }
        })
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea is not None
    assert idea.title == 'Understanding AI'
    assert idea.source_type == ContentType.TEXT  # Medium articles are text
    assert idea.source_id == 'test-article-123'
    assert len(idea.keywords) == 3
    assert 'ai' in idea.keywords


def test_process_with_no_title_raises_error():
    """Test that processing fails without a title."""
    record = {
        'id': 1,
        'source': 'medium_trending',
        'source_id': 'test-123',
        'title': None,
        'description': 'Test',
        'tags': 'test'
    }
    
    with pytest.raises(ValueError, match="must have a title"):
        IdeaProcessor.process(record)


def test_process_with_no_source_id_raises_error():
    """Test that processing fails without a source_id."""
    record = {
        'id': 1,
        'source': 'medium_trending',
        'source_id': None,
        'title': 'Test Article',
        'description': 'Test',
        'tags': 'test'
    }
    
    with pytest.raises(ValueError, match="must have a source_id"):
        IdeaProcessor.process(record)


def test_process_extracts_metadata():
    """Test that metadata is properly extracted."""
    record = {
        'id': 1,
        'source': 'medium_tag',
        'source_id': 'article-456',
        'title': 'Test',
        'description': 'Test desc',
        'tags': 'test',
        'score': 5.0,
        'score_dictionary': json.dumps({
            'view_count': 1000,
            'like_count': 100,
            'comment_count': 10,
            'engagement_rate': 11.0,
            'platform_specific': {
                'reading_time_min': 5,
                'author_username': 'testuser'
            }
        })
    }
    
    idea = IdeaProcessor.process(record)
    
    assert 'platform' in idea.metadata
    assert idea.metadata['platform'] == 'medium'
    assert 'claps' in idea.metadata
    assert idea.metadata['claps'] == '100'
    assert 'reading_time_min' in idea.metadata
    assert idea.metadata['reading_time_min'] == '5'


def test_process_to_dict():
    """Test converting processed idea to dictionary."""
    record = {
        'id': 1,
        'source': 'medium_author',
        'source_id': 'article-789',
        'title': 'Test Article',
        'description': 'Test description',
        'tags': 'test,article',
        'score': 7.0,
        'score_dictionary': '{}'
    }
    
    idea = IdeaProcessor.process(record)
    idea_dict = idea.to_dict()
    
    assert isinstance(idea_dict, dict)
    assert idea_dict['title'] == 'Test Article'
    assert idea_dict['source_type'] == ContentType.TEXT
    assert 'keywords' in idea_dict
    assert 'metadata' in idea_dict


def test_process_batch():
    """Test processing multiple records in batch."""
    records = [
        {
            'id': i,
            'source': 'medium_trending',
            'source_id': f'article-{i}',
            'title': f'Article {i}',
            'description': f'Description {i}',
            'tags': 'test',
            'score': float(i),
            'score_dictionary': '{}'
        }
        for i in range(1, 4)
    ]
    
    ideas = IdeaProcessor.process_batch(records)
    
    assert len(ideas) == 3
    assert all(idea.source_type == ContentType.TEXT for idea in ideas)
