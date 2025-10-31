"""Integration tests for HackerNews source - tests full workflows."""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, Mock
from src.core.config import Config
from src.core.database import Database
from src.core.metrics import UniversalMetrics
from src.plugins.hn_frontpage import HNFrontpagePlugin
from src.plugins.hn_new import HNNewPlugin
from src.plugins.hn_best import HNBestPlugin
from src.plugins.hn_type import HNTypePlugin
from src.core.idea_processor import IdeaProcessor
from src.core import db_utils


class TestEndToEndWorkflow:
    """End-to-end integration tests for complete workflows."""
    
    @pytest.fixture
    def temp_env_and_db(self):
        """Create temporary env file and database."""
        temp_env = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        temp_env.write("HN_FRONTPAGE_MAX_POSTS=5\n")
        temp_env.write("HN_API_BASE_URL=https://hacker-news.firebaseio.com/v0\n")
        temp_env.close()
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.s3db')
        temp_db.close()
        
        yield temp_env.name, temp_db.name
        
        os.unlink(temp_env.name)
        os.unlink(temp_db.name)
    
    def test_full_scrape_and_process_workflow(self, temp_env_and_db):
        """Test complete workflow: scrape -> store -> process."""
        env_file, db_file = temp_env_and_db
        
        # Step 1: Initialize config and database
        config = Config(env_file=env_file, interactive=False)
        db = Database(db_file, interactive=False)
        
        assert config.hn_frontpage_max_posts == 5
        assert db.count_ideas() == 0
        
        # Step 2: Create mock HN item
        mock_item = {
            'id': 12345,
            'title': 'Show HN: My Awesome Project',
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890,
            'text': 'This is a detailed description of my awesome project.',
            'url': 'https://example.com/project'
        }
        
        # Step 3: Process with plugin
        plugin = HNFrontpagePlugin(config)
        idea = plugin._item_to_idea(mock_item)
        
        assert idea is not None
        assert idea['source_id'] == '12345'
        assert 'Show HN' in idea['tags']
        assert 'example.com' in idea['tags']
        
        # Step 4: Calculate metrics
        metrics = UniversalMetrics.from_hackernews(mock_item)
        
        assert metrics.like_count == 500
        assert metrics.comment_count == 150
        assert metrics.engagement_rate == 30.0
        assert metrics.platform == "hackernews"
        
        # Step 5: Store in database
        success = db.insert_idea(
            source='hackernews_frontpage',
            source_id=idea['source_id'],
            title=idea['title'],
            description=idea['description'],
            tags=idea['tags'],
            score=metrics.engagement_rate,
            score_dictionary=metrics.to_dict()
        )
        
        assert success is True
        assert db.count_ideas() == 1
        
        # Step 6: Retrieve and verify
        retrieved = db.get_idea('hackernews_frontpage', '12345')
        
        assert retrieved is not None
        assert retrieved['title'] == 'Show HN: My Awesome Project'
        assert retrieved['source_id'] == '12345'
        
        # Step 7: Process to IdeaInspiration format
        processed_idea = IdeaProcessor.process(retrieved)
        
        assert processed_idea.title == 'Show HN: My Awesome Project'
        assert processed_idea.source_id == '12345'
        assert processed_idea.source_url == 'https://news.ycombinator.com/item?id=12345'
        assert 'hn_score' in processed_idea.metadata
        assert 'engagement_rate' in processed_idea.metadata
        assert processed_idea.category == 'hackernews'
        
        # Step 8: Verify metadata completeness
        idea_dict = processed_idea.to_dict()
        
        assert 'title' in idea_dict
        assert 'source_id' in idea_dict
        assert 'source_url' in idea_dict
        assert 'metadata' in idea_dict
        assert 'keywords' in idea_dict
        assert 'Show HN' in processed_idea.keywords
    
    def test_deduplication_workflow(self, temp_env_and_db):
        """Test that duplicate items are properly handled."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        db = Database(db_file, interactive=False)
        
        # Insert first version
        db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Original Title',
            description='Original description',
            tags='story',
            score=50.0
        )
        
        assert db.count_ideas() == 1
        
        # Insert duplicate with updated data
        success = db.insert_idea(
            source='hackernews_frontpage',
            source_id='12345',
            title='Updated Title',
            description='Updated description',
            tags='story,updated',
            score=100.0
        )
        
        # Should update, not insert
        assert success is False
        assert db.count_ideas() == 1
        
        # Verify updated data
        idea = db.get_idea('hackernews_frontpage', '12345')
        assert idea['title'] == 'Updated Title'
        assert idea['score'] == 100.0
    
    def test_multiple_sources_workflow(self, temp_env_and_db):
        """Test handling ideas from multiple sources."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        db = Database(db_file, interactive=False)
        
        # Insert from different sources
        sources = [
            ('hackernews_frontpage', '1'),
            ('hackernews_new', '2'),
            ('hackernews_best', '3'),
            ('hackernews_ask', '4'),
            ('hackernews_show', '5')
        ]
        
        for source, source_id in sources:
            db.insert_idea(
                source=source,
                source_id=source_id,
                title=f'Story from {source}',
                description='Test',
                tags='story',
                score=50.0
            )
        
        # Verify all inserted
        assert db.count_ideas() == 5
        
        # Verify counts by source
        assert db.count_by_source('hackernews_frontpage') == 1
        assert db.count_by_source('hackernews_new') == 1
        assert db.count_by_source('hackernews_best') == 1
        assert db.count_by_source('hackernews_ask') == 1
        assert db.count_by_source('hackernews_show') == 1
    
    def test_metrics_calculation_accuracy(self):
        """Test accuracy of metrics calculations with real scenarios."""
        from datetime import datetime, timezone, timedelta
        
        # Scenario 1: High engagement story
        high_engagement_item = {
            'id': 1001,
            'score': 1000,
            'descendants': 500,
            'type': 'story',
            'by': 'popular_user',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=10)).timestamp())
        }
        
        metrics1 = UniversalMetrics.from_hackernews(high_engagement_item)
        
        assert metrics1.engagement_rate == 50.0
        assert metrics1.points_per_hour == 100.0
        assert metrics1.viral_velocity == 500.0
        
        # Scenario 2: Low engagement story
        low_engagement_item = {
            'id': 1002,
            'score': 100,
            'descendants': 10,
            'type': 'story',
            'by': 'regular_user',
            'time': int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp())
        }
        
        metrics2 = UniversalMetrics.from_hackernews(low_engagement_item)
        
        assert metrics2.engagement_rate == 10.0
        assert metrics2.points_per_hour == 20.0
        assert metrics2.viral_velocity == 20.0
        
        # Scenario 3: Recent story
        recent_item = {
            'id': 1003,
            'score': 50,
            'descendants': 25,
            'type': 'story',
            'by': 'new_user',
            'time': int((datetime.now(timezone.utc) - timedelta(minutes=30)).timestamp())
        }
        
        metrics3 = UniversalMetrics.from_hackernews(recent_item)
        
        assert metrics3.engagement_rate == 50.0
        assert metrics3.hours_since_post >= 0.1
    
    def test_ask_hn_filtering_workflow(self, temp_env_and_db):
        """Test Ask HN filtering functionality."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        plugin = HNTypePlugin(config)
        
        # Create test items
        ask_items = [
            {
                'id': 101,
                'title': 'Ask HN: How to learn Rust?',
                'score': 100,
                'descendants': 50,
                'type': 'story',
                'by': 'learner',
                'time': 1234567890
            },
            {
                'id': 102,
                'title': 'Ask HN: Best IDE for Python?',
                'score': 75,
                'descendants': 30,
                'type': 'story',
                'by': 'developer',
                'time': 1234567890
            }
        ]
        
        show_items = [
            {
                'id': 201,
                'title': 'Show HN: My new app',
                'score': 200,
                'descendants': 100,
                'type': 'story',
                'by': 'maker',
                'time': 1234567890
            }
        ]
        
        # Test Ask HN filtering
        ask_ideas = [plugin._item_to_idea(item, 'ask') for item in ask_items]
        show_ideas_filtered = [plugin._item_to_idea(item, 'ask') for item in show_items]
        
        # All Ask HN items should pass
        assert all(idea is not None for idea in ask_ideas)
        assert all('Ask HN' in idea['tags'] for idea in ask_ideas if idea)
        
        # Show HN items should be filtered out
        assert all(idea is None for idea in show_ideas_filtered)
    
    def test_show_hn_filtering_workflow(self, temp_env_and_db):
        """Test Show HN filtering functionality."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        plugin = HNTypePlugin(config)
        
        ask_item = {
            'id': 301,
            'title': 'Ask HN: Career advice?',
            'score': 50,
            'descendants': 25,
            'type': 'story',
            'by': 'user1',
            'time': 1234567890
        }
        
        show_items = [
            {
                'id': 401,
                'title': 'Show HN: My side project',
                'score': 150,
                'descendants': 75,
                'type': 'story',
                'by': 'maker1',
                'time': 1234567890
            },
            {
                'id': 402,
                'title': 'Show HN: Open source tool',
                'score': 300,
                'descendants': 150,
                'type': 'story',
                'by': 'maker2',
                'time': 1234567890
            }
        ]
        
        # Test Show HN filtering
        ask_filtered = plugin._item_to_idea(ask_item, 'show')
        show_ideas = [plugin._item_to_idea(item, 'show') for item in show_items]
        
        # Ask HN should be filtered out
        assert ask_filtered is None
        
        # All Show HN items should pass
        assert all(idea is not None for idea in show_ideas)
        assert all('Show HN' in idea['tags'] for idea in show_ideas if idea)
    
    def test_url_domain_extraction_workflow(self, temp_env_and_db):
        """Test URL and domain extraction from various sources."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        test_urls = [
            ('https://www.github.com/user/repo', 'github.com'),
            ('https://blog.example.com/article', 'blog.example.com'),
            ('https://news.ycombinator.com/item?id=123', 'news.ycombinator.com'),
            ('https://www.reddit.com/r/programming', 'reddit.com'),
        ]
        
        for url, expected_domain in test_urls:
            item = {
                'id': 12345,
                'title': 'Test Story',
                'score': 100,
                'descendants': 50,
                'type': 'story',
                'by': 'user',
                'time': 1234567890,
                'url': url
            }
            
            idea = plugin._item_to_idea(item)
            
            assert idea is not None
            assert expected_domain in idea['tags']
    
    def test_process_and_clear_workflow(self, temp_env_and_db):
        """Test processing ideas and clearing database."""
        env_file, db_file = temp_env_and_db
        
        config = Config(env_file=env_file, interactive=False)
        db = Database(db_file, interactive=False)
        
        # Insert test ideas
        for i in range(5):
            db.insert_idea(
                source='hackernews_frontpage',
                source_id=str(i),
                title=f'Story {i}',
                description='Test',
                tags='story',
                score=50.0
            )
        
        assert db.count_ideas() == 5
        
        # Get unprocessed
        database_url = f"sqlite:///{db_file}"
        unprocessed = db_utils.get_unprocessed_ideas(database_url, limit=10)
        
        assert len(unprocessed) == 5
        
        # Mark some as processed
        for record in unprocessed[:3]:
            db_utils.mark_as_processed(database_url, record['id'])
        
        # Verify processed count
        remaining_unprocessed = db_utils.get_unprocessed_ideas(database_url, limit=10)
        assert len(remaining_unprocessed) == 2
        
        # Clear all
        deleted = db_utils.clear_all_ideas(database_url)
        assert deleted == 5
        assert db.count_ideas() == 0
    
    def test_score_dictionary_serialization(self, temp_env_and_db):
        """Test that score dictionaries are properly serialized and deserialized."""
        env_file, db_file = temp_env_and_db
        
        db = Database(db_file, interactive=False)
        
        # Test with dict
        score_dict = {
            'score': 500,
            'descendants': 150,
            'engagement_rate': 30.0,
            'viral_velocity': 300.0
        }
        
        db.insert_idea(
            source='hackernews_frontpage',
            source_id='999',
            title='Test',
            description='Test',
            tags='test',
            score=100.0,
            score_dictionary=score_dict
        )
        
        # Retrieve and verify
        idea = db.get_idea('hackernews_frontpage', '999')
        
        assert idea is not None
        retrieved_dict = json.loads(idea['score_dictionary'])
        assert retrieved_dict['score'] == 500
        assert retrieved_dict['descendants'] == 150
        assert retrieved_dict['engagement_rate'] == 30.0


class TestPluginInteroperability:
    """Test that all plugins work together correctly."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return Config(interactive=False)
    
    def test_all_plugins_initialized(self, config):
        """Test all plugins can be initialized."""
        plugins = [
            HNFrontpagePlugin(config),
            HNNewPlugin(config),
            HNBestPlugin(config),
            HNTypePlugin(config)
        ]
        
        assert len(plugins) == 4
        assert all(p.api_base_url == config.hn_api_base_url for p in plugins)
        assert all(p.timeout == config.hn_request_timeout for p in plugins)
    
    def test_all_plugins_unique_source_names(self, config):
        """Test each plugin has unique source name."""
        plugins = [
            HNFrontpagePlugin(config),
            HNNewPlugin(config),
            HNBestPlugin(config),
            HNTypePlugin(config)
        ]
        
        source_names = [p.get_source_name() for p in plugins]
        
        assert len(source_names) == len(set(source_names))
        assert 'hackernews_frontpage' in source_names
        assert 'hackernews_new' in source_names
        assert 'hackernews_best' in source_names
        assert 'hackernews_type' in source_names
    
    def test_plugins_process_same_item_differently(self, config):
        """Test that different plugins add their own tags."""
        item = {
            'id': 12345,
            'title': 'Test Story',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'user',
            'time': 1234567890
        }
        
        frontpage_plugin = HNFrontpagePlugin(config)
        new_plugin = HNNewPlugin(config)
        best_plugin = HNBestPlugin(config)
        
        frontpage_idea = frontpage_plugin._item_to_idea(item)
        new_idea = new_plugin._item_to_idea(item)
        best_idea = best_plugin._item_to_idea(item)
        
        # All should process successfully
        assert all([frontpage_idea, new_idea, best_idea])
        
        # Each should have different tags
        assert 'new' not in frontpage_idea['tags']
        assert 'new' in new_idea['tags']
        assert 'best' in best_idea['tags']


class TestErrorHandling:
    """Test error handling in various scenarios."""
    
    def test_database_handles_invalid_order_by(self):
        """Test SQL injection protection in order_by parameter."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.s3db')
        temp_db.close()
        
        try:
            db = Database(temp_db.name, interactive=False)
            
            # Insert test data
            db.insert_idea(
                source='hackernews_test',
                source_id='1',
                title='Test',
                description='Test',
                tags='test',
                score=50.0
            )
            
            # Valid column
            ideas = db.get_all_ideas(limit=10, order_by='score')
            assert len(ideas) == 1
            
            # Invalid column (SQL injection attempt)
            ideas = db.get_all_ideas(limit=10, order_by='score; DROP TABLE HackerNewsSource;--')
            assert len(ideas) == 1
            
            # Verify table still exists
            assert db.count_ideas() == 1
        finally:
            os.unlink(temp_db.name)
    
    def test_plugin_handles_deleted_items(self):
        """Test plugins properly filter deleted items."""
        config = Config(interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        deleted_item = {
            'id': 12345,
            'deleted': True,
            'title': 'Deleted Story'
        }
        
        dead_item = {
            'id': 12346,
            'dead': True,
            'title': 'Dead Story'
        }
        
        assert plugin._item_to_idea(deleted_item) is None
        assert plugin._item_to_idea(dead_item) is None
    
    def test_plugin_handles_missing_fields(self):
        """Test plugins handle items with missing optional fields."""
        config = Config(interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        minimal_item = {
            'id': 12345,
            'title': 'Minimal Story',
            'type': 'story',
            'by': 'user',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(minimal_item)
        
        assert idea is not None
        assert idea['source_id'] == '12345'
        assert idea['description'] == ''
    
    def test_metrics_handles_zero_values(self):
        """Test metrics calculation with edge case values."""
        # Zero score
        zero_score_item = {
            'id': 1,
            'score': 0,
            'descendants': 10,
            'type': 'story',
            'by': 'user',
            'time': 1234567890
        }
        
        metrics = UniversalMetrics.from_hackernews(zero_score_item)
        
        assert metrics.like_count == 0
        assert metrics.engagement_rate is None or metrics.engagement_rate == 0
        
        # Zero descendants
        zero_descendants_item = {
            'id': 2,
            'score': 100,
            'descendants': 0,
            'type': 'story',
            'by': 'user',
            'time': 1234567890
        }
        
        metrics2 = UniversalMetrics.from_hackernews(zero_descendants_item)
        
        assert metrics2.comment_count == 0
        assert metrics2.engagement_rate == 0.0
