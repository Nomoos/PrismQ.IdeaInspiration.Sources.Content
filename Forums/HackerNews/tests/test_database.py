"""Tests for database module."""

import os
import tempfile
import pytest
from src.core.database import Database
from src.core import db_utils


class TestDatabase:
    """Test cases for Database class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.s3db')
        temp_file.close()
        db = Database(temp_file.name, interactive=False)
        yield db
        os.unlink(temp_file.name)
    
    def test_database_initialization(self, temp_db):
        """Test that database initializes correctly."""
        assert temp_db.db_path is not None
        assert temp_db.database_url.startswith("sqlite:///")
    
    def test_insert_idea(self, temp_db):
        """Test inserting an idea into the database."""
        success = temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Test Story',
            description='Test description',
            tags='story,test',
            score=100.0,
            score_dictionary={'score': 500, 'descendants': 150}
        )
        
        assert success is True
        assert temp_db.count_ideas() == 1
    
    def test_insert_duplicate_idea(self, temp_db):
        """Test that duplicate ideas update existing records."""
        temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Original Title',
            description='Original description',
            tags='story',
            score=50.0
        )
        
        success = temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Updated Title',
            description='Updated description',
            tags='story,updated',
            score=100.0
        )
        
        assert success is False
        assert temp_db.count_ideas() == 1
        
        idea = temp_db.get_idea('hackernews_frontpage', '12345')
        assert idea['title'] == 'Updated Title'
    
    def test_get_idea(self, temp_db):
        """Test retrieving a specific idea."""
        temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Test Story',
            description='Test description',
            tags='story',
            score=100.0
        )
        
        idea = temp_db.get_idea('hackernews_frontpage', '12345')
        
        assert idea is not None
        assert idea['source_id'] == '12345'
        assert idea['title'] == 'Test Story'
    
    def test_get_nonexistent_idea(self, temp_db):
        """Test retrieving a non-existent idea returns None."""
        idea = temp_db.get_idea('hackernews_frontpage', '99999')
        assert idea is None
    
    def test_get_all_ideas(self, temp_db):
        """Test retrieving all ideas."""
        for i in range(5):
            temp_db.insert_idea(
                source='hackernews_frontpage',
                source_id=str(i),
                title=f'Story {i}',
                description='Test',
                tags='story',
                score=float(i * 10)
            )
        
        ideas = temp_db.get_all_ideas(limit=10)
        assert len(ideas) == 5
    
    def test_count_ideas(self, temp_db):
        """Test counting ideas."""
        assert temp_db.count_ideas() == 0
        
        for i in range(3):
            temp_db.insert_idea(
                source='hackernews_frontpage',
                source_id=str(i),
                title=f'Story {i}',
                description='Test',
                tags='story',
                score=50.0
            )
        
        assert temp_db.count_ideas() == 3
    
    def test_count_by_source(self, temp_db):
        """Test counting ideas by source."""
        temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='1',
            title='Story 1',
            description='Test',
            tags='story',
            score=50.0
        )
        temp_db.insert_idea(
            source='hackernews_new',
            source_id='2',
            title='Story 2',
            description='Test',
            tags='story',
            score=50.0
        )
        temp_db.insert_idea(
            source='hackernews_frontpage',
            source_id='3',
            title='Story 3',
            description='Test',
            tags='story',
            score=50.0
        )
        
        assert temp_db.count_by_source('hackernews_frontpage') == 2
        assert temp_db.count_by_source('hackernews_new') == 1
        assert temp_db.count_by_source('hackernews_best') == 0


class TestDbUtils:
    """Test cases for db_utils module."""
    
    @pytest.fixture
    def temp_db_url(self):
        """Create a temporary database URL for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.s3db')
        temp_file.close()
        db_url = f"sqlite:///{temp_file.name}"
        db_utils.init_database(db_url)
        yield db_url
        os.unlink(temp_file.name)
    
    def test_init_database(self, temp_db_url):
        """Test database initialization creates tables."""
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='HackerNewsSource'"
            ))
            assert result.fetchone() is not None
    
    def test_insert_idea_utils(self, temp_db_url):
        """Test inserting idea via db_utils."""
        success = db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='123',
            title='Test',
            description='Test desc',
            tags='test',
            score=50.0
        )
        
        assert success is True
    
    def test_get_all_ideas_order_by_whitelist(self, temp_db_url):
        """Test that order_by parameter is validated against whitelist."""
        db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='123',
            title='Test',
            description='Test',
            tags='test',
            score=50.0
        )
        
        # Valid column should work
        ideas = db_utils.get_all_ideas(temp_db_url, limit=10, order_by='score')
        assert len(ideas) == 1
        
        # Invalid column should default to 'score'
        ideas = db_utils.get_all_ideas(temp_db_url, limit=10, order_by='invalid_column')
        assert len(ideas) == 1
    
    def test_clear_all_ideas(self, temp_db_url):
        """Test clearing all ideas."""
        db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='1',
            title='Test 1',
            description='Test',
            tags='test',
            score=50.0
        )
        db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='2',
            title='Test 2',
            description='Test',
            tags='test',
            score=50.0
        )
        
        deleted = db_utils.clear_all_ideas(temp_db_url)
        assert deleted == 2
        assert db_utils.count_ideas(temp_db_url) == 0
    
    def test_get_unprocessed_ideas(self, temp_db_url):
        """Test retrieving unprocessed ideas."""
        db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='1',
            title='Test 1',
            description='Test',
            tags='test',
            score=50.0
        )
        
        unprocessed = db_utils.get_unprocessed_ideas(temp_db_url, limit=10)
        assert len(unprocessed) == 1
    
    def test_mark_as_processed(self, temp_db_url):
        """Test marking an idea as processed."""
        db_utils.insert_idea(
            temp_db_url,
            source='hackernews_test',
            source_id='1',
            title='Test 1',
            description='Test',
            tags='test',
            score=50.0
        )
        
        ideas = db_utils.get_all_ideas(temp_db_url, limit=10)
        record_id = ideas[0]['id']
        
        db_utils.mark_as_processed(temp_db_url, record_id)
        
        unprocessed = db_utils.get_unprocessed_ideas(temp_db_url, limit=10)
        assert len(unprocessed) == 0
