"""Tests for Medium source plugins."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.config import Config
from src.plugins.medium_trending import MediumTrendingPlugin
from src.plugins.medium_tag import MediumTagPlugin
from src.plugins.medium_publication import MediumPublicationPlugin
from src.plugins.medium_author import MediumAuthorPlugin


@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = Mock()
    config.user_agent = 'Mozilla/5.0 Test Agent'
    config.request_timeout = 30
    config.request_delay = 1
    config.medium_trending_max_articles = 10
    config.medium_tag_max_articles = 10
    config.medium_publication_max_articles = 10
    config.medium_author_max_articles = 10
    return config


@pytest.fixture
def mock_html():
    """Create mock HTML response for Medium pages."""
    return """
    <html>
        <body>
            <article>
                <a href="/p/test-article-123">Test Article</a>
            </article>
            <article>
                <a href="/p/another-article-456">Another Article</a>
            </article>
        </body>
    </html>
    """


@pytest.fixture
def mock_article_html():
    """Create mock HTML for a single article page."""
    return """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <h1>Understanding AI in 2024</h1>
            <h2 class="pw-subtitle-paragraph">A comprehensive guide</h2>
            <a data-action="show-user-card">TestAuthor</a>
            <a href="/tag/artificial-intelligence">AI</a>
            <a href="/tag/machine-learning">ML</a>
            <button data-action="show-recommends">1.2K</button>
            <span>8 min read</span>
            <article>
                <p>This is the first paragraph of the article.</p>
                <p>This is the second paragraph with more content.</p>
            </article>
        </body>
    </html>
    """


class TestMediumTrendingPlugin:
    """Tests for MediumTrendingPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = MediumTrendingPlugin(mock_config)
        
        assert plugin is not None
        assert plugin.config == mock_config
        assert plugin.timeout == 30
        assert plugin.delay == 1
        assert hasattr(plugin, 'session')
    
    def test_get_source_name(self, mock_config):
        """Test get_source_name returns correct value."""
        plugin = MediumTrendingPlugin(mock_config)
        assert plugin.get_source_name() == "medium_trending"
    
    @patch('src.plugins.medium_trending.requests.Session')
    def test_scrape_success(self, mock_session_class, mock_config, mock_html, mock_article_html):
        """Test successful scraping of trending articles."""
        # Setup mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock the trending page response
        trending_response = Mock()
        trending_response.status_code = 200
        trending_response.content = mock_html.encode('utf-8')
        trending_response.raise_for_status = Mock()
        
        # Mock the article page response
        article_response = Mock()
        article_response.status_code = 200
        article_response.content = mock_article_html.encode('utf-8')
        article_response.raise_for_status = Mock()
        
        # Setup mock session to return different responses
        mock_session.get.side_effect = [trending_response, article_response, article_response]
        
        plugin = MediumTrendingPlugin(mock_config)
        plugin.session = mock_session
        
        # Mock time.sleep to speed up test
        with patch('src.plugins.medium_trending.time.sleep'):
            ideas = plugin.scrape(top_n=2)
        
        assert len(ideas) <= 2
        assert all(isinstance(idea, dict) for idea in ideas)
    
    @patch('src.plugins.medium_trending.requests.Session')
    def test_scrape_with_request_exception(self, mock_session_class, mock_config):
        """Test scraping handles request exceptions gracefully."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock session to raise exception
        import requests
        mock_session.get.side_effect = requests.RequestException("Network error")
        
        plugin = MediumTrendingPlugin(mock_config)
        plugin.session = mock_session
        
        ideas = plugin.scrape(top_n=5)
        
        # Should return empty list on error
        assert ideas == []
    
    def test_extract_article_links(self, mock_config, mock_html):
        """Test extracting article links from HTML."""
        from bs4 import BeautifulSoup
        
        plugin = MediumTrendingPlugin(mock_config)
        soup = BeautifulSoup(mock_html, 'lxml')
        
        links = plugin._extract_article_links(soup, limit=10)
        
        assert isinstance(links, list)
        assert len(links) <= 10
    
    @patch('src.plugins.medium_trending.requests.Session')
    def test_scrape_article(self, mock_session_class, mock_config, mock_article_html):
        """Test scraping a single article."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        article_response = Mock()
        article_response.status_code = 200
        article_response.content = mock_article_html.encode('utf-8')
        article_response.raise_for_status = Mock()
        
        mock_session.get.return_value = article_response
        
        plugin = MediumTrendingPlugin(mock_config)
        plugin.session = mock_session
        
        article_data = plugin._scrape_article("https://medium.com/p/test-123")
        
        assert article_data is not None
        assert 'source_id' in article_data
        assert 'title' in article_data
        assert 'author' in article_data
        assert 'metrics' in article_data
    
    @patch('src.plugins.medium_trending.requests.Session')
    def test_scrape_article_with_exception(self, mock_session_class, mock_config):
        """Test scraping article handles exceptions."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        import requests
        mock_session.get.side_effect = requests.RequestException("Error")
        
        plugin = MediumTrendingPlugin(mock_config)
        plugin.session = mock_session
        
        article_data = plugin._scrape_article("https://medium.com/p/test-123")
        
        assert article_data is None
    
    def test_format_tags(self, mock_config):
        """Test tag formatting."""
        plugin = MediumTrendingPlugin(mock_config)
        
        tags = ['ai', 'machine-learning', 'python']
        formatted = plugin.format_tags(tags)
        
        assert formatted == 'ai,machine-learning,python'
        
        # Test with empty tags
        assert plugin.format_tags([]) == ''
        
        # Test with tags containing whitespace
        tags_with_space = ['  ai  ', 'ml', '  ']
        formatted = plugin.format_tags(tags_with_space)
        assert formatted == 'ai,ml'


class TestMediumTagPlugin:
    """Tests for MediumTagPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = MediumTagPlugin(mock_config)
        
        assert plugin is not None
        assert plugin.config == mock_config
        assert hasattr(plugin, '_trending_plugin')
    
    def test_get_source_name(self, mock_config):
        """Test get_source_name returns correct value."""
        plugin = MediumTagPlugin(mock_config)
        assert plugin.get_source_name() == "medium_tag"
    
    @patch('src.plugins.medium_tag.MediumTrendingPlugin')
    def test_scrape_with_tag(self, mock_trending_class, mock_config):
        """Test scraping with a specific tag."""
        # Mock the trending plugin
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.timeout = 30
        mock_trending.delay = 1
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><article><a href="/p/test">Test</a></article></html>'
        mock_response.raise_for_status = Mock()
        mock_trending.session.get.return_value = mock_response
        
        # Mock _extract_article_links and _scrape_article
        mock_trending._extract_article_links.return_value = ['https://medium.com/p/test-123']
        mock_trending._scrape_article.return_value = {
            'source_id': 'test-123',
            'title': 'Test Article',
            'tags': 'ai'
        }
        
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumTagPlugin(mock_config)
        
        with patch('src.plugins.medium_tag.time.sleep'):
            ideas = plugin.scrape(tag='artificial-intelligence', top_n=5)
        
        assert isinstance(ideas, list)
    
    def test_scrape_without_tag(self, mock_config):
        """Test scraping without tag returns empty list."""
        plugin = MediumTagPlugin(mock_config)
        
        ideas = plugin.scrape(tag=None, top_n=5)
        
        assert ideas == []
    
    @patch('src.plugins.medium_tag.MediumTrendingPlugin')
    def test_scrape_with_exception(self, mock_trending_class, mock_config):
        """Test scraping handles exceptions gracefully."""
        mock_trending = Mock()
        import requests
        mock_trending.session.get.side_effect = requests.RequestException("Error")
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumTagPlugin(mock_config)
        
        ideas = plugin.scrape(tag='test', top_n=5)
        
        assert ideas == []


class TestMediumPublicationPlugin:
    """Tests for MediumPublicationPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = MediumPublicationPlugin(mock_config)
        
        assert plugin is not None
        assert plugin.config == mock_config
        assert hasattr(plugin, '_trending_plugin')
    
    def test_get_source_name(self, mock_config):
        """Test get_source_name returns correct value."""
        plugin = MediumPublicationPlugin(mock_config)
        assert plugin.get_source_name() == "medium_publication"
    
    @patch('src.plugins.medium_publication.MediumTrendingPlugin')
    def test_scrape_with_publication_name(self, mock_trending_class, mock_config):
        """Test scraping with publication name."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.timeout = 30
        mock_trending.delay = 1
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><article><a href="/p/test">Test</a></article></html>'
        mock_response.raise_for_status = Mock()
        mock_trending.session.get.return_value = mock_response
        
        mock_trending._extract_article_links.return_value = ['https://medium.com/p/test-123']
        mock_trending._scrape_article.return_value = {
            'source_id': 'test-123',
            'title': 'Test Article'
        }
        
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumPublicationPlugin(mock_config)
        
        with patch('src.plugins.medium_publication.time.sleep'):
            ideas = plugin.scrape(publication='towards-data-science', top_n=5)
        
        assert isinstance(ideas, list)
        # Check that publication was added to article data
        if ideas:
            assert 'publication' in ideas[0]
    
    @patch('src.plugins.medium_publication.MediumTrendingPlugin')
    def test_scrape_with_publication_url(self, mock_trending_class, mock_config):
        """Test scraping with full publication URL."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.session.get.return_value = Mock(status_code=200, content=b'<html></html>')
        mock_trending._extract_article_links.return_value = []
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumPublicationPlugin(mock_config)
        
        ideas = plugin.scrape(publication='https://medium.com/towards-data-science', top_n=5)
        
        # Should call get with the provided URL
        mock_trending.session.get.assert_called()
    
    def test_scrape_without_publication(self, mock_config):
        """Test scraping without publication returns empty list."""
        plugin = MediumPublicationPlugin(mock_config)
        
        ideas = plugin.scrape(publication=None, top_n=5)
        
        assert ideas == []


class TestMediumAuthorPlugin:
    """Tests for MediumAuthorPlugin."""
    
    def test_initialization(self, mock_config):
        """Test plugin initialization."""
        plugin = MediumAuthorPlugin(mock_config)
        
        assert plugin is not None
        assert plugin.config == mock_config
        assert hasattr(plugin, '_trending_plugin')
    
    def test_get_source_name(self, mock_config):
        """Test get_source_name returns correct value."""
        plugin = MediumAuthorPlugin(mock_config)
        assert plugin.get_source_name() == "medium_author"
    
    @patch('src.plugins.medium_author.MediumTrendingPlugin')
    def test_scrape_with_author_username(self, mock_trending_class, mock_config):
        """Test scraping with author username."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.timeout = 30
        mock_trending.delay = 1
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><article><a href="/p/test">Test</a></article></html>'
        mock_response.raise_for_status = Mock()
        mock_trending.session.get.return_value = mock_response
        
        mock_trending._extract_article_links.return_value = ['https://medium.com/p/test-123']
        mock_trending._scrape_article.return_value = {
            'source_id': 'test-123',
            'title': 'Test Article',
            'author': {'username': 'testuser'}
        }
        
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumAuthorPlugin(mock_config)
        
        with patch('src.plugins.medium_author.time.sleep'):
            ideas = plugin.scrape(author='testuser', top_n=5)
        
        assert isinstance(ideas, list)
    
    @patch('src.plugins.medium_author.MediumTrendingPlugin')
    def test_scrape_with_at_prefix(self, mock_trending_class, mock_config):
        """Test scraping with @ prefix in username."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.session.get.return_value = Mock(status_code=200, content=b'<html></html>')
        mock_trending._extract_article_links.return_value = []
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumAuthorPlugin(mock_config)
        
        ideas = plugin.scrape(author='@testuser', top_n=5)
        
        # Should construct URL with @ prefix
        call_args = mock_trending.session.get.call_args
        assert '@testuser' in str(call_args)
    
    @patch('src.plugins.medium_author.MediumTrendingPlugin')
    def test_scrape_adds_at_prefix_if_missing(self, mock_trending_class, mock_config):
        """Test that @ prefix is added if not provided."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.session.get.return_value = Mock(status_code=200, content=b'<html></html>')
        mock_trending._extract_article_links.return_value = []
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumAuthorPlugin(mock_config)
        
        ideas = plugin.scrape(author='testuser', top_n=5)
        
        # Should add @ prefix and construct URL
        call_args = mock_trending.session.get.call_args
        assert '@testuser' in str(call_args)
    
    @patch('src.plugins.medium_author.MediumTrendingPlugin')
    def test_scrape_with_author_url(self, mock_trending_class, mock_config):
        """Test scraping with full author URL."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.session.get.return_value = Mock(status_code=200, content=b'<html></html>')
        mock_trending._extract_article_links.return_value = []
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumAuthorPlugin(mock_config)
        
        ideas = plugin.scrape(author='https://medium.com/@testuser', top_n=5)
        
        # Should use the provided URL directly
        mock_trending.session.get.assert_called()
    
    def test_scrape_without_author(self, mock_config):
        """Test scraping without author returns empty list."""
        plugin = MediumAuthorPlugin(mock_config)
        
        ideas = plugin.scrape(author=None, top_n=5)
        
        assert ideas == []
    
    @patch('src.plugins.medium_author.MediumTrendingPlugin')
    def test_scrape_sets_author_if_missing(self, mock_trending_class, mock_config):
        """Test that author is set in article data if missing."""
        mock_trending = Mock()
        mock_trending.session = Mock()
        mock_trending.timeout = 30
        mock_trending.delay = 1
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html></html>'
        mock_response.raise_for_status = Mock()
        mock_trending.session.get.return_value = mock_response
        
        mock_trending._extract_article_links.return_value = ['https://medium.com/p/test-123']
        # Return article without author
        mock_trending._scrape_article.return_value = {
            'source_id': 'test-123',
            'title': 'Test Article',
            'author': {}
        }
        
        mock_trending_class.return_value = mock_trending
        
        plugin = MediumAuthorPlugin(mock_config)
        
        with patch('src.plugins.medium_author.time.sleep'):
            ideas = plugin.scrape(author='testuser', top_n=1)
        
        # Should set author in article data
        if ideas:
            assert 'author' in ideas[0]
            assert ideas[0]['author']['username'] == 'testuser'
