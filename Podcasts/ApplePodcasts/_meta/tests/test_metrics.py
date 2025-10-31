"""Tests for ApplePodcasts metrics module."""

import pytest
from core.metrics import UniversalMetrics


def test_universal_metrics_from_apple_podcasts():
    """Test creating UniversalMetrics from Apple Podcasts data."""
    episode_data = {
        'trackId': 123456,
        'trackName': 'Test Episode',
        'description': 'Test description',
        'trackTimeMillis': 3600000,  # 1 hour
        'releaseDate': '2025-01-15T00:00:00Z',
        'collectionName': 'Test Show',
        'artistName': 'Test Creator',
        'genres': ['Comedy', 'Business'],
        'show': {
            'name': 'Test Show',
            'artist': 'Test Creator',
            'rating': 4.8
        },
        'rating': 4.5,
        'rating_count': 100
    }
    
    metrics = UniversalMetrics.from_apple_podcasts(episode_data)
    
    assert metrics.platform == 'apple_podcasts'
    assert metrics.content_type == 'audio'
    assert metrics.rating == 4.5
    assert metrics.rating_count == 100
    assert metrics.duration_ms == 3600000
    assert metrics.duration_seconds == 3600
    assert metrics.show_name == 'Test Show'
    assert metrics.show_artist == 'Test Creator'
    assert metrics.show_rating == 4.8
    assert 'Comedy' in metrics.categories
    assert 'Business' in metrics.categories


def test_universal_metrics_engagement_estimate():
    """Test engagement estimate calculation."""
    episode_data = {
        'trackId': 123456,
        'rating': 4.5,
        'show': {}
    }
    
    metrics = UniversalMetrics.from_apple_podcasts(episode_data)
    
    # Rating 4.5 out of 5.0 should give 90% engagement
    assert metrics.engagement_estimate == 90.0


def test_universal_metrics_to_dict():
    """Test converting metrics to dictionary."""
    episode_data = {
        'trackId': 123456,
        'rating': 4.8,
        'rating_count': 500,
        'show': {
            'name': 'Test Show',
            'rating': 4.7
        }
    }
    
    metrics = UniversalMetrics.from_apple_podcasts(episode_data)
    metrics_dict = metrics.to_dict()
    
    assert 'platform' in metrics_dict
    assert 'rating' in metrics_dict
    assert 'rating_count' in metrics_dict
    assert 'engagement_estimate' in metrics_dict
    assert metrics_dict['platform'] == 'apple_podcasts'
    assert metrics_dict['rating'] == 4.8


def test_universal_metrics_with_minimal_data():
    """Test creating metrics with minimal data."""
    episode_data = {
        'trackId': 123456,
        'show': {}
    }
    
    metrics = UniversalMetrics.from_apple_podcasts(episode_data)
    
    assert metrics.platform == 'apple_podcasts'
    assert metrics.content_type == 'audio'
    # Engagement should be None or 0 when no rating
    assert metrics.engagement_estimate is None or metrics.engagement_estimate == 0
