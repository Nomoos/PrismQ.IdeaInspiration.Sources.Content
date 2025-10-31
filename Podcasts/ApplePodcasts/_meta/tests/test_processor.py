"""Tests for ApplePodcasts idea processor module."""

import pytest
from core.idea_processor import IdeaProcessor, ContentType


def test_process_basic_record():
    """Test processing a basic podcast record."""
    record = {
        'id': 1,
        'source': 'apple_podcasts',
        'source_id': '123456',
        'title': 'Test Episode',
        'description': 'Test description',
        'tags': 'comedy,business',
        'score': 90.0,
        'score_dictionary': {
            'rating': 4.5,
            'rating_count': 100,
            'duration_ms': 3600000,
            'release_date': '2025-01-15',
            'show': {
                'name': 'Test Show',
                'artist': 'Test Creator'
            },
            'platform_specific': {
                'track_id': 123456
            }
        }
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Test Episode'
    assert idea.description == 'Test description'
    assert idea.source_type == ContentType.AUDIO
    assert idea.source_id == '123456'
    assert idea.score == 90
    assert 'comedy' in idea.keywords
    assert 'business' in idea.keywords


def test_process_record_with_json_string():
    """Test processing record with JSON string score_dictionary."""
    import json
    
    record = {
        'id': 1,
        'source': 'apple_podcasts',
        'source_id': '789012',
        'title': 'Test Episode 2',
        'description': 'Test description 2',
        'tags': 'technology',
        'score': 85.5,
        'score_dictionary': json.dumps({
            'rating': 4.2,
            'show': {
                'name': 'Tech Show',
                'artist': 'Tech Creator'
            }
        })
    }
    
    idea = IdeaProcessor.process(record)
    
    assert idea.title == 'Test Episode 2'
    assert idea.source_type == ContentType.AUDIO
    assert 'technology' in idea.keywords


def test_process_missing_title():
    """Test that processing fails with missing title."""
    record = {
        'id': 1,
        'source_id': '123456',
        'description': 'Test'
    }
    
    with pytest.raises(ValueError, match="must have a title"):
        IdeaProcessor.process(record)


def test_process_missing_source_id():
    """Test that processing fails with missing source_id."""
    record = {
        'id': 1,
        'title': 'Test Episode'
    }
    
    with pytest.raises(ValueError, match="must have a source_id"):
        IdeaProcessor.process(record)


def test_build_metadata():
    """Test metadata building."""
    record = {
        'id': 1,
        'source_id': '123456',
        'title': 'Test'
    }
    
    score_dict = {
        'rating': 4.8,
        'rating_count': 500,
        'duration_ms': 1800000,
        'show': {
            'name': 'Test Show',
            'artist': 'Test Creator'
        }
    }
    
    metadata = IdeaProcessor._build_metadata(record, score_dict)
    
    assert metadata['platform'] == 'apple_podcasts'
    assert metadata['source_type'] == 'audio'
    assert metadata['rating'] == '4.8'
    assert metadata['rating_count'] == '500'
    assert metadata['duration_ms'] == '1800000'
    assert metadata['show_name'] == 'Test Show'
    assert metadata['show_artist'] == 'Test Creator'


def test_process_batch():
    """Test processing multiple records."""
    records = [
        {
            'id': 1,
            'source_id': '111',
            'title': 'Episode 1',
            'score_dictionary': {}
        },
        {
            'id': 2,
            'source_id': '222',
            'title': 'Episode 2',
            'score_dictionary': {}
        }
    ]
    
    ideas = IdeaProcessor.process_batch(records)
    
    assert len(ideas) == 2
    assert ideas[0].title == 'Episode 1'
    assert ideas[1].title == 'Episode 2'


def test_process_batch_with_failures():
    """Test that batch processing continues on failures."""
    records = [
        {
            'id': 1,
            'source_id': '111',
            'title': 'Episode 1',
            'score_dictionary': {}
        },
        {
            'id': 2,
            # Missing source_id - will fail
            'title': 'Episode 2',
            'score_dictionary': {}
        },
        {
            'id': 3,
            'source_id': '333',
            'title': 'Episode 3',
            'score_dictionary': {}
        }
    ]
    
    ideas = IdeaProcessor.process_batch(records)
    
    # Should have 2 successful ideas (1 failed)
    assert len(ideas) == 2
    assert ideas[0].title == 'Episode 1'
    assert ideas[1].title == 'Episode 3'
