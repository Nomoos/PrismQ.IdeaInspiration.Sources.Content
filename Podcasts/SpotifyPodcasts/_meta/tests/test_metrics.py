"""Tests for universal metrics."""

import pytest
from src.core.metrics import UniversalMetrics


def test_universal_metrics_initialization():
    """Test basic metrics initialization."""
    metrics = UniversalMetrics()
    
    assert metrics.engagement_estimate == 0.0
    assert metrics.platform == "spotify"
    assert metrics.content_type == "podcast_episode"


def test_universal_metrics_from_spotify():
    """Test creating metrics from Spotify data."""
    episode_data = {
        'id': 'test123',
        'uri': 'spotify:episode:test123',
        'duration_ms': 3600000,
        'release_date': '2025-01-15',
        'explicit': False,
        'language': 'en',
        'show': {
            'name': 'Test Show',
            'publisher': 'Test Publisher',
            'total_episodes': 100
        },
        'external_urls': {'spotify': 'https://open.spotify.com/episode/test123'},
        'images': [{'url': 'https://example.com/image.jpg'}]
    }
    
    metrics = UniversalMetrics.from_spotify(episode_data)
    
    assert metrics.duration_ms == 3600000
    assert metrics.release_date == '2025-01-15'
    assert metrics.has_explicit_content is False
    assert metrics.language == 'en'
    assert metrics.show_name == 'Test Show'
    assert metrics.publisher == 'Test Publisher'
    assert metrics.total_episodes == 100


def test_universal_metrics_to_dict():
    """Test converting metrics to dictionary."""
    metrics = UniversalMetrics(
        engagement_estimate=5.0,
        duration_ms=1800000,
        release_date='2025-01-15'
    )
    
    metrics_dict = metrics.to_dict()
    
    assert isinstance(metrics_dict, dict)
    assert metrics_dict['engagement_estimate'] == 5.0
    assert metrics_dict['duration_ms'] == 1800000
    assert metrics_dict['release_date'] == '2025-01-15'


def test_universal_metrics_from_dict():
    """Test creating metrics from dictionary."""
    data = {
        'engagement_estimate': 7.5,
        'duration_ms': 2400000,
        'release_date': '2025-01-20',
        'platform': 'spotify'
    }
    
    metrics = UniversalMetrics.from_dict(data)
    
    assert metrics.engagement_estimate == 7.5
    assert metrics.duration_ms == 2400000
    assert metrics.release_date == '2025-01-20'
    assert metrics.platform == 'spotify'
