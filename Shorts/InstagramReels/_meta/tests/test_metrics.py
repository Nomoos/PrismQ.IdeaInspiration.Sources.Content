"""Tests for UniversalMetrics class."""

import pytest
from src.core.metrics import UniversalMetrics


class TestUniversalMetrics:
    """Test UniversalMetrics class."""
    
    def test_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = UniversalMetrics(
            plays_count=1000,
            like_count=100,
            comment_count=10,
            share_count=5,
            save_count=20
        )
        
        assert metrics.plays_count == 1000
        assert metrics.like_count == 100
        assert metrics.comment_count == 10
    
    def test_calculate_derived_metrics(self):
        """Test calculation of derived metrics."""
        metrics = UniversalMetrics(
            plays_count=1000,
            like_count=100,
            comment_count=10,
            share_count=5,
            save_count=20
        )
        
        metrics.calculate_derived_metrics()
        
        # Engagement rate = (100 + 10 + 5 + 20) / 1000 * 100 = 13.5%
        assert metrics.engagement_rate == 13.5
        assert metrics.like_to_plays_ratio == 10.0  # 100/1000 * 100
    
    def test_from_instagram(self):
        """Test creating metrics from Instagram data."""
        reel_data = {
            'source_id': 'test123',
            'title': 'Test Reel',
            'description': 'Test description',
            'tags': ['test', 'reel'],
            'creator': {
                'username': 'testuser',
                'followers': 1000,
                'verified': False
            },
            'metrics': {
                'plays': 1000,
                'likes': 100,
                'comments': 10,
                'shares': 5,
                'saves': 20
            },
            'reel': {
                'duration': 30,
                'audio': 'Original audio',
                'location': 'Test City'
            }
        }
        
        metrics = UniversalMetrics.from_instagram(reel_data)
        
        assert metrics.plays_count == 1000
        assert metrics.like_count == 100
        assert metrics.author_username == 'testuser'
        assert metrics.engagement_rate == 13.5
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = UniversalMetrics(
            plays_count=1000,
            like_count=100
        )
        
        data = metrics.to_dict()
        
        assert isinstance(data, dict)
        assert data['plays_count'] == 1000
        assert data['like_count'] == 100
