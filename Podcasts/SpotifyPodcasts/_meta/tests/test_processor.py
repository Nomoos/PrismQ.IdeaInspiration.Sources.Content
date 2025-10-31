"""Tests for IdeaProcessor."""

import pytest
import json
from src.core.idea_processor import IdeaProcessor, ContentType


def test_process_basic_record():
    """Test processing a basic record."""
    record = {
        'id': 1,
        'source': 'spotify_trending',
        'source_id': 'test123',
        'title': 'Test Episode',
        'description': 'Test description',
        'tags': 'business,podcast',
        'score': 5.0,
        'score_dictionary': json.dumps({
            'show_name': 'Test Show',
            'publisher': 'Test Publisher',
            'duration_ms': 1800000,
            'release_date': '2025-01-15'
        })
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Test Episode'
    assert idea.description == 'Test description'
    assert idea.source_type == ContentType.AUDIO
    assert idea.source_id == 'test123'
    assert 'business' in idea.keywords
    assert 'podcast' in idea.keywords
    assert idea.category == 'podcast'


def test_process_with_metadata():
    """Test processing record with complete metadata."""
    record = {
        'id': 1,
        'source': 'spotify_show',
        'source_id': 'episode123',
        'title': 'Episode Title',
        'description': 'Episode description',
        'tags': 'tech,ai,startup',
        'score': 8.5,
        'score_dictionary': json.dumps({
            'show_name': 'Tech Talks',
            'publisher': 'Tech Media Inc',
            'total_episodes': 250,
            'duration_ms': 2700000,
            'release_date': '2025-01-20',
            'language': 'en',
            'has_explicit_content': False
        })
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Episode Title'
    assert idea.metadata['show_name'] == 'Tech Talks'
    assert idea.metadata['publisher'] == 'Tech Media Inc'
    assert idea.metadata['total_episodes'] == '250'
    assert idea.metadata['duration_ms'] == '2700000'
    assert idea.source_created_by == 'Tech Talks'
    assert idea.source_created_at == '2025-01-20'


def test_process_minimal_record():
    """Test processing minimal record."""
    record = {
        'id': 1,
        'source': 'spotify_category',
        'source_id': 'min123',
        'title': 'Minimal Episode',
        'description': None,
        'tags': None,
        'score': None,
        'score_dictionary': None
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Minimal Episode'
    assert idea.description == ''
    assert idea.keywords == []
    assert idea.source_id == 'min123'
    assert idea.source_type == ContentType.AUDIO


def test_idea_to_dict():
    """Test converting idea to dictionary."""
    record = {
        'id': 1,
        'source': 'spotify_trending',
        'source_id': 'test123',
        'title': 'Test Episode',
        'description': 'Test description',
        'tags': 'test',
        'score': 5.0,
        'score_dictionary': None
    }
    
    idea = IdeaProcessor.process(record)
    idea_dict = idea.to_dict()
    
    assert isinstance(idea_dict, dict)
    assert idea_dict['title'] == 'Test Episode'
    assert idea_dict['source_type'] == ContentType.AUDIO
    assert 'keywords' in idea_dict
    assert 'metadata' in idea_dict
