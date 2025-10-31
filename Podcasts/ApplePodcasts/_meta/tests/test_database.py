"""Tests for ApplePodcasts database module."""

import pytest
import tempfile
import os

from core.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = Database(db_path, interactive=False)
    yield db
    
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_database_initialization(temp_db):
    """Test database initialization creates tables."""
    # Check that we can count ideas (table exists)
    count = temp_db.count_ideas()
    assert count == 0


def test_insert_idea(temp_db):
    """Test inserting an idea."""
    success = temp_db.insert_idea(
        source='apple_podcasts',
        source_id='123456',
        title='Test Podcast Episode',
        description='Test description',
        tags='comedy,business',
        score=96.0,
        score_dictionary={'rating': 4.8, 'engagement_estimate': 96.0}
    )
    assert success is True


def test_insert_duplicate_idea(temp_db):
    """Test that duplicate ideas are updated, not inserted twice."""
    # Insert first idea
    temp_db.insert_idea(
        source='apple_podcasts',
        source_id='123456',
        title='Original Title',
        description='Original description',
        score=80.0
    )
    
    # Insert duplicate with updated info
    success = temp_db.insert_idea(
        source='apple_podcasts',
        source_id='123456',
        title='Updated Title',
        description='Updated description',
        score=90.0
    )
    
    # Second insert should return False (update, not insert)
    assert success is False
    
    # Verify only one entry exists
    ideas = temp_db.get_all_ideas()
    assert len(ideas) == 1
    assert ideas[0]['title'] == 'Updated Title'
    assert ideas[0]['score'] == 90.0


def test_get_idea(temp_db):
    """Test retrieving a specific idea."""
    temp_db.insert_idea(
        source='apple_podcasts',
        source_id='789012',
        title='Test Episode',
        description='Test description'
    )
    
    idea = temp_db.get_idea('apple_podcasts', '789012')
    assert idea is not None
    assert idea['title'] == 'Test Episode'
    assert idea['source_id'] == '789012'


def test_get_all_ideas(temp_db):
    """Test retrieving all ideas."""
    # Insert multiple ideas
    for i in range(5):
        temp_db.insert_idea(
            source='apple_podcasts',
            source_id=f'id_{i}',
            title=f'Episode {i}',
            score=float(i * 10)
        )
    
    ideas = temp_db.get_all_ideas(limit=10)
    assert len(ideas) == 5


def test_count_ideas(temp_db):
    """Test counting ideas."""
    # Insert test ideas
    for i in range(3):
        temp_db.insert_idea(
            source='apple_podcasts',
            source_id=f'id_{i}',
            title=f'Episode {i}'
        )
    
    count = temp_db.count_ideas()
    assert count == 3


def test_count_by_source(temp_db):
    """Test counting ideas by source."""
    # Insert ideas from different sources
    temp_db.insert_idea(source='apple_podcasts_charts', source_id='1', title='E1')
    temp_db.insert_idea(source='apple_podcasts_charts', source_id='2', title='E2')
    temp_db.insert_idea(source='apple_podcasts_show', source_id='3', title='E3')
    
    count_charts = temp_db.count_by_source('apple_podcasts_charts')
    count_show = temp_db.count_by_source('apple_podcasts_show')
    
    assert count_charts == 2
    assert count_show == 1
