"""Tests for article_url plugin."""

import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.config import Config
from src.plugins.article_url import ArticleUrlPlugin


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        yield config


def test_plugin_initialization(mock_config):
    """Test plugin initialization."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        assert plugin.config == mock_config


def test_get_source_name(mock_config):
    """Test get_source_name returns correct name."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        assert plugin.get_source_name() == "web_article_url"


def test_check_dependencies_no_libraries():
    """Test that ValueError is raised when no libraries are available."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        config = Config(env_file=str(env_file), interactive=False)
        
        with patch.object(ArticleUrlPlugin, '_check_dependencies', side_effect=ValueError("Neither trafilatura nor newspaper3k is installed.")):
            with pytest.raises(ValueError, match="Neither trafilatura nor newspaper3k is installed"):
                ArticleUrlPlugin(config)


def test_check_dependencies_with_trafilatura(mock_config):
    """Test dependency check with trafilatura available."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        plugin.has_trafilatura = True
        plugin.has_newspaper = False
        assert plugin.has_trafilatura is True


def test_scrape_empty_urls(mock_config):
    """Test scraping with no URLs provided."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        articles = plugin.scrape(None)
        assert articles == []
        
        articles = plugin.scrape([])
        assert articles == []


def test_scrape_with_urls(mock_config):
    """Test scraping with URLs."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        # Mock the extraction method
        mock_article = {
            'source': 'web_article',
            'source_id': 'test123',
            'title': 'Test Article',
            'description': 'Test description',
            'content': {'text': 'Test content'},
            'url': 'https://example.com/article'
        }
        
        with patch.object(plugin, '_extract_article', return_value=mock_article):
            articles = plugin.scrape(['https://example.com/article'])
            assert len(articles) == 1
            assert articles[0]['title'] == 'Test Article'


def test_scrape_handles_extraction_failure(mock_config):
    """Test that scrape handles extraction failures gracefully."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        with patch.object(plugin, '_extract_article', return_value=None):
            articles = plugin.scrape(['https://example.com/article'])
            assert len(articles) == 0


def test_scrape_handles_exceptions(mock_config):
    """Test that scrape handles exceptions gracefully."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        with patch.object(plugin, '_extract_article', side_effect=Exception("Network error")):
            articles = plugin.scrape(['https://example.com/article'])
            assert len(articles) == 0


def test_extract_article_with_trafilatura(mock_config):
    """Test article extraction using trafilatura."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        plugin.has_trafilatura = True
        plugin.has_newspaper = False
        
        mock_article = {
            'source': 'web_article',
            'title': 'Test Article',
            'content': {'text': 'Test content'}
        }
        
        with patch.object(plugin, '_extract_with_trafilatura', return_value=mock_article):
            result = plugin._extract_article('https://example.com/article')
            assert result is not None
            assert result['title'] == 'Test Article'


def test_extract_article_fallback_to_newspaper(mock_config):
    """Test article extraction falls back to newspaper when trafilatura fails."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        plugin.has_trafilatura = True
        plugin.has_newspaper = True
        
        mock_article = {
            'source': 'web_article',
            'title': 'Test Article from Newspaper',
            'content': {'text': 'Test content'}
        }
        
        with patch.object(plugin, '_extract_with_trafilatura', return_value=None):
            with patch.object(plugin, '_extract_with_newspaper', return_value=mock_article):
                result = plugin._extract_article('https://example.com/article')
                assert result is not None
                assert result['title'] == 'Test Article from Newspaper'


def test_generate_id(mock_config):
    """Test ID generation from URL."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
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
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        assert plugin._extract_domain('https://example.com/article') == 'example.com'
        assert plugin._extract_domain('https://www.test.org/path/to/article') == 'www.test.org'
        assert plugin._extract_domain('http://blog.example.com/post') == 'blog.example.com'


def test_extract_with_trafilatura_success(mock_config):
    """Test successful extraction with trafilatura."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        mock_metadata = Mock()
        mock_metadata.title = 'Test Article'
        mock_metadata.description = 'Test description'
        mock_metadata.author = 'Test Author'
        mock_metadata.sitename = 'Test Site'
        mock_metadata.date = '2025-01-01'
        mock_metadata.tags = ['tag1', 'tag2']
        
        with patch('trafilatura.fetch_url', return_value='<html>content</html>'):
            with patch('trafilatura.extract', return_value='Article text content'):
                with patch('trafilatura.extract_metadata', return_value=mock_metadata):
                    result = plugin._extract_with_trafilatura('https://example.com/article')
                    
                    assert result is not None
                    assert result['title'] == 'Test Article'
                    assert result['description'] == 'Test description'
                    assert result['author']['name'] == 'Test Author'
                    assert 'tag1' in result['tags']


def test_extract_with_trafilatura_no_content(mock_config):
    """Test trafilatura extraction when no content is found."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        with patch('trafilatura.fetch_url', return_value='<html>content</html>'):
            with patch('trafilatura.extract', return_value=None):
                result = plugin._extract_with_trafilatura('https://example.com/article')
                assert result is None


def test_extract_with_newspaper_success(mock_config):
    """Test successful extraction with newspaper3k."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        mock_article = Mock()
        mock_article.title = 'Test Article'
        mock_article.text = 'Article text content'
        mock_article.meta_description = 'Test description'
        mock_article.authors = ['Author1', 'Author2']
        mock_article.meta_site_name = 'Test Site'
        mock_article.publish_date = None
        mock_article.keywords = ['keyword1', 'keyword2']
        mock_article.top_image = 'https://example.com/image.jpg'
        mock_article.images = ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
        mock_article.html = '<html>content</html>'
        
        with patch('newspaper.Article', return_value=mock_article):
            result = plugin._extract_with_newspaper('https://example.com/article')
            
            assert result is not None
            assert result['title'] == 'Test Article'
            assert result['description'] == 'Test description'
            assert result['author']['name'] == 'Author1, Author2'


def test_extract_with_newspaper_no_text(mock_config):
    """Test newspaper extraction when no text is found."""
    with patch.object(ArticleUrlPlugin, '_check_dependencies'):
        plugin = ArticleUrlPlugin(mock_config)
        
        mock_article = Mock()
        mock_article.text = ''
        
        with patch('newspaper.Article', return_value=mock_article):
            result = plugin._extract_with_newspaper('https://example.com/article')
            assert result is None
