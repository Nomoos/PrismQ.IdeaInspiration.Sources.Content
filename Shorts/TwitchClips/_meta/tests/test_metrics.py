"""Tests for universal metrics module."""

import pytest
from datetime import datetime
from src.core.metrics import UniversalMetrics


def test_universal_metrics_initialization():
    """Test basic metrics initialization."""
    metrics = UniversalMetrics(
        platform="twitch",
        view_count=10000,
        like_count=500,
        comment_count=50,
        share_count=25
    )
    
    assert metrics.platform == "twitch"
    assert metrics.view_count == 10000
    assert metrics.like_count == 500
    assert metrics.comment_count == 50
    assert metrics.share_count == 25


def test_calculate_derived_metrics():
    """Test derived metrics calculation."""
    metrics = UniversalMetrics(
        view_count=10000,
        like_count=500,
        comment_count=50,
        share_count=25
    )
    
    metrics.calculate_derived_metrics()
    
    # Engagement rate = (500 + 50 + 25) / 10000 * 100 = 5.75%
    assert metrics.engagement_rate == pytest.approx(5.75, rel=0.01)
    
    # Like to view ratio = 500 / 10000 * 100 = 5%
    assert metrics.like_to_view_ratio == pytest.approx(5.0, rel=0.01)
    
    # Comment to view ratio = 50 / 10000 * 100 = 0.5%
    assert metrics.comment_to_view_ratio == pytest.approx(0.5, rel=0.01)
    
    # Share to view ratio = 25 / 10000 * 100 = 0.25%
    assert metrics.share_to_view_ratio == pytest.approx(0.25, rel=0.01)


def test_from_twitch():
    """Test creating metrics from Twitch clip data."""
    clip_data = {
        'id': 'test_clip_id',
        'title': 'Amazing Play!',
        'url': 'https://clips.twitch.tv/test_clip_id',
        'view_count': 10000,
        'duration': 30.5,
        'created_at': '2024-01-01T00:00:00Z',
        'broadcaster_id': '123456',
        'broadcaster_name': 'TestStreamer',
        'broadcaster_type': 'partner',
        'creator_id': '789012',
        'creator_name': 'TestCreator',
        'game_id': '33214',
        'game_name': 'Fortnite',
        'language': 'en',
        'vod_offset': 3600,
        'thumbnail_url': 'https://example.com/thumb.jpg'
    }
    
    metrics = UniversalMetrics.from_twitch(clip_data)
    
    assert metrics.platform == "twitch"
    assert metrics.content_type == "clip"
    assert metrics.view_count == 10000
    assert metrics.duration_seconds == 30
    assert metrics.title_length == len('Amazing Play!')
    assert metrics.author_verification is True
    assert metrics.platform_specific['broadcaster_name'] == 'TestStreamer'
    assert metrics.platform_specific['game_name'] == 'Fortnite'
    assert metrics.platform_specific['vod_offset'] == 3600


def test_to_dict():
    """Test conversion to dictionary."""
    metrics = UniversalMetrics(
        platform="twitch",
        view_count=1000,
        like_count=50
    )
    
    metrics_dict = metrics.to_dict()
    
    assert metrics_dict['platform'] == "twitch"
    assert metrics_dict['view_count'] == 1000
    assert metrics_dict['like_count'] == 50
    # None values should be excluded
    assert 'comment_count' not in metrics_dict or metrics_dict['comment_count'] == 0
