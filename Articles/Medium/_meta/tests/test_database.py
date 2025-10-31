"""Tests for Medium source database operations."""

import pytest
import tempfile
from pathlib import Path
from src.core.database import Database
from src.core import db_utils


def test_database_creation():
    """Test that database can be created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        assert db is not None
        assert db.database_url is not None


def test_insert_idea():
    """Test that ideas can be inserted into database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert an idea
        success = db.insert_idea(
            source='medium_trending',
            source_id='test-article-123',
            title='Test Article',
            description='This is a test article',
            tags='test,article,medium',
            score=5.5
        )
        
        assert success  # Should be inserted (not updated)


def test_insert_duplicate_idea():
    """Test that duplicate ideas are updated, not re-inserted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert first time
        success1 = db.insert_idea(
            source='medium_trending',
            source_id='test-article-123',
            title='Test Article',
            description='This is a test article',
            tags='test,article',
            score=5.5
        )
        
        # Insert again with same source and source_id
        success2 = db.insert_idea(
            source='medium_trending',
            source_id='test-article-123',
            title='Test Article Updated',
            description='Updated description',
            tags='test,article,updated',
            score=6.0
        )
        
        assert success1  # First insert
        assert not success2  # Update (not insert)


def test_get_idea():
    """Test retrieving a specific idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert an idea
        db.insert_idea(
            source='medium_tag',
            source_id='test-123',
            title='Test',
            description='Test description',
            tags='test'
        )
        
        # Retrieve it
        idea = db.get_idea('medium_tag', 'test-123')
        
        assert idea is not None
        assert idea['title'] == 'Test'
        assert idea['source_id'] == 'test-123'


def test_count_ideas():
    """Test counting ideas in database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert multiple ideas
        for i in range(5):
            db.insert_idea(
                source='medium_trending',
                source_id=f'test-{i}',
                title=f'Test {i}',
                description=f'Description {i}',
                tags='test'
            )
        
        count = db.count_ideas()
        assert count == 5


def test_count_by_source():
    """Test counting ideas by source."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert ideas from different sources
        for i in range(3):
            db.insert_idea(
                source='medium_trending',
                source_id=f'trending-{i}',
                title=f'Trending {i}',
                description=f'Description {i}',
                tags='trending'
            )
        
        for i in range(2):
            db.insert_idea(
                source='medium_tag',
                source_id=f'tag-{i}',
                title=f'Tag {i}',
                description=f'Description {i}',
                tags='tag'
            )
        
        trending_count = db.count_by_source('medium_trending')
        tag_count = db.count_by_source('medium_tag')
        
        assert trending_count == 3
        assert tag_count == 2
