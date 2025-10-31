"""Tests for article_rss plugin."""

import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        yield config


def test_plugin_initialization(mock_config):
    """Test plugin initialization."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            assert plugin.config == mock_config


def test_initialization_without_feedparser(mock_config):
    """Test that ValueError is raised when feedparser is not available."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=False):
        with pytest.raises(ValueError, match="feedparser is not installed"):
            from src.plugins.article_rss import ArticleRssPlugin
            ArticleRssPlugin(mock_config)


def test_get_source_name(mock_config):
    """Test get_source_name returns correct name."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            assert plugin.get_source_name() == "web_article_rss"


def test_scrape_empty_feed_urls(mock_config):
    """Test scraping with no feed URLs provided."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            articles = plugin.scrape(None)
            assert articles == []
            
            articles = plugin.scrape([])
            assert articles == []


def test_scrape_with_feed_urls(mock_config):
    """Test scraping with feed URLs."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            mock_articles = [
                {'title': 'Article 1', 'source_id': 'test1'},
                {'title': 'Article 2', 'source_id': 'test2'}
            ]
            
            with patch.object(plugin, '_parse_feed', return_value=mock_articles):
                articles = plugin.scrape(['https://example.com/rss'])
                assert len(articles) == 2
                assert articles[0]['title'] == 'Article 1'


def test_scrape_handles_exceptions(mock_config):
    """Test that scrape handles exceptions gracefully."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            with patch.object(plugin, '_parse_feed', side_effect=Exception("Feed error")):
                articles = plugin.scrape(['https://example.com/rss'])
                assert len(articles) == 0


def test_parse_feed_empty_entries(mock_config):
    """Test feed parsing with no entries."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            mock_feed = Mock()
            mock_feed.entries = []
            
            with patch('feedparser.parse', return_value=mock_feed):
                articles = plugin._parse_feed('https://example.com/rss', 10)
                assert len(articles) == 0


def test_generate_id(mock_config):
    """Test ID generation from URL."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            url1 = "https://example.com/article1"
            url2 = "https://example.com/article2"
            
            id1 = plugin._generate_id(url1)
            id2 = plugin._generate_id(url2)
            
            # Different URLs should generate different IDs
            assert id1 != id2
            
            # Same URL should generate same ID
            id1_again = plugin._generate_id(url1)
            assert id1 == id1_again
            
            # ID should be 16 characters
            assert len(id1) == 16


def test_extract_domain(mock_config):
    """Test domain extraction from URL."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            assert plugin._extract_domain('https://example.com/article') == 'example.com'
            assert plugin._extract_domain('https://www.test.org/feed') == 'www.test.org'


def test_strip_html(mock_config):
    """Test HTML stripping."""
    with patch('src.plugins.article_rss.ArticleRssPlugin._check_feedparser', return_value=True):
        with patch('src.plugins.article_url.ArticleUrlPlugin'):
            from src.plugins.article_rss import ArticleRssPlugin
            plugin = ArticleRssPlugin(mock_config)
            
            html = '<p>Hello <strong>World</strong>!</p>'
            text = plugin._strip_html(html)
            assert 'Hello' in text
            assert 'World' in text
            assert '<p>' not in text
            assert '<strong>' not in text
