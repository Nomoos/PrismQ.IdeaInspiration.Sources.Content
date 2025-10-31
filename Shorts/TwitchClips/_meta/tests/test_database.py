"""Tests for database operations."""

import pytest
import tempfile
from pathlib import Path
from src.core.database import Database


def test_database_initialization():
    """Test database initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        assert Path(db_path).exists()
        assert db.db_path == str(db_path)


def test_insert_idea():
    """Test inserting an idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert new idea
        success = db.insert_idea(
            source='twitch_clips',
            source_id='test_clip_1',
            title='Test Clip',
            description='Test description',
            tags='test,clip',
            score=100.0
        )
        
        assert success is True


def test_insert_duplicate_idea():
    """Test inserting a duplicate idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert first time
        success1 = db.insert_idea(
            source='twitch_clips',
            source_id='test_clip_1',
            title='Test Clip',
            description='Test description',
            tags='test,clip',
            score=100.0
        )
        
        # Insert duplicate
        success2 = db.insert_idea(
            source='twitch_clips',
            source_id='test_clip_1',
            title='Test Clip Updated',
            description='Updated description',
            tags='test,clip,updated',
            score=200.0
        )
        
        assert success1 is True  # First insert
        assert success2 is False  # Duplicate (updated)


def test_get_idea():
    """Test retrieving an idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert idea
        db.insert_idea(
            source='twitch_clips',
            source_id='test_clip_1',
            title='Test Clip',
            description='Test description',
            tags='test,clip',
            score=100.0
        )
        
        # Retrieve idea
        idea = db.get_idea('twitch_clips', 'test_clip_1')
        
        assert idea is not None
        assert idea['source'] == 'twitch_clips'
        assert idea['source_id'] == 'test_clip_1'
        assert idea['title'] == 'Test Clip'


def test_get_all_ideas():
    """Test retrieving all ideas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert multiple ideas
        db.insert_idea(
            source='twitch_clips',
            source_id='clip_1',
            title='Clip 1',
            description='Description 1'
        )
        
        db.insert_idea(
            source='twitch_clips',
            source_id='clip_2',
            title='Clip 2',
            description='Description 2'
        )
        
        # Get all ideas
        ideas = db.get_all_ideas()
        
        assert len(ideas) == 2
        assert ideas[0]['source_id'] in ['clip_1', 'clip_2']
        assert ideas[1]['source_id'] in ['clip_1', 'clip_2']


def test_mark_as_processed():
    """Test marking an idea as processed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert idea
        db.insert_idea(
            source='twitch_clips',
            source_id='test_clip_1',
            title='Test Clip'
        )
        
        # Mark as processed
        success = db.mark_as_processed('twitch_clips', 'test_clip_1')
        
        assert success is True
        
        # Verify it's marked (SQLite returns 1 for True)
        idea = db.get_idea('twitch_clips', 'test_clip_1')
        assert idea['processed'] == True or idea['processed'] == 1
