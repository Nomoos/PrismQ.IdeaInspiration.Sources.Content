"""Tests for plugin modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.config import Config
from src.plugins.hn_frontpage import HNFrontpagePlugin
from src.plugins.hn_new import HNNewPlugin
from src.plugins.hn_best import HNBestPlugin
from src.plugins.hn_type import HNTypePlugin


class TestHNFrontpagePlugin:
    """Test cases for HNFrontpagePlugin."""
    
    @pytest.fixture
    def config(self):
        """Create a test config."""
        return Config(interactive=False)
    
    @pytest.fixture
    def plugin(self, config):
        """Create a HNFrontpagePlugin instance."""
        return HNFrontpagePlugin(config)
    
    def test_initialization(self, plugin):
        """Test plugin initialization."""
        assert plugin.api_base_url == "https://hacker-news.firebaseio.com/v0"
        assert plugin.timeout == 10
    
    def test_get_source_name(self, plugin):
        """Test get_source_name returns correct name."""
        assert plugin.get_source_name() == "hackernews_frontpage"
    
    def test_item_to_idea_basic(self, plugin):
        """Test converting HN item to idea format."""
        item = {
            'id': 12345,
            'title': 'Test Story',
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890,
            'text': 'Test content'
        }
        
        idea = plugin._item_to_idea(item)
        
        assert idea is not None
        assert idea['source_id'] == '12345'
        assert idea['title'] == 'Test Story'
        assert idea['description'] == 'Test content'
        assert 'story' in idea['tags']
    
    def test_item_to_idea_with_url(self, plugin):
        """Test item with URL extracts domain."""
        item = {
            'id': 12345,
            'title': 'Test Story',
            'score': 500,
            'descendants': 150,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890,
            'url': 'https://www.example.com/article'
        }
        
        idea = plugin._item_to_idea(item)
        
        assert 'example.com' in idea['tags']
    
    def test_item_to_idea_ask_hn(self, plugin):
        """Test Ask HN detection in tags."""
        item = {
            'id': 12345,
            'title': 'Ask HN: How to learn Python?',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(item)
        
        assert 'Ask HN' in idea['tags']
    
    def test_item_to_idea_show_hn(self, plugin):
        """Test Show HN detection in tags."""
        item = {
            'id': 12345,
            'title': 'Show HN: My Project',
            'score': 200,
            'descendants': 75,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(item)
        
        assert 'Show HN' in idea['tags']
    
    def test_item_to_idea_deleted(self, plugin):
        """Test that deleted items return None."""
        item = {
            'id': 12345,
            'deleted': True,
            'title': 'Deleted Story'
        }
        
        idea = plugin._item_to_idea(item)
        
        assert idea is None
    
    def test_item_to_idea_dead(self, plugin):
        """Test that dead items return None."""
        item = {
            'id': 12345,
            'dead': True,
            'title': 'Dead Story'
        }
        
        idea = plugin._item_to_idea(item)
        
        assert idea is None
    
    @patch('src.plugins.hn_frontpage.requests.get')
    def test_fetch_item_success(self, mock_get, plugin):
        """Test successful item fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {'id': 12345, 'title': 'Test'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        item = plugin._fetch_item(12345)
        
        assert item == {'id': 12345, 'title': 'Test'}
        mock_get.assert_called_once()
    
    @patch('src.plugins.hn_frontpage.requests.get')
    def test_fetch_item_failure(self, mock_get, plugin):
        """Test item fetch failure."""
        mock_get.side_effect = Exception("Network error")
        
        item = plugin._fetch_item(12345)
        
        assert item is None


class TestHNNewPlugin:
    """Test cases for HNNewPlugin."""
    
    @pytest.fixture
    def config(self):
        """Create a test config."""
        return Config(interactive=False)
    
    @pytest.fixture
    def plugin(self, config):
        """Create a HNNewPlugin instance."""
        return HNNewPlugin(config)
    
    def test_get_source_name(self, plugin):
        """Test get_source_name returns correct name."""
        assert plugin.get_source_name() == "hackernews_new"
    
    def test_item_to_idea_includes_new_tag(self, plugin):
        """Test that new stories include 'new' tag."""
        item = {
            'id': 12345,
            'title': 'Test Story',
            'score': 10,
            'descendants': 5,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(item)
        
        assert 'new' in idea['tags']


class TestHNBestPlugin:
    """Test cases for HNBestPlugin."""
    
    @pytest.fixture
    def config(self):
        """Create a test config."""
        return Config(interactive=False)
    
    @pytest.fixture
    def plugin(self, config):
        """Create a HNBestPlugin instance."""
        return HNBestPlugin(config)
    
    def test_get_source_name(self, plugin):
        """Test get_source_name returns correct name."""
        assert plugin.get_source_name() == "hackernews_best"
    
    def test_item_to_idea_includes_best_tag(self, plugin):
        """Test that best stories include 'best' tag."""
        item = {
            'id': 12345,
            'title': 'Test Story',
            'score': 1000,
            'descendants': 200,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(item)
        
        assert 'best' in idea['tags']


class TestHNTypePlugin:
    """Test cases for HNTypePlugin."""
    
    @pytest.fixture
    def config(self):
        """Create a test config."""
        return Config(interactive=False)
    
    @pytest.fixture
    def plugin(self, config):
        """Create a HNTypePlugin instance."""
        return HNTypePlugin(config)
    
    def test_get_source_name(self, plugin):
        """Test get_source_name returns correct name."""
        assert plugin.get_source_name() == "hackernews_type"
    
    def test_item_to_idea_ask_filter(self, plugin):
        """Test filtering for Ask HN posts."""
        ask_item = {
            'id': 12345,
            'title': 'Ask HN: How to learn Python?',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        show_item = {
            'id': 67890,
            'title': 'Show HN: My Project',
            'score': 200,
            'descendants': 75,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        ask_idea = plugin._item_to_idea(ask_item, filter_type='ask')
        show_idea = plugin._item_to_idea(show_item, filter_type='ask')
        
        assert ask_idea is not None
        assert show_idea is None
    
    def test_item_to_idea_show_filter(self, plugin):
        """Test filtering for Show HN posts."""
        ask_item = {
            'id': 12345,
            'title': 'Ask HN: How to learn Python?',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        show_item = {
            'id': 67890,
            'title': 'Show HN: My Project',
            'score': 200,
            'descendants': 75,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        ask_idea = plugin._item_to_idea(ask_item, filter_type='show')
        show_idea = plugin._item_to_idea(show_item, filter_type='show')
        
        assert ask_idea is None
        assert show_idea is not None
    
    def test_item_to_idea_no_filter(self, plugin):
        """Test that no filter returns all items."""
        item = {
            'id': 12345,
            'title': 'Regular Story',
            'score': 100,
            'descendants': 50,
            'type': 'story',
            'by': 'testuser',
            'time': 1234567890
        }
        
        idea = plugin._item_to_idea(item, filter_type=None)
        
        assert idea is not None


class TestSourcePlugin:
    """Test cases for SourcePlugin base class."""
    
    def test_format_tags(self):
        """Test format_tags method."""
        config = Config(interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        tags = ['story', 'test', 'example.com']
        formatted = plugin.format_tags(tags)
        
        assert formatted == 'story,test,example.com'
    
    def test_format_tags_with_empty_strings(self):
        """Test format_tags removes empty strings."""
        config = Config(interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        tags = ['story', '', 'test', '  ', 'example.com']
        formatted = plugin.format_tags(tags)
        
        assert formatted == 'story,test,example.com'
    
    def test_format_tags_with_whitespace(self):
        """Test format_tags strips whitespace."""
        config = Config(interactive=False)
        plugin = HNFrontpagePlugin(config)
        
        tags = [' story ', '  test  ', 'example.com']
        formatted = plugin.format_tags(tags)
        
        assert formatted == 'story,test,example.com'
