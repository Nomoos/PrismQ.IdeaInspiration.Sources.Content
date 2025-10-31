"""Article URL source plugin for scraping individual web articles.

This plugin uses trafilatura for extracting article content from URLs,
with fallback to newspaper3k for comprehensive metadata extraction.
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin


class ArticleUrlPlugin(SourcePlugin):
    """Plugin for scraping individual articles by URL."""
    
    def __init__(self, config):
        """Initialize article URL plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if required libraries are available
        self._check_dependencies()
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "web_article_url"
    
    def _check_dependencies(self):
        """Check if required libraries are installed."""
        self.has_trafilatura = False
        self.has_newspaper = False
        
        try:
            import trafilatura
            self.has_trafilatura = True
        except ImportError:
            pass
        
        try:
            import newspaper
            self.has_newspaper = True
        except ImportError:
            pass
        
        if not self.has_trafilatura and not self.has_newspaper:
            raise ValueError(
                "Neither trafilatura nor newspaper3k is installed. "
                "Install with: pip install trafilatura newspaper3k"
            )
    
    def scrape(self, urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Scrape articles from URLs.
        
        Args:
            urls: List of article URLs to scrape
        
        Returns:
            List of article dictionaries
        """
        if not urls:
            print("No URLs provided")
            return []
        
        articles = []
        
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] Scraping: {url}")
            
            try:
                article_data = self._extract_article(url)
                if article_data:
                    articles.append(article_data)
                else:
                    print(f"    ✗ Failed to extract content")
            except Exception as e:
                print(f"    ✗ Error: {e}")
        
        return articles
    
    def _extract_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract article content and metadata from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Article dictionary or None if extraction failed
        """
        # Try trafilatura first (faster and more robust)
        if self.has_trafilatura:
            article_data = self._extract_with_trafilatura(url)
            if article_data:
                return article_data
        
        # Fallback to newspaper3k
        if self.has_newspaper:
            article_data = self._extract_with_newspaper(url)
            if article_data:
                return article_data
        
        return None
    
    def _extract_with_trafilatura(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract article using trafilatura.
        
        Args:
            url: Article URL
            
        Returns:
            Article dictionary or None
        """
        try:
            import trafilatura
            from trafilatura import fetch_url, extract_metadata
            
            # Fetch the page
            downloaded = fetch_url(url)
            if not downloaded:
                return None
            
            # Extract content
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not text:
                return None
            
            # Extract metadata
            metadata = extract_metadata(downloaded)
            
            # Build article data
            article_data = {
                'source': 'web_article',
                'source_id': self._generate_id(url),
                'title': metadata.title if metadata else url,
                'description': metadata.description if metadata and metadata.description else text[:200],
                'tags': [],
                'author': {
                    'name': metadata.author if metadata and metadata.author else None
                },
                'source_info': {
                    'domain': self._extract_domain(url),
                    'publication': metadata.sitename if metadata and metadata.sitename else None
                },
                'content': {
                    'text': text,
                    'html': downloaded[:1000],  # Store snippet
                },
                'url': url,
                'published_at': metadata.date if metadata and metadata.date else None,
                'metrics': {
                    'word_count': len(text.split()),
                    'reading_time_min': max(1, len(text.split()) // 200),
                }
            }
            
            # Add tags if available
            if metadata and metadata.tags:
                article_data['tags'] = metadata.tags
            
            return article_data
            
        except Exception as e:
            print(f"    Trafilatura error: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract article using newspaper3k.
        
        Args:
            url: Article URL
            
        Returns:
            Article dictionary or None
        """
        try:
            from newspaper import Article
            
            article = Article(url)
            article.download()
            article.parse()
            
            # Try to extract NLP features (keywords)
            try:
                article.nlp()
            except Exception:
                pass  # NLP features are optional
            
            if not article.text:
                return None
            
            # Build article data
            article_data = {
                'source': 'web_article',
                'source_id': self._generate_id(url),
                'title': article.title or url,
                'description': article.meta_description or article.text[:200],
                'tags': list(article.keywords) if hasattr(article, 'keywords') else [],
                'author': {
                    'name': ', '.join(article.authors) if article.authors else None
                },
                'source_info': {
                    'domain': self._extract_domain(url),
                    'publication': article.meta_site_name or None
                },
                'content': {
                    'text': article.text,
                    'html': article.html[:1000] if article.html else '',
                    'top_image': article.top_image or None,
                    'images': list(article.images) if article.images else []
                },
                'url': url,
                'published_at': article.publish_date.isoformat() if article.publish_date else None,
                'metrics': {
                    'word_count': len(article.text.split()),
                    'reading_time_min': max(1, len(article.text.split()) // 200),
                }
            }
            
            return article_data
            
        except Exception as e:
            print(f"    Newspaper error: {e}")
            return None
    
    def _generate_id(self, url: str) -> str:
        """Generate unique ID from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Unique hash-based ID
        """
        return hashlib.sha256(url.encode()).hexdigest()[:16]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
