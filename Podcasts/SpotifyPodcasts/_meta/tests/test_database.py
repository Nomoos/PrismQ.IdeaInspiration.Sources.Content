"""Tests for database operations."""

import pytest
import tempfile
from pathlib import Path
from src.core import db_utils


def test_init_database():
    """Test database initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Database file should exist
        assert db_path.exists()


def test_insert_idea():
    """Test inserting an idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert a test idea
        result = db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test123",
            title="Test Episode",
            description="Test description",
            tags="test,podcast",
            score=5.0,
            score_dictionary='{"engagement_estimate": 5.0}'
        )
        
        # Should return True for new insert
        assert result is True


def test_insert_duplicate_idea():
    """Test inserting duplicate ideas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert first time
        result1 = db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test123",
            title="Test Episode",
            description="Test description"
        )
        
        # Insert duplicate
        result2 = db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test123",
            title="Test Episode Updated",
            description="Updated description"
        )
        
        # First insert should return True, duplicate should return False
        assert result1 is True
        assert result2 is False


def test_get_idea():
    """Test retrieving a specific idea."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert a test idea
        db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test123",
            title="Test Episode",
            description="Test description"
        )
        
        # Retrieve the idea
        idea = db_utils.get_idea(database_url, "spotify_trending", "test123")
        
        assert idea is not None
        assert idea['source'] == "spotify_trending"
        assert idea['source_id'] == "test123"
        assert idea['title'] == "Test Episode"


def test_get_all_ideas():
    """Test retrieving all ideas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert multiple ideas
        for i in range(5):
            db_utils.insert_idea(
                database_url,
                source="spotify_trending",
                source_id=f"test{i}",
                title=f"Test Episode {i}"
            )
        
        # Get all ideas
        ideas = db_utils.get_all_ideas(database_url)
        
        assert len(ideas) == 5


def test_get_unprocessed_records():
    """Test retrieving unprocessed records."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert ideas
        db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test1",
            title="Test Episode 1"
        )
        
        # Get unprocessed records
        records = db_utils.get_unprocessed_records(database_url)
        
        assert len(records) == 1
        assert records[0]['processed'] is False or records[0]['processed'] == 0


def test_mark_as_processed():
    """Test marking a record as processed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        database_url = f"sqlite:///{db_path}"
        
        db_utils.init_database(database_url)
        
        # Insert and get idea
        db_utils.insert_idea(
            database_url,
            source="spotify_trending",
            source_id="test1",
            title="Test Episode 1"
        )
        
        records = db_utils.get_unprocessed_records(database_url)
        assert len(records) == 1
        
        record_id = records[0]['id']
        
        # Mark as processed
        db_utils.mark_as_processed(database_url, record_id)
        
        # Should have no unprocessed records now
        unprocessed = db_utils.get_unprocessed_records(database_url)
        assert len(unprocessed) == 0
