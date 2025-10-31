"""Tests for article_sitemap plugin."""

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
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        assert plugin.config == mock_config


def test_get_source_name(mock_config):
    """Test get_source_name returns correct name."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        assert plugin.get_source_name() == "web_article_sitemap"


def test_scrape_empty_sitemap_urls(mock_config):
    """Test scraping with no sitemap URLs provided."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        articles = plugin.scrape(None)
        assert articles == []
        
        articles = plugin.scrape([])
        assert articles == []


def test_scrape_with_sitemap_urls(mock_config):
    """Test scraping with sitemap URLs."""
    with patch('src.plugins.article_url.ArticleUrlPlugin') as MockUrlPlugin:
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        
        mock_url_plugin = Mock()
        MockUrlPlugin.return_value = mock_url_plugin
        
        plugin = ArticleSitemapPlugin(mock_config)
        plugin.url_plugin = mock_url_plugin
        
        mock_urls = [
            'https://example.com/article1',
            'https://example.com/article2'
        ]
        
        mock_articles = [
            {'title': 'Article 1', 'source_id': 'test1'},
            {'title': 'Article 2', 'source_id': 'test2'}
        ]
        
        with patch.object(plugin, '_parse_sitemap', return_value=mock_urls):
            mock_url_plugin.scrape.return_value = mock_articles
            
            articles = plugin.scrape(['https://example.com/sitemap.xml'])
            assert len(articles) == 2
            assert articles[0]['title'] == 'Article 1'


def test_scrape_handles_exceptions(mock_config):
    """Test that scrape handles exceptions gracefully."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        with patch.object(plugin, '_parse_sitemap', side_effect=Exception("Sitemap error")):
            articles = plugin.scrape(['https://example.com/sitemap.xml'])
            assert len(articles) == 0


def test_parse_sitemap_regular(mock_config):
    """Test parsing a regular sitemap with URLs."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/article1</loc>
            </url>
            <url>
                <loc>https://example.com/article2</loc>
            </url>
            <url>
                <loc>https://example.com/article3</loc>
            </url>
        </urlset>'''
        
        mock_response = Mock()
        mock_response.content = sitemap_xml.encode()
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            urls = plugin._parse_sitemap('https://example.com/sitemap.xml', 10)
            assert len(urls) == 3
            assert 'https://example.com/article1' in urls
            assert 'https://example.com/article2' in urls


def test_parse_sitemap_with_max_limit(mock_config):
    """Test that parse_sitemap respects max_articles limit."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/article1</loc></url>
            <url><loc>https://example.com/article2</loc></url>
            <url><loc>https://example.com/article3</loc></url>
            <url><loc>https://example.com/article4</loc></url>
            <url><loc>https://example.com/article5</loc></url>
        </urlset>'''
        
        mock_response = Mock()
        mock_response.content = sitemap_xml.encode()
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            urls = plugin._parse_sitemap('https://example.com/sitemap.xml', 3)
            assert len(urls) <= 3


def test_parse_sitemap_http_error(mock_config):
    """Test that parse_sitemap handles HTTP errors."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                plugin._parse_sitemap('https://example.com/sitemap.xml', 10)


def test_parse_sitemap_timeout(mock_config):
    """Test that parse_sitemap respects timeout setting."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/article1</loc></url>
        </urlset>'''
        
        mock_response = Mock()
        mock_response.content = sitemap_xml.encode()
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            plugin._parse_sitemap('https://example.com/sitemap.xml', 10)
            
            # Verify timeout was passed
            call_kwargs = mock_get.call_args[1]
            assert 'timeout' in call_kwargs


def test_parse_sitemap_malformed_xml(mock_config):
    """Test that parse_sitemap handles malformed XML."""
    with patch('src.plugins.article_url.ArticleUrlPlugin'):
        from src.plugins.article_sitemap import ArticleSitemapPlugin
        plugin = ArticleSitemapPlugin(mock_config)
        
        malformed_xml = '<urlset><url><loc>incomplete'
        
        mock_response = Mock()
        mock_response.content = malformed_xml.encode()
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                plugin._parse_sitemap('https://example.com/sitemap.xml', 10)
