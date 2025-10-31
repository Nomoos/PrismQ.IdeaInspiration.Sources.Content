"""Tests for UniversalMetrics class."""

import pytest
from src.core.metrics import UniversalMetrics


class TestUniversalMetrics:
    """Test cases for UniversalMetrics class."""
    
    def test_metrics_from_tiktok(self):
        """Test creating metrics from TikTok data."""
        tiktok_data = {
            'stats': {
                'playCount': 1000000,
                'diggCount': 50000,
                'commentCount': 2000,
                'shareCount': 5000,
                'repostCount': 100
            }
        }
        
        metrics = UniversalMetrics.from_tiktok(tiktok_data)
        
        assert metrics.platform == 'tiktok'
        assert metrics.view_count == 1000000
        assert metrics.like_count == 50000
        assert metrics.comment_count == 2000
        assert metrics.share_count == 5000
        assert metrics.repost_count == 100
    
    def test_metrics_engagement_calculation(self):
        """Test engagement rate calculation."""
        metrics = UniversalMetrics(
            platform='tiktok',
            view_count=1000,
            like_count=100,
            comment_count=20,
            share_count=10
        )
        
        metrics.calculate_derived_metrics()
        
        # Engagement rate = (100 + 20 + 10) / 1000 * 100 = 13%
        assert metrics.engagement_rate == pytest.approx(13.0)
        assert metrics.like_to_view_ratio == pytest.approx(10.0)
        assert metrics.comment_to_view_ratio == pytest.approx(2.0)
        assert metrics.share_to_view_ratio == pytest.approx(1.0)
    
    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = UniversalMetrics(
            platform='tiktok',
            view_count=1000,
            like_count=100
        )
        
        metrics_dict = metrics.to_dict()
        
        assert 'platform' in metrics_dict
        assert 'view_count' in metrics_dict
        assert 'like_count' in metrics_dict
        assert metrics_dict['platform'] == 'tiktok'
        assert metrics_dict['view_count'] == 1000
