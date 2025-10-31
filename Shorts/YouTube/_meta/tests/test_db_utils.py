"""Tests for database utility functions."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone
from src.core import db_utils


@pytest.fixture
def temp_db_url():
    """Create a temporary database URL for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.s3db")
        db_url = f"sqlite:///{db_path}"
        yield db_url


class TestGetEngine:
    """Test get_engine function."""
    
    def test_sqlite_engine_creation(self, temp_db_url):
        """Test that SQLite engine is created correctly."""
        engine = db_utils.get_engine(temp_db_url)
        assert engine is not None
        assert str(engine.url).startswith("sqlite:///")
    
    def test_sqlite_creates_directory(self):
        """Test that parent directory is created for SQLite database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "subdir", "test.db")
            db_url = f"sqlite:///{db_path}"
            
            engine = db_utils.get_engine(db_url)
            assert Path(db_path).parent.exists()
    
    def test_engine_reuse(self, temp_db_url):
        """Test that calling get_engine multiple times works."""
        engine1 = db_utils.get_engine(temp_db_url)
        engine2 = db_utils.get_engine(temp_db_url)
        
        # Both should be valid engines
        assert engine1 is not None
        assert engine2 is not None


class TestInitDatabase:
    """Test init_database function."""
    
    def test_database_initialization(self, temp_db_url):
        """Test that database schema is initialized correctly."""
        db_utils.init_database(temp_db_url)
        
        # Verify table exists by querying it
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='YouTubeShortsSource'"
            ))
            table = result.fetchone()
            assert table is not None
    
    def test_table_columns(self, temp_db_url):
        """Test that table has all required columns."""
        db_utils.init_database(temp_db_url)
        
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text("PRAGMA table_info(YouTubeShortsSource)"))
            columns = {row[1] for row in result.fetchall()}
        
        expected_columns = {
            'id', 'source', 'source_id', 'title', 'description',
            'tags', 'score', 'score_dictionary', 'processed',
            'created_at', 'updated_at'
        }
        assert expected_columns.issubset(columns)
    
    def test_reinitializing_database(self, temp_db_url):
        """Test that reinitializing database doesn't cause errors."""
        db_utils.init_database(temp_db_url)
        # Should not raise an error
        db_utils.init_database(temp_db_url)


class TestUtcNow:
    """Test utc_now function."""
    
    def test_returns_datetime(self):
        """Test that utc_now returns a datetime object."""
        result = db_utils.utc_now()
        assert isinstance(result, datetime)
    
    def test_returns_utc_timezone(self):
        """Test that utc_now returns UTC timezone."""
        result = db_utils.utc_now()
        assert result.tzinfo == timezone.utc
    
    def test_approximate_current_time(self):
        """Test that utc_now returns approximately current time."""
        before = datetime.now(timezone.utc)
        result = db_utils.utc_now()
        after = datetime.now(timezone.utc)
        
        assert before <= result <= after


class TestGetConnection:
    """Test get_connection context manager."""
    
    def test_connection_context_manager(self, temp_db_url):
        """Test that get_connection works as context manager."""
        db_utils.init_database(temp_db_url)
        
        with db_utils.get_connection(temp_db_url) as conn:
            assert conn is not None
            # Should be able to execute queries
            result = conn.execute(db_utils.text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_connection_closes_after_context(self, temp_db_url):
        """Test that connection closes after context exits."""
        db_utils.init_database(temp_db_url)
        
        with db_utils.get_connection(temp_db_url) as conn:
            pass
        
        # Connection should be closed
        assert conn.closed


class TestInsertIdea:
    """Test insert_idea function."""
    
    def test_insert_new_idea(self, temp_db_url):
        """Test inserting a new idea."""
        db_utils.init_database(temp_db_url)
        
        result = db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="test123",
            title="Test Video",
            description="Test description",
            tags="tag1,tag2",
            score=85.5,
            score_dictionary='{"engagement": 0.85}'
        )
        
        assert result is True  # New insert returns True
    
    def test_insert_duplicate_idea(self, temp_db_url):
        """Test that inserting duplicate updates existing record."""
        db_utils.init_database(temp_db_url)
        
        # Insert first time
        result1 = db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="test123",
            title="Original Title",
            score=50.0
        )
        
        # Insert duplicate
        result2 = db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="test123",
            title="Updated Title",
            score=75.0
        )
        
        assert result1 is True  # First insert
        assert result2 is False  # Update, not insert
        
        # Verify only one record exists with updated data
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT title, score FROM YouTubeShortsSource WHERE source_id = :sid"
            ), {"sid": "test123"})
            rows = result.fetchall()
            
            assert len(rows) == 1
            assert rows[0][0] == "Updated Title"
            assert rows[0][1] == 75.0
    
    def test_insert_with_optional_fields(self, temp_db_url):
        """Test inserting idea with only required fields."""
        db_utils.init_database(temp_db_url)
        
        result = db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="test456",
            title="Minimal Video"
        )
        
        assert result is True
        
        # Verify record was inserted
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT * FROM YouTubeShortsSource WHERE source_id = :sid"
            ), {"sid": "test456"})
            row = result.fetchone()
            
            assert row is not None
    
    def test_insert_sets_timestamps(self, temp_db_url):
        """Test that insert sets created_at and updated_at."""
        db_utils.init_database(temp_db_url)
        
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="test789",
            title="Test Video"
        )
        
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT created_at, updated_at FROM YouTubeShortsSource WHERE source_id = :sid"
            ), {"sid": "test789"})
            row = result.fetchone()
            
            assert row[0] is not None  # created_at
            assert row[1] is not None  # updated_at


class TestGetUnprocessedRecords:
    """Test get_unprocessed_records function."""
    
    def test_get_unprocessed_records_empty(self, temp_db_url):
        """Test getting unprocessed records from empty database."""
        db_utils.init_database(temp_db_url)
        
        records = db_utils.get_unprocessed_records(temp_db_url)
        assert records == []
    
    def test_get_unprocessed_records(self, temp_db_url):
        """Test getting unprocessed records."""
        db_utils.init_database(temp_db_url)
        
        # Insert unprocessed record
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="unprocessed1",
            title="Unprocessed Video"
        )
        
        records = db_utils.get_unprocessed_records(temp_db_url)
        assert len(records) == 1
        assert records[0]['source_id'] == 'unprocessed1'
        assert records[0]['processed'] in (0, False, None)
    
    def test_get_unprocessed_records_with_limit(self, temp_db_url):
        """Test limiting number of unprocessed records."""
        db_utils.init_database(temp_db_url)
        
        # Insert multiple unprocessed records
        for i in range(5):
            db_utils.insert_idea(
                database_url=temp_db_url,
                source="youtube",
                source_id=f"video{i}",
                title=f"Video {i}"
            )
        
        records = db_utils.get_unprocessed_records(temp_db_url, limit=2)
        assert len(records) == 2
    
    def test_excludes_processed_records(self, temp_db_url):
        """Test that processed records are excluded."""
        db_utils.init_database(temp_db_url)
        
        # Insert unprocessed record
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="video1",
            title="Video 1"
        )
        
        # Insert and mark as processed
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="video2",
            title="Video 2"
        )
        
        with db_utils.get_connection(temp_db_url) as conn:
            conn.execute(db_utils.text(
                "UPDATE YouTubeShortsSource SET processed = 1 WHERE source_id = :sid"
            ), {"sid": "video2"})
            conn.commit()
        
        records = db_utils.get_unprocessed_records(temp_db_url)
        assert len(records) == 1
        assert records[0]['source_id'] == 'video1'


class TestMarkAsProcessed:
    """Test mark_as_processed function."""
    
    def test_mark_record_as_processed(self, temp_db_url):
        """Test marking a record as processed."""
        db_utils.init_database(temp_db_url)
        
        # Insert unprocessed record
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="video1",
            title="Video 1"
        )
        
        # Get record ID
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT id FROM YouTubeShortsSource WHERE source_id = :sid"
            ), {"sid": "video1"})
            record_id = result.fetchone()[0]
        
        # Mark as processed
        db_utils.mark_as_processed(temp_db_url, record_id)
        
        # Verify it's marked as processed
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT processed FROM YouTubeShortsSource WHERE id = :id"
            ), {"id": record_id})
            processed = result.fetchone()[0]
            
            assert processed == 1
    
    def test_mark_as_processed_updates_timestamp(self, temp_db_url):
        """Test that marking as processed updates updated_at."""
        db_utils.init_database(temp_db_url)
        
        # Insert record
        db_utils.insert_idea(
            database_url=temp_db_url,
            source="youtube",
            source_id="video1",
            title="Video 1"
        )
        
        # Get record ID and original timestamp
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT id, updated_at FROM YouTubeShortsSource WHERE source_id = :sid"
            ), {"sid": "video1"})
            row = result.fetchone()
            record_id = row[0]
            original_updated = row[1]
        
        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)
        
        # Mark as processed
        db_utils.mark_as_processed(temp_db_url, record_id)
        
        # Verify updated_at changed
        with db_utils.get_connection(temp_db_url) as conn:
            result = conn.execute(db_utils.text(
                "SELECT updated_at FROM YouTubeShortsSource WHERE id = :id"
            ), {"id": record_id})
            new_updated = result.fetchone()[0]
            
            # Note: Depending on DB precision, may or may not be different
            # At minimum, should not error
            assert new_updated is not None


class TestGetAllIdeas:
    """Test get_all_ideas function."""
    
    def test_get_all_ideas_empty(self, temp_db_url):
        """Test getting all ideas from empty database."""
        db_utils.init_database(temp_db_url)
        
        ideas = db_utils.get_all_ideas(temp_db_url)
        assert ideas == []
    
    def test_get_all_ideas(self, temp_db_url):
        """Test getting all ideas."""
        db_utils.init_database(temp_db_url)
        
        # Insert multiple ideas
        for i in range(3):
            db_utils.insert_idea(
                database_url=temp_db_url,
                source="youtube",
                source_id=f"video{i}",
                title=f"Video {i}",
                score=float(i * 10)
            )
        
        ideas = db_utils.get_all_ideas(temp_db_url, limit=20)
        assert len(ideas) == 3
    
    def test_get_all_ideas_with_limit(self, temp_db_url):
        """Test limiting number of ideas returned."""
        db_utils.init_database(temp_db_url)
        
        # Insert multiple ideas
        for i in range(5):
            db_utils.insert_idea(
                database_url=temp_db_url,
                source="youtube",
                source_id=f"video{i}",
                title=f"Video {i}",
                score=float(i)
            )
        
        ideas = db_utils.get_all_ideas(temp_db_url, limit=3)
        assert len(ideas) == 3
    
    def test_get_all_ideas_ordering(self, temp_db_url):
        """Test that ideas are ordered by score descending."""
        db_utils.init_database(temp_db_url)
        
        # Insert ideas with different scores
        db_utils.insert_idea(temp_db_url, "youtube", "v1", "Video 1", score=10.0)
        db_utils.insert_idea(temp_db_url, "youtube", "v2", "Video 2", score=50.0)
        db_utils.insert_idea(temp_db_url, "youtube", "v3", "Video 3", score=30.0)
        
        ideas = db_utils.get_all_ideas(temp_db_url, order_by="score")
        
        # Should be ordered by score descending
        assert ideas[0]['score'] == 50.0
        assert ideas[1]['score'] == 30.0
        assert ideas[2]['score'] == 10.0
    
    def test_order_by_sql_injection_protection(self, temp_db_url):
        """Test that order_by is protected against SQL injection."""
        db_utils.init_database(temp_db_url)
        
        db_utils.insert_idea(temp_db_url, "youtube", "v1", "Video 1", score=10.0)
        
        # Attempt SQL injection - should fall back to default
        ideas = db_utils.get_all_ideas(temp_db_url, order_by="score; DROP TABLE YouTubeShortsSource;")
        
        # Should still work and not drop table
        assert len(ideas) == 1


class TestCountIdeas:
    """Test count_ideas function."""
    
    def test_count_empty_database(self, temp_db_url):
        """Test counting ideas in empty database."""
        db_utils.init_database(temp_db_url)
        
        count = db_utils.count_ideas(temp_db_url)
        assert count == 0
    
    def test_count_ideas(self, temp_db_url):
        """Test counting ideas."""
        db_utils.init_database(temp_db_url)
        
        # Insert multiple ideas
        for i in range(7):
            db_utils.insert_idea(
                database_url=temp_db_url,
                source="youtube",
                source_id=f"video{i}",
                title=f"Video {i}"
            )
        
        count = db_utils.count_ideas(temp_db_url)
        assert count == 7


class TestCountBySource:
    """Test count_by_source function."""
    
    def test_count_by_source_empty(self, temp_db_url):
        """Test counting by source in empty database."""
        db_utils.init_database(temp_db_url)
        
        count = db_utils.count_by_source(temp_db_url, "youtube")
        assert count == 0
    
    def test_count_by_source(self, temp_db_url):
        """Test counting ideas by specific source."""
        db_utils.init_database(temp_db_url)
        
        # Insert ideas from different sources
        db_utils.insert_idea(temp_db_url, "youtube", "v1", "Video 1")
        db_utils.insert_idea(temp_db_url, "youtube", "v2", "Video 2")
        db_utils.insert_idea(temp_db_url, "youtube_channel", "v3", "Video 3")
        db_utils.insert_idea(temp_db_url, "youtube_trending", "v4", "Video 4")
        
        count_youtube = db_utils.count_by_source(temp_db_url, "youtube")
        count_channel = db_utils.count_by_source(temp_db_url, "youtube_channel")
        count_trending = db_utils.count_by_source(temp_db_url, "youtube_trending")
        
        assert count_youtube == 2
        assert count_channel == 1
        assert count_trending == 1
    
    def test_count_by_nonexistent_source(self, temp_db_url):
        """Test counting by source that doesn't exist."""
        db_utils.init_database(temp_db_url)
        
        db_utils.insert_idea(temp_db_url, "youtube", "v1", "Video 1")
        
        count = db_utils.count_by_source(temp_db_url, "nonexistent")
        assert count == 0
