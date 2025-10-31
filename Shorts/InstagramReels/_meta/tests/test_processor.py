"""Tests for IdeaProcessor class."""

import pytest
import json
from src.core.idea_processor import IdeaProcessor, ContentType


class TestIdeaProcessor:
    """Test IdeaProcessor class."""
    
    def test_process_record(self):
        """Test processing a single record."""
        record = {
            'id': 1,
            'source': 'instagram_reels_test',
            'source_id': 'test123',
            'title': 'Test Reel',
            'description': 'Test description #test #reel',
            'tags': 'test,reel',
            'score': 5.0,
            'score_dictionary': json.dumps({
                'engagement_rate': 5.0,
                'plays_count': 1000,
                'like_count': 50,
                'author_username': 'testuser'
            })
        }
        
        idea = IdeaProcessor.process_record(record)
        
        assert idea.title == 'Test Reel'
        assert idea.source_type == ContentType.VIDEO
        assert idea.source_id == 'test123'
        assert 'test' in idea.keywords
        assert 'reel' in idea.keywords
    
    def test_process_records(self):
        """Test processing multiple records."""
        records = [
            {
                'id': 1,
                'source': 'instagram_reels_test',
                'source_id': 'test1',
                'title': 'Test 1',
                'description': 'Description 1',
                'tags': 'tag1',
                'score': 5.0,
                'score_dictionary': '{}'
            },
            {
                'id': 2,
                'source': 'instagram_reels_test',
                'source_id': 'test2',
                'title': 'Test 2',
                'description': 'Description 2',
                'tags': 'tag2',
                'score': 3.0,
                'score_dictionary': '{}'
            }
        ]
        
        ideas = IdeaProcessor.process_records(records)
        
        assert len(ideas) == 2
        assert ideas[0].title == 'Test 1'
        assert ideas[1].title == 'Test 2'
    
    def test_to_json(self):
        """Test converting ideas to JSON."""
        records = [
            {
                'id': 1,
                'source': 'instagram_reels_test',
                'source_id': 'test1',
                'title': 'Test 1',
                'description': 'Description 1',
                'tags': 'tag1',
                'score': 5.0,
                'score_dictionary': '{}'
            }
        ]
        
        ideas = IdeaProcessor.process_records(records)
        json_output = IdeaProcessor.to_json(ideas)
        
        assert isinstance(json_output, str)
        data = json.loads(json_output)
        assert len(data) == 1
        assert data[0]['title'] == 'Test 1'
