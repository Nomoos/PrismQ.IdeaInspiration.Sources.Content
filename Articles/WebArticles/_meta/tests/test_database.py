"""Tests for database module."""

import tempfile
from pathlib import Path
import pytest
from src.core.database import Database


def test_database_creation():
    """Test database creation and initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        db = Database(str(db_path), interactive=False)
        
        assert Path(db_path).exists()
        assert db.database_url.startswith("sqlite:///")


def test_insert_article():
    """Test article insertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        db = Database(str(db_path), interactive=False)
        
        # Insert new article
        result = db.insert_article(
            source="web_article",
            source_id="test123",
            title="Test Article",
            description="Test description",
            content="Test content",
            tags="tag1,tag2",
            author="Test Author",
            url="https://example.com/test",
            score=8.5
        )
        
        assert result is True  # Should be inserted
        
        # Try to insert duplicate
        result2 = db.insert_article(
            source="web_article",
            source_id="test123",
            title="Test Article Updated",
            description="Updated description",
            content="Updated content",
            tags="tag1,tag2,tag3",
            author="Test Author",
            url="https://example.com/test",
            score=9.0
        )
        
        assert result2 is False  # Should be updated, not inserted


def test_get_all_articles():
    """Test retrieving all articles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        db = Database(str(db_path), interactive=False)
        
        # Insert test articles
        for i in range(5):
            db.insert_article(
                source="web_article",
                source_id=f"test{i}",
                title=f"Test Article {i}",
                description=f"Test description {i}",
                score=float(i)
            )
        
        # Get all articles
        articles = db.get_all_articles(limit=10)
        assert len(articles) == 5


def test_count_articles():
    """Test article counting."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        db = Database(str(db_path), interactive=False)
        
        # Insert test articles
        for i in range(3):
            db.insert_article(
                source="web_article",
                source_id=f"test{i}",
                title=f"Test Article {i}",
                score=float(i)
            )
        
        count = db.count_articles()
        assert count == 3


def test_count_by_source():
    """Test counting articles by source."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.s3db"
        db = Database(str(db_path), interactive=False)
        
        # Insert articles from different sources
        db.insert_article(source="web_article_url", source_id="test1", title="Test 1", score=1.0)
        db.insert_article(source="web_article_url", source_id="test2", title="Test 2", score=2.0)
        db.insert_article(source="web_article_rss", source_id="test3", title="Test 3", score=3.0)
        
        url_count = db.count_by_source("web_article_url")
        rss_count = db.count_by_source("web_article_rss")
        
        assert url_count == 2
        assert rss_count == 1
