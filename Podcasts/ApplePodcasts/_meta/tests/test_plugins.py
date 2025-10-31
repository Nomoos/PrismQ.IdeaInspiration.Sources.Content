"""Tests for ApplePodcasts plugin modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from plugins.apple_charts import AppleChartsPlugin
from plugins.apple_category import AppleCategoryPlugin
from plugins.apple_show import AppleShowPlugin


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = Mock()
    config.apple_podcasts_region = 'us'
    config.apple_podcasts_max_shows = 20
    config.apple_podcasts_max_episodes = 10
    return config


class TestAppleChartsPlugin:
    """Tests for AppleChartsPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = AppleChartsPlugin(mock_config)
        
        assert plugin.region == 'us'
        assert plugin.max_shows == 20
        assert plugin.max_episodes == 10
    
    def test_get_source_name(self, mock_config):
        """Test getting source name."""
        plugin = AppleChartsPlugin(mock_config)
        
        assert plugin.get_source_name() == 'apple_podcasts_charts'
    
    @patch('plugins.apple_charts.requests.get')
    def test_search_podcasts_success(self, mock_get, mock_config):
        """Test successful podcast search."""
        plugin = AppleChartsPlugin(mock_config)
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'collectionId': 123, 'collectionName': 'Test Podcast'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        results = plugin._search_podcasts(genre='comedy', limit=5)
        
        assert len(results) == 1
        assert results[0]['collectionId'] == 123
    
    @patch('plugins.apple_charts.requests.get')
    def test_search_podcasts_api_error(self, mock_get, mock_config):
        """Test handling API errors during search."""
        plugin = AppleChartsPlugin(mock_config)
        
        # Mock API error - use RequestException which is caught by the code
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("API Error")
        
        results = plugin._search_podcasts(genre='comedy', limit=5)
        
        assert results == []
    
    @patch('plugins.apple_charts.requests.get')
    def test_get_podcast_episodes_success(self, mock_get, mock_config):
        """Test successful episode retrieval."""
        plugin = AppleChartsPlugin(mock_config)
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'kind': 'podcast'},  # First result is podcast
                {'kind': 'podcast-episode', 'trackId': 456, 'trackName': 'Episode 1'},
                {'kind': 'podcast-episode', 'trackId': 789, 'trackName': 'Episode 2'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        episodes = plugin._get_podcast_episodes(collection_id=123, limit=10)
        
        assert len(episodes) == 2
        assert episodes[0]['trackId'] == 456
    
    def test_episode_to_idea_conversion(self, mock_config):
        """Test converting episode data to idea format."""
        plugin = AppleChartsPlugin(mock_config)
        
        episode = {
            'trackId': 123456,
            'trackName': 'Test Episode',
            'description': 'Test description',
            'trackTimeMillis': 3600000,
            'releaseDate': '2025-01-15',
            'genres': ['Comedy', 'Business']
        }
        
        podcast = {
            'collectionId': 789,
            'collectionName': 'Test Show',
            'artistName': 'Test Artist',
            'averageUserRating': 4.5,
            'userRatingCount': 100
        }
        
        idea = plugin._episode_to_idea(episode, podcast)
        
        assert idea is not None
        assert idea['source'] == 'apple_podcasts'
        assert idea['source_id'] == '123456'
        assert idea['title'] == 'Test Episode'
        assert idea['metrics']['rating'] == 4.5
    
    def test_episode_to_idea_missing_track_id(self, mock_config):
        """Test handling episode with missing track ID."""
        plugin = AppleChartsPlugin(mock_config)
        
        episode = {'trackName': 'Test Episode'}
        podcast = {'collectionName': 'Test Show'}
        
        idea = plugin._episode_to_idea(episode, podcast)
        
        assert idea is None
    
    def test_get_genre_id_known_genre(self, mock_config):
        """Test getting genre ID for known genre."""
        plugin = AppleChartsPlugin(mock_config)
        
        genre_id = plugin._get_genre_id('comedy')
        
        assert genre_id == 1303
    
    def test_get_genre_id_unknown_genre(self, mock_config):
        """Test getting genre ID for unknown genre."""
        plugin = AppleChartsPlugin(mock_config)
        
        genre_id = plugin._get_genre_id('unknown_genre')
        
        assert genre_id is None


class TestAppleCategoryPlugin:
    """Tests for AppleCategoryPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = AppleCategoryPlugin(mock_config)
        
        assert plugin.region == 'us'
        assert plugin.max_shows == 20
        assert plugin.max_episodes == 10
    
    def test_get_source_name(self, mock_config):
        """Test getting source name."""
        plugin = AppleCategoryPlugin(mock_config)
        
        assert plugin.get_source_name() == 'apple_podcasts_category'
    
    @patch('plugins.apple_category.requests.get')
    def test_search_category_success(self, mock_get, mock_config):
        """Test successful category search."""
        plugin = AppleCategoryPlugin(mock_config)
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'collectionId': 123, 'collectionName': 'Test Podcast'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        results = plugin._search_category(category='business', limit=5)
        
        assert len(results) == 1
    
    def test_scrape_requires_category(self, mock_config):
        """Test that scrape requires category parameter."""
        plugin = AppleCategoryPlugin(mock_config)
        
        with pytest.raises(ValueError, match="Category is required"):
            plugin.scrape()


class TestAppleShowPlugin:
    """Tests for AppleShowPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = AppleShowPlugin(mock_config)
        
        assert plugin.region == 'us'
        assert plugin.max_episodes == 10
    
    def test_get_source_name(self, mock_config):
        """Test getting source name."""
        plugin = AppleShowPlugin(mock_config)
        
        assert plugin.get_source_name() == 'apple_podcasts_show'
    
    @patch('plugins.apple_show.requests.get')
    def test_search_show_by_name_success(self, mock_get, mock_config):
        """Test successful show search by name."""
        plugin = AppleShowPlugin(mock_config)
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'collectionId': 123, 'collectionName': 'The Daily'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = plugin._search_show('The Daily')
        
        assert result is not None
        assert result['collectionId'] == 123
    
    @patch('plugins.apple_show.requests.get')
    def test_search_show_not_found(self, mock_get, mock_config):
        """Test handling show not found."""
        plugin = AppleShowPlugin(mock_config)
        
        # Mock API response with no results
        mock_response = Mock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = plugin._search_show('NonexistentShow')
        
        assert result is None
    
    @patch('plugins.apple_show.requests.get')
    def test_lookup_show_by_id(self, mock_get, mock_config):
        """Test looking up show by collection ID."""
        plugin = AppleShowPlugin(mock_config)
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'kind': 'podcast', 'collectionId': 123, 'collectionName': 'Test Show'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = plugin._lookup_show(123)
        
        assert result is not None
        assert result['collectionId'] == 123
    
    def test_scrape_requires_show_id(self, mock_config):
        """Test that scrape requires show_id parameter."""
        plugin = AppleShowPlugin(mock_config)
        
        with pytest.raises(ValueError, match="show_id is required"):
            plugin.scrape()
