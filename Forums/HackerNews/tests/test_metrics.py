"""Tests for metrics module."""

import pytest
from datetime import datetime, timezone, timedelta
from src.core.metrics import UniversalMetrics


class TestUniversalMetrics:
    """Test cases for UniversalMetrics class."""
    
    def test_metrics_initialization(self):
        """Test that UniversalMetrics initializes with correct defaults."""
        metrics = UniversalMetrics()
        
        assert metrics.view_count == 0
        assert metrics.like_count == 0
        assert metrics.comment_count == 0
        assert metrics.platform == "unknown"
    
    def test_from_hackernews_basic(self):
        """Test creating metrics from basic HackerNews item."""
        item_data = {
            'id': 12345,
            'title': 'Test Story',
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp()),
            'text': 'Test content'
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        assert metrics.platform == "hackernews"
        assert metrics.like_count == 500
        assert metrics.comment_count == 150
        assert metrics.descendants_count == 150
        assert metrics.content_type == 'story'
    
    def test_from_hackernews_engagement_rate(self):
        """Test engagement rate calculation."""
        item_data = {
            'id': 12345,
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        # Engagement rate = (comments / score) * 100 = (150 / 500) * 100 = 30.0
        assert metrics.engagement_rate == 30.0
    
    def test_from_hackernews_points_per_hour(self):
        """Test points per hour calculation."""
        hours_ago = 5
        item_data = {
            'id': 12345,
            'score': 500,
            'descendants': 100,
            'type': 'story',
            'by': 'testuser',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=hours_ago)).timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        expected_pph = 500 / hours_ago
        assert abs(metrics.points_per_hour - expected_pph) < 1.0
    
    def test_from_hackernews_viral_velocity(self):
        """Test viral velocity calculation."""
        item_data = {
            'id': 12345,
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        # Viral velocity = (points_per_hour * engagement_rate) / 10
        assert metrics.viral_velocity is not None
        assert metrics.viral_velocity > 0
    
    def test_from_hackernews_zero_score(self):
        """Test metrics with zero score."""
        item_data = {
            'id': 12345,
            'score': 0,
            'descendants': 10,
            'type': 'story',
            'by': 'testuser',
            'time': int(datetime.now(timezone.utc).timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        assert metrics.like_count == 0
        assert metrics.engagement_rate is None or metrics.engagement_rate == 0
    
    def test_from_hackernews_title_and_text_length(self):
        """Test that title and text lengths are captured."""
        item_data = {
            'id': 12345,
            'title': 'Test Story Title',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': int(datetime.now(timezone.utc).timestamp()),
            'text': 'This is test content for the story.'
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        assert metrics.title_length == len('Test Story Title')
        assert metrics.description_length == len('This is test content for the story.')
    
    def test_from_hackernews_platform_specific_data(self):
        """Test that platform-specific data is stored."""
        item_data = {
            'id': 12345,
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890,
            'url': 'https://example.com'
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        assert 'score' in metrics.platform_specific
        assert 'descendants' in metrics.platform_specific
        assert 'type' in metrics.platform_specific
        assert 'by' in metrics.platform_specific
        assert 'url' in metrics.platform_specific
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        item_data = {
            'id': 12345,
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': int(datetime.now(timezone.utc).timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        metrics_dict = metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert 'platform' in metrics_dict
        assert 'like_count' in metrics_dict
        assert 'comment_count' in metrics_dict
        assert 'engagement_rate' in metrics_dict
    
    def test_to_dict_excludes_none_values(self):
        """Test that to_dict excludes None values."""
        metrics = UniversalMetrics(platform="hackernews", like_count=100)
        metrics_dict = metrics.to_dict()
        
        # Check that None values are not included
        for key, value in metrics_dict.items():
            assert value is not None
            assert value != []
            assert value != {}
    
    def test_calculate_derived_metrics(self):
        """Test that derived metrics are calculated correctly."""
        metrics = UniversalMetrics(
            platform="hackernews",
            like_count=500,
            comment_count=150,
            hours_since_post=5.0
        )
        
        metrics.calculate_derived_metrics()
        
        assert metrics.engagement_rate == 30.0
        assert metrics.points_per_hour == 100.0
        assert metrics.viral_velocity == 300.0
        assert metrics.days_since_upload == 0
    
    def test_hours_since_post_minimum(self):
        """Test that hours_since_post has a minimum value."""
        current_time = datetime.now(timezone.utc)
        item_data = {
            'id': 12345,
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': int(current_time.timestamp())
        }
        
        metrics = UniversalMetrics.from_hackernews(item_data)
        
        # Should be at least 0.1 hours
        assert metrics.hours_since_post >= 0.1
