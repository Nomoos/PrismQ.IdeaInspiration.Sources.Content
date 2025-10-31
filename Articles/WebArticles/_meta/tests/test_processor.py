"""Tests for idea processor module."""

import pytest
from datetime import datetime
from src.core.idea_processor import IdeaProcessor, ContentType


def test_process_basic_article():
    """Test processing a basic article record."""
    record = {
        'id': 1,
        'source': 'web_article',
        'source_id': 'test123',
        'title': 'Test Article',
        'description': 'Test description',
        'content': 'Full article content here',
        'tags': 'tag1,tag2,tag3',
        'author': 'Test Author',
        'url': 'https://example.com/test',
        'published_at': '2025-01-01T00:00:00',
        'score': 8.5,
        'score_dictionary': '{"word_count": 1200, "reading_time_min": 6}'
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Test Article'
    assert idea.description == 'Test description'
    assert idea.content == 'Full article content here'
    assert idea.source_type == ContentType.TEXT
    assert idea.source_id == 'test123'
    assert idea.source_url == 'https://example.com/test'
    assert idea.source_created_by == 'Test Author'
    assert 'tag1' in idea.keywords
    assert 'tag2' in idea.keywords
    assert 'tag3' in idea.keywords


def test_process_missing_required_fields():
    """Test that processing fails with missing required fields."""
    # Missing title
    record_no_title = {
        'source_id': 'test123',
    }
    
    with pytest.raises(ValueError, match="must have a title"):
        IdeaProcessor.process(record_no_title)
    
    # Missing source_id
    record_no_id = {
        'title': 'Test Article',
    }
    
    with pytest.raises(ValueError, match="must have a source_id"):
        IdeaProcessor.process(record_no_id)


def test_process_with_dict_score_dictionary():
    """Test processing with score_dictionary as dict."""
    record = {
        'source': 'web_article',
        'source_id': 'test123',
        'title': 'Test Article',
        'score_dictionary': {
            'word_count': 1200,
            'quality_score': 8.5,
            'freshness_score': 0.95
        }
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.metadata.get('word_count') == '1200'
    assert idea.metadata.get('quality_score') == '8.5'


def test_to_dict():
    """Test converting IdeaInspiration to dictionary."""
    record = {
        'source': 'web_article',
        'source_id': 'test123',
        'title': 'Test Article',
        'description': 'Test description',
        'content': 'Full content',
        'tags': 'tag1,tag2',
        'score': 8.0,
        'score_dictionary': '{"word_count": 1200}'
    }
    
    idea = IdeaProcessor.process(record)
    idea_dict = idea.to_dict()
    
    assert isinstance(idea_dict, dict)
    assert idea_dict['title'] == 'Test Article'
    assert idea_dict['description'] == 'Test description'
    assert idea_dict['source_type'] == ContentType.TEXT
    assert 'metadata' in idea_dict
