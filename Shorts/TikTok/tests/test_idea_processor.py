"""Tests for IdeaProcessor class."""

import pytest
from src.core.idea_processor import IdeaProcessor, ContentType


class TestIdeaProcessor:
    """Test cases for IdeaProcessor class."""
    
    def test_process_tiktok_record(self):
        """Test processing a TikTok record."""
        record = {
            'source_id': '12345',
            'title': 'Test Video',
            'description': 'Test description',
            'tags': 'test,video,tiktok',
            'score': 5.5,
            'score_dictionary': {
                'view_count': 1000,
                'like_count': 100,
                'platform_specific': {
                    'username': 'testuser',
                    'created_time': 1234567890
                }
            }
        }
        
        idea = IdeaProcessor.process(record)
        
        assert idea is not None
        assert idea.title == 'Test Video'
        assert idea.source_id == '12345'
        assert idea.source_type == ContentType.VIDEO
        assert len(idea.keywords) == 3
        assert 'test' in idea.keywords
    
    def test_process_missing_title(self):
        """Test that processing fails without title."""
        record = {
            'source_id': '12345',
            'description': 'Test description'
        }
        
        with pytest.raises(ValueError, match="must have a title"):
            IdeaProcessor.process(record)
    
    def test_process_missing_source_id(self):
        """Test that processing fails without source_id."""
        record = {
            'title': 'Test Video',
            'description': 'Test description'
        }
        
        with pytest.raises(ValueError, match="must have a source_id"):
            IdeaProcessor.process(record)
    
    def test_build_metadata(self):
        """Test metadata building."""
        record = {
            'source_id': '12345',
            'title': 'Test Video'
        }
        
        score_dict = {
            'view_count': 1000,
            'like_count': 100,
            'comment_count': 20,
            'share_count': 10,
            'platform_specific': {
                'username': 'testuser',
                'duration_seconds': 30
            }
        }
        
        metadata = IdeaProcessor._build_metadata(record, score_dict)
        
        assert 'platform' in metadata
        assert metadata['platform'] == 'tiktok'
        assert metadata['views'] == '1000'
        assert metadata['likes'] == '100'
    
    def test_process_batch(self):
        """Test batch processing."""
        records = [
            {
                'source_id': '1',
                'title': 'Video 1',
                'description': 'Desc 1',
                'tags': 'test',
                'score_dictionary': {}
            },
            {
                'source_id': '2',
                'title': 'Video 2',
                'description': 'Desc 2',
                'tags': 'test',
                'score_dictionary': {}
            }
        ]
        
        ideas = IdeaProcessor.process_batch(records)
        
        assert len(ideas) == 2
        assert ideas[0].title == 'Video 1'
        assert ideas[1].title == 'Video 2'
