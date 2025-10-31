"""Tests for Database class."""

import pytest
import json
from pathlib import Path
from src.core.database import Database


class TestDatabase:
    """Test Database class."""
    
    def test_database_creation(self, tmp_path):
        """Test database creation."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        assert Path(db_path).exists()
    
    def test_insert_idea(self, tmp_path):
        """Test inserting an idea."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        result = db.insert_idea(
            source="instagram_reels_test",
            source_id="test123",
            title="Test Reel",
            description="Test description",
            tags="test,reel",
            score=5.0,
            score_dictionary={"engagement_rate": 5.0}
        )
        
        assert result == True  # First insert should return True
    
    def test_insert_duplicate_idea(self, tmp_path):
        """Test inserting duplicate idea."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert first time
        db.insert_idea(
            source="instagram_reels_test",
            source_id="test123",
            title="Test Reel",
            description="Test description"
        )
        
        # Insert second time (duplicate)
        result = db.insert_idea(
            source="instagram_reels_test",
            source_id="test123",
            title="Test Reel Updated",
            description="Updated description"
        )
        
        assert result == False  # Duplicate should return False
    
    def test_get_stats(self, tmp_path):
        """Test getting database statistics."""
        db_path = tmp_path / "test.db"
        db = Database(str(db_path), interactive=False)
        
        # Insert some ideas
        db.insert_idea(
            source="instagram_reels_test",
            source_id="test1",
            title="Test 1"
        )
        db.insert_idea(
            source="instagram_reels_test",
            source_id="test2",
            title="Test 2"
        )
        
        stats = db.get_stats()
        
        assert stats['total'] == 2
        assert stats['unprocessed'] == 2
        assert 'instagram_reels_test' in stats['by_source']
