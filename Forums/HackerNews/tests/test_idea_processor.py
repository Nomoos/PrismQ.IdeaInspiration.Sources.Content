"""Tests for idea_processor module."""

import pytest
import json
from datetime import datetime
from src.core.idea_processor import IdeaProcessor, IdeaInspiration, ContentType


class TestIdeaInspiration:
    """Test cases for IdeaInspiration class."""
    
    def test_initialization(self):
        """Test IdeaInspiration initialization."""
        idea = IdeaInspiration(
            title="Test Title",
            description="Test Description",
            content="Test Content",
            keywords=["test", "keyword"],
            source_type=ContentType.TEXT,
            source_id="12345"
        )
        
        assert idea.title == "Test Title"
        assert idea.description == "Test Description"
        assert idea.content == "Test Content"
        assert idea.keywords == ["test", "keyword"]
        assert idea.source_type == ContentType.TEXT
        assert idea.source_id == "12345"
    
    def test_to_dict(self):
        """Test converting IdeaInspiration to dictionary."""
        idea = IdeaInspiration(
            title="Test Title",
            description="Test Description",
            keywords=["test"],
            source_id="12345"
        )
        
        idea_dict = idea.to_dict()
        
        assert isinstance(idea_dict, dict)
        assert idea_dict['title'] == "Test Title"
        assert idea_dict['description'] == "Test Description"
        assert idea_dict['keywords'] == ["test"]
        assert idea_dict['source_id'] == "12345"


class TestIdeaProcessor:
    """Test cases for IdeaProcessor class."""
    
    def test_process_basic_record(self):
        """Test processing a basic record."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test description',
            'tags': 'story,test',
            'score': 100.0,
            'score_dictionary': json.dumps({
                'score': 500,
                'descendants': 150,
                'engagement_rate': 30.0,
                'platform_specific': {
                    'by': 'testuser',
                    'time': 1234567890,
                    'url': 'https://example.com'
                }
            }),
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert isinstance(idea, IdeaInspiration)
        assert idea.title == 'Test Story'
        assert idea.description == 'Test description'
        assert idea.source_id == '12345'
        assert 'story' in idea.keywords
        assert 'test' in idea.keywords
    
    def test_process_with_metadata(self):
        """Test that metadata is properly extracted."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'score_dictionary': json.dumps({
                'score': 500,
                'descendants': 150,
                'engagement_rate': 30.0,
                'viral_velocity': 300.0,
                'points_per_hour': 100.0,
                'platform_specific': {
                    'by': 'testuser',
                    'time': 1234567890
                }
            }),
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert 'source' in idea.metadata
        assert 'hn_item_id' in idea.metadata
        assert 'hn_score' in idea.metadata
        assert 'descendants' in idea.metadata
        assert 'engagement_rate' in idea.metadata
        assert 'viral_velocity' in idea.metadata
        assert 'points_per_hour' in idea.metadata
        assert 'author' in idea.metadata
    
    def test_process_with_external_url(self):
        """Test that external URLs are captured in metadata."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'score_dictionary': json.dumps({
                'score': 500,
                'platform_specific': {
                    'url': 'https://example.com/article'
                }
            }),
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert 'external_url' in idea.metadata
        assert idea.metadata['external_url'] == 'https://example.com/article'
    
    def test_process_source_url_generation(self):
        """Test that HackerNews source URL is generated correctly."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.source_url == "https://news.ycombinator.com/item?id=12345"
    
    def test_process_source_created_at(self):
        """Test that source creation timestamp is extracted."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'score_dictionary': json.dumps({
                'platform_specific': {
                    'time': 1234567890
                }
            }),
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.source_created_at is not None
    
    def test_process_with_video_content(self):
        """Test content type detection for video URLs."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'score_dictionary': json.dumps({
                'platform_specific': {
                    'url': 'https://youtube.com/watch?v=123'
                }
            }),
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.source_type == ContentType.VIDEO
    
    def test_process_with_text_content(self):
        """Test content type defaults to TEXT."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.source_type == ContentType.TEXT
    
    def test_process_empty_tags(self):
        """Test processing record with empty tags."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': '',
            'score': 100.0,
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.keywords == []
    
    def test_process_description_truncation(self):
        """Test that long descriptions are truncated."""
        long_description = 'A' * 1000
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': long_description,
            'tags': 'story',
            'score': 100.0,
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        # MAX_DESCRIPTION_LENGTH is 500
        assert len(idea.description) == 500
        assert len(idea.content) == 1000
    
    def test_process_with_dict_score_dictionary(self):
        """Test processing when score_dictionary is already a dict."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'score_dictionary': {
                'score': 500,
                'descendants': 150
            },
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.title == 'Test Story'
        assert 'hn_score' in idea.metadata
    
    def test_process_category_set(self):
        """Test that category is set to 'hackernews'."""
        record = {
            'id': 1,
            'source': 'hackernews_frontpage',
            'source_id': '12345',
            'title': 'Test Story',
            'description': 'Test',
            'tags': 'story',
            'score': 100.0,
            'created_at': datetime.now()
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea.category == 'hackernews'
