"""Tests for Database class."""

import pytest
import tempfile
from pathlib import Path
from src.core.database import Database


class TestDatabase:
    """Test cases for Database class."""
    
    def test_database_initialization(self):
        """Test that Database can be initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.s3db"
            db = Database(str(db_path), interactive=False)
            
            assert db is not None
            assert db.db_path == str(db_path)
    
    def test_database_insert_idea(self):
        """Test inserting an idea into database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.s3db"
            db = Database(str(db_path), interactive=False)
            
            # Insert a test idea
            success = db.insert_idea(
                source='tiktok_test',
                source_id='12345',
                title='Test Video',
                description='Test description',
                tags='test,video',
                score=5.5,
                score_dictionary='{"engagement_rate": 5.5}'
            )
            
            assert success is True
    
    def test_database_get_idea(self):
        """Test retrieving an idea from database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.s3db"
            db = Database(str(db_path), interactive=False)
            
            # Insert a test idea
            db.insert_idea(
                source='tiktok_test',
                source_id='12345',
                title='Test Video',
                description='Test description',
                tags='test,video',
                score=5.5
            )
            
            # Retrieve the idea
            idea = db.get_idea('tiktok_test', '12345')
            
            assert idea is not None
            assert idea['source_id'] == '12345'
            assert idea['title'] == 'Test Video'
    
    def test_database_duplicate_handling(self):
        """Test that duplicate ideas are handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.s3db"
            db = Database(str(db_path), interactive=False)
            
            # Insert a test idea
            success1 = db.insert_idea(
                source='tiktok_test',
                source_id='12345',
                title='Test Video',
                description='Test description'
            )
            
            # Insert the same idea again (should update)
            success2 = db.insert_idea(
                source='tiktok_test',
                source_id='12345',
                title='Updated Video',
                description='Updated description'
            )
            
            assert success1 is True  # First insert
            assert success2 is False  # Second is update
            
            # Verify the update
            idea = db.get_idea('tiktok_test', '12345')
            assert idea['title'] == 'Updated Video'
    
    def test_database_statistics(self):
        """Test database statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.s3db"
            db = Database(str(db_path), interactive=False)
            
            # Insert some test ideas
            db.insert_idea(source='tiktok_test', source_id='1', title='Test 1')
            db.insert_idea(source='tiktok_test', source_id='2', title='Test 2')
            db.insert_idea(source='tiktok_trending', source_id='3', title='Test 3')
            
            # Get statistics
            stats = db.get_statistics()
            
            assert stats['total'] == 3
            assert 'tiktok_test' in stats['by_source']
            assert stats['by_source']['tiktok_test'] == 2
