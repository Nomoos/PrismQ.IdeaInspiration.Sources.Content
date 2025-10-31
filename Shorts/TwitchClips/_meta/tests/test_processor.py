"""Tests for IdeaProcessor module."""

import pytest
from src.core.idea_processor import IdeaProcessor, IdeaInspiration, ContentType


def test_process_clip():
    """Test processing a Twitch clip to IdeaInspiration format."""
    clip_data = {
        'id': 'test_clip_123',
        'url': 'https://clips.twitch.tv/test_clip_123',
        'title': 'Amazing Play!',
        'broadcaster_name': 'TestStreamer',
        'broadcaster_id': '123456',
        'creator_name': 'TestCreator',
        'game_name': 'Fortnite',
        'game_id': '33214',
        'language': 'en',
        'view_count': 50000,
        'duration': 30,
        'created_at': '2024-01-15T10:30:00Z',
        'vod_offset': 3600
    }
    
    idea = IdeaProcessor.process_clip(clip_data)
    
    assert isinstance(idea, IdeaInspiration)
    assert idea.title == 'Amazing Play!'
    assert idea.source_type == ContentType.VIDEO
    assert idea.source_id == 'twitch_clip_test_clip_123'
    assert idea.source_url == 'https://clips.twitch.tv/test_clip_123'
    assert idea.source_created_by == 'TestStreamer'
    assert idea.category == 'Fortnite'
    assert 'Fortnite' in idea.keywords
    assert 'twitch' in idea.keywords
    assert 'gaming' in idea.keywords


def test_process_clip_with_score():
    """Test processing a clip with score dictionary."""
    clip_data = {
        'id': 'test_clip_123',
        'title': 'Great Moment',
        'broadcaster_name': 'Streamer',
        'game_name': 'League of Legends',
        'view_count': 10000,
        'duration': 20,
        'created_at': '2024-01-15T10:30:00Z'
    }
    
    score_dict = {
        'views_per_day': 1000,
        'engagement_rate': 5.5
    }
    
    idea = IdeaProcessor.process_clip(clip_data, score_dict)
    
    assert idea.score == 1000  # Uses views_per_day


def test_process_clip_minimal_data():
    """Test processing a clip with minimal data."""
    clip_data = {
        'id': 'minimal_clip',
        'title': 'Untitled',
    }
    
    idea = IdeaProcessor.process_clip(clip_data)
    
    assert isinstance(idea, IdeaInspiration)
    assert idea.title == 'Untitled'
    assert idea.source_id == 'twitch_clip_minimal_clip'


def test_process_database_record():
    """Test processing a database record to IdeaInspiration format."""
    db_record = {
        'id': 1,
        'source': 'twitch_clips',
        'source_id': 'test_clip_123',
        'title': 'Database Clip',
        'description': 'From database',
        'tags': 'tag1,tag2,tag3',
        'score': 500.0,
        'score_dictionary': '{"views_per_day": 100}',
        'processed': False,
        'created_at': '2024-01-15 10:30:00',
        'updated_at': '2024-01-15 10:30:00'
    }
    
    idea = IdeaProcessor.process_database_record(db_record)
    
    assert isinstance(idea, IdeaInspiration)
    assert idea.title == 'Database Clip'
    assert idea.description == 'From database'
    assert idea.source_id == 'test_clip_123'
    assert idea.score == 500
    assert 'tag1' in idea.keywords
    assert 'tag2' in idea.keywords
    assert 'tag3' in idea.keywords


def test_idea_inspiration_to_dict():
    """Test converting IdeaInspiration to dictionary."""
    idea = IdeaInspiration(
        title='Test Title',
        description='Test Description',
        keywords=['test', 'keywords'],
        source_type=ContentType.VIDEO,
        source_id='test_123',
        score=100
    )
    
    idea_dict = idea.to_dict()
    
    assert idea_dict['title'] == 'Test Title'
    assert idea_dict['description'] == 'Test Description'
    assert idea_dict['keywords'] == ['test', 'keywords']
    assert idea_dict['source_type'] == ContentType.VIDEO
    assert idea_dict['source_id'] == 'test_123'
    assert idea_dict['score'] == 100
