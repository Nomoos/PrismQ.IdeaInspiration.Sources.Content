"""Tests for metrics module."""

import pytest
from datetime import datetime
from src.core.metrics import UniversalMetrics


def test_universal_metrics_initialization():
    """Test UniversalMetrics initialization."""
    metrics = UniversalMetrics(
        view_count=1000,
        like_count=100,
        comment_count=50,
        share_count=25
    )
    
    assert metrics.view_count == 1000
    assert metrics.like_count == 100
    assert metrics.comment_count == 50
    assert metrics.share_count == 25


def test_calculate_derived_metrics():
    """Test calculation of derived metrics."""
    metrics = UniversalMetrics(
        view_count=1000,
        like_count=100,
        comment_count=50,
        share_count=25,
        days_since_publish=10,
        word_count=1200
    )
    
    metrics.calculate_derived_metrics()
    
    # Engagement rate should be (100 + 50 + 25) / 1000 * 100 = 17.5
    assert metrics.engagement_rate == 17.5
    
    # Views per day should be 1000 / 10 = 100
    assert metrics.views_per_day == 100.0
    
    # Quality score should be calculated
    assert metrics.quality_score is not None
    assert 0 <= metrics.quality_score <= 10
    
    # Freshness score should be calculated
    assert metrics.freshness_score is not None
    assert 0 <= metrics.freshness_score <= 1


def test_from_article():
    """Test creating metrics from article data."""
    article_data = {
        'source': 'web_article',
        'title': 'Test Article',
        'description': 'Test description',
        'content': {
            'text': 'This is a test article with some content. ' * 100,
        },
        'tags': ['test', 'article'],
        'published_at': '2025-01-01T00:00:00',
        'metrics': {
            'view_count': 1000,
            'like_count': 100,
            'comment_count': 50,
        }
    }
    
    metrics = UniversalMetrics.from_article(article_data)
    
    assert metrics.platform == 'web_article'
    assert metrics.view_count == 1000
    assert metrics.like_count == 100
    assert metrics.word_count > 0
    assert metrics.reading_time_min > 0


def test_to_dict():
    """Test converting metrics to dictionary."""
    metrics = UniversalMetrics(
        view_count=1000,
        like_count=100,
        word_count=1200
    )
    
    metrics_dict = metrics.to_dict()
    
    assert 'view_count' in metrics_dict
    assert 'like_count' in metrics_dict
    assert 'word_count' in metrics_dict
    # Dictionary should contain the specified values
    assert metrics_dict['view_count'] == 1000
    assert metrics_dict['like_count'] == 100
    assert metrics_dict['word_count'] == 1200


def test_generate_article_id():
    """Test article ID generation."""
    url1 = "https://example.com/article1"
    url2 = "https://example.com/article2"
    
    id1 = UniversalMetrics.generate_article_id(url1)
    id2 = UniversalMetrics.generate_article_id(url2)
    
    # IDs should be different for different URLs
    assert id1 != id2
    
    # Same URL should generate same ID
    id1_again = UniversalMetrics.generate_article_id(url1)
    assert id1 == id1_again
    
    # ID should be 16 characters
    assert len(id1) == 16
