"""Article RSS source plugin for scraping articles from RSS/Atom feeds.

This plugin uses feedparser to parse RSS/Atom feeds and extract article URLs,
then uses ArticleUrlPlugin to extract full content from each URL.
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin


class ArticleRssPlugin(SourcePlugin):
    """Plugin for scraping articles from RSS/Atom feeds."""
    
    def __init__(self, config):
        """Initialize article RSS plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if feedparser is available
        if not self._check_feedparser():
            raise ValueError("feedparser is not installed. Install with: pip install feedparser")
        
        # Import ArticleUrlPlugin for content extraction
        from .article_url import ArticleUrlPlugin
        self.url_plugin = ArticleUrlPlugin(config)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "web_article_rss"
    
    def _check_feedparser(self) -> bool:
        """Check if feedparser is installed.
        
        Returns:
            True if feedparser is available
        """
        try:
            import feedparser
            return True
        except ImportError:
            return False
    
    def scrape(self, feed_urls: Optional[List[str]] = None, max_articles: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape articles from RSS/Atom feeds.
        
        Args:
            feed_urls: List of RSS/Atom feed URLs
            max_articles: Maximum articles to scrape per feed (uses config if not provided)
        
        Returns:
            List of article dictionaries
        """
        if not feed_urls:
            print("No feed URLs provided")
            return []
        
        if max_articles is None:
            max_articles = getattr(self.config, 'web_article_max_articles', 10)
        
        all_articles = []
        
        for i, feed_url in enumerate(feed_urls, 1):
            print(f"  [{i}/{len(feed_urls)}] Parsing feed: {feed_url}")
            
            try:
                articles = self._parse_feed(feed_url, max_articles)
                all_articles.extend(articles)
                print(f"    ✓ Found {len(articles)} articles")
            except Exception as e:
                print(f"    ✗ Error parsing feed: {e}")
        
        return all_articles
    
    def _parse_feed(self, feed_url: str, max_articles: int) -> List[Dict[str, Any]]:
        """Parse RSS/Atom feed and extract articles.
        
        Args:
            feed_url: RSS/Atom feed URL
            max_articles: Maximum articles to extract
            
        Returns:
            List of article dictionaries
        """
        import feedparser
        
        # Parse the feed
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            return []
        
        articles = []
        
        # Process entries up to max_articles
        for entry in feed.entries[:max_articles]:
            try:
                article_data = self._process_entry(entry, feed)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                print(f"      ✗ Error processing entry: {e}")
        
        return articles
    
    def _process_entry(self, entry, feed) -> Optional[Dict[str, Any]]:
        """Process a single feed entry.
        
        Args:
            entry: Feed entry
            feed: Parent feed object
            
        Returns:
            Article dictionary or None
        """
        # Get article URL
        url = entry.get('link')
        if not url:
            return None
        
        # Try to extract full article content using URL plugin
        article_data = self.url_plugin._extract_article(url)
        
        # If extraction failed, use feed data as fallback
        if not article_data:
            article_data = self._fallback_from_feed_entry(entry, feed, url)
        else:
            # Enhance with feed metadata
            article_data = self._enhance_with_feed_metadata(article_data, entry, feed)
        
        return article_data
    
    def _fallback_from_feed_entry(self, entry, feed, url: str) -> Dict[str, Any]:
        """Create article data from feed entry when full extraction fails.
        
        Args:
            entry: Feed entry
            feed: Parent feed object
            url: Article URL
            
        Returns:
            Article dictionary
        """
        # Get content (prefer full content over summary)
        content = ""
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content = entry.summary
        
        # Extract publication date
        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                from time import mktime
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()
            except Exception:
                pass
        
        # Build article data
        article_data = {
            'source': 'web_article_rss',
            'source_id': self._generate_id(url),
            'title': entry.get('title', url),
            'description': entry.get('summary', '')[:500],
            'tags': [tag.get('term', '') for tag in entry.get('tags', []) if tag.get('term')],
            'author': {
                'name': entry.get('author', None)
            },
            'source_info': {
                'domain': self._extract_domain(url),
                'publication': feed.feed.get('title', None) if hasattr(feed, 'feed') else None
            },
            'content': {
                'text': self._strip_html(content) if content else '',
                'html': content[:1000] if content else '',
            },
            'url': url,
            'published_at': published_at,
            'metrics': {
                'word_count': len(self._strip_html(content).split()) if content else 0,
                'reading_time_min': max(1, len(self._strip_html(content).split()) // 200) if content else 1,
            }
        }
        
        return article_data
    
    def _enhance_with_feed_metadata(self, article_data: Dict[str, Any], entry, feed) -> Dict[str, Any]:
        """Enhance article data with feed metadata.
        
        Args:
            article_data: Existing article data
            entry: Feed entry
            feed: Parent feed object
            
        Returns:
            Enhanced article dictionary
        """
        # Add feed tags if not already present
        if not article_data.get('tags'):
            article_data['tags'] = [tag.get('term', '') for tag in entry.get('tags', []) if tag.get('term')]
        
        # Add publication info if not present
        if not article_data.get('source_info', {}).get('publication') and hasattr(feed, 'feed'):
            if 'source_info' not in article_data:
                article_data['source_info'] = {}
            article_data['source_info']['publication'] = feed.feed.get('title')
        
        # Update source to indicate RSS origin
        article_data['source'] = 'web_article_rss'
        
        return article_data
    
    def _strip_html(self, html: str) -> str:
        """Strip HTML tags from text.
        
        Args:
            html: HTML string
            
        Returns:
            Plain text
        """
        try:
            from html.parser import HTMLParser
            
            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.strict = False
                    self.convert_charrefs = True
                    self.fed = []
                
                def handle_data(self, d):
                    self.fed.append(d)
                
                def get_data(self):
                    return ''.join(self.fed)
            
            s = MLStripper()
            s.feed(html)
            return s.get_data()
        except Exception:
            return html
    
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
