"""Tests for Medium source metrics."""

import pytest
from src.core.metrics import UniversalMetrics
from datetime import datetime


def test_metrics_from_medium():
    """Test creating UniversalMetrics from Medium article data."""
    article_data = {
        'source_id': 'test-article-123',
        'title': 'Test Article',
        'description': 'Test description',
        'tags': ['ai', 'machine-learning', 'python'],
        'author': {
            'username': 'testauthor',
            'followers': 5000
        },
        'metrics': {
            'claps': 1200,
            'responses': 45,
            'reading_time_min': 7,
            'views': 10000
        },
        'publish_date': '2024-01-01T00:00:00Z'
    }
    
    metrics = UniversalMetrics.from_medium(article_data)
    
    assert metrics.platform == 'medium'
    assert metrics.content_type == 'article'
    assert metrics.like_count == 1200  # Claps mapped to likes
    assert metrics.comment_count == 45  # Responses mapped to comments
    assert metrics.view_count == 10000
    assert metrics.duration_seconds == 7 * 60  # Reading time in seconds
    assert metrics.author_follower_count == 5000
    assert metrics.tag_count == 3


def test_metrics_engagement_calculation():
    """Test that engagement metrics are calculated correctly."""
    article_data = {
        'source_id': 'test-article-123',
        'title': 'Test Article',
        'description': 'Test description',
        'tags': ['test'],
        'author': {'username': 'test'},
        'metrics': {
            'claps': 100,
            'responses': 10,
            'reading_time_min': 5,
            'views': 1000
        }
    }
    
    metrics = UniversalMetrics.from_medium(article_data)
    
    # Engagement rate should be calculated
    assert metrics.engagement_rate is not None
    # (100 claps + 10 responses) / 1000 views * 100 = 11%
    # Note: shares are typically 0 for Medium as they're not easily accessible
    assert metrics.engagement_rate == pytest.approx(11.0, rel=0.01)


def test_metrics_to_dict():
    """Test converting metrics to dictionary."""
    article_data = {
        'source_id': 'test-article',
        'title': 'Test',
        'description': 'Test',
        'tags': ['test'],
        'author': {'username': 'test'},
        'metrics': {
            'claps': 50,
            'responses': 5,
            'reading_time_min': 3,
            'views': 500
        }
    }
    
    metrics = UniversalMetrics.from_medium(article_data)
    metrics_dict = metrics.to_dict()
    
    assert isinstance(metrics_dict, dict)
    assert 'platform' in metrics_dict
    assert metrics_dict['platform'] == 'medium'
    assert 'like_count' in metrics_dict
    assert metrics_dict['like_count'] == 50


def test_metrics_with_minimal_data():
    """Test metrics creation with minimal article data."""
    article_data = {
        'source_id': 'minimal-article',
        'title': 'Minimal Article',
        'description': '',
        'tags': [],
        'author': {'username': 'unknown'},
        'metrics': {
            'claps': 0,
            'responses': 0,
            'reading_time_min': 0
        }
    }
    
    metrics = UniversalMetrics.from_medium(article_data)
    
    # Should still create metrics object
    assert metrics is not None
    assert metrics.platform == 'medium'
    assert metrics.like_count == 0
    assert metrics.comment_count == 0
