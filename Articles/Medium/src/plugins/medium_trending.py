"""Medium Trending articles plugin for scraping idea inspirations.

This plugin scrapes trending articles from Medium.com.
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin


class MediumTrendingPlugin(SourcePlugin):
    """Plugin for scraping trending articles from Medium."""
    
    def __init__(self, config):
        """Initialize Medium trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = config.request_timeout
        self.delay = config.request_delay
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "medium_trending"
    
    def scrape(self, top_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape trending articles from Medium.
        
        Args:
            top_n: Number of articles to scrape (optional, uses config if not provided)
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if top_n is None:
            top_n = getattr(self.config, 'medium_trending_max_articles', 10)
        
        print(f"Scraping trending Medium articles...")
        
        try:
            # Fetch Medium trending page
            url = "https://medium.com/tag/trending"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract article links and metadata
            # Note: Medium's structure may change, this is a simplified version
            article_links = self._extract_article_links(soup, top_n)
            
            # Scrape each article
            for i, article_url in enumerate(article_links, 1):
                print(f"  [{i}/{len(article_links)}] Scraping: {article_url}")
                
                # Add delay between requests
                if i > 1:
                    time.sleep(self.delay)
                
                article_data = self._scrape_article(article_url)
                if article_data:
                    ideas.append(article_data)
            
            print(f"Successfully scraped {len(ideas)} trending articles")
            
        except requests.RequestException as e:
            print(f"Error scraping Medium trending: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return ideas
    
    def _extract_article_links(self, soup: BeautifulSoup, limit: int) -> List[str]:
        """Extract article links from trending page.
        
        Args:
            soup: BeautifulSoup object of the page
            limit: Maximum number of links to extract
        
        Returns:
            List of article URLs
        """
        links = []
        
        # Find article links (Medium uses various selectors)
        # This is a simplified approach
        article_elements = soup.find_all('article', limit=limit * 2)
        
        for article in article_elements:
            # Find link within article
            link_elem = article.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                # Ensure it's a full URL
                if href.startswith('/'):
                    href = f"https://medium.com{href}"
                elif not href.startswith('http'):
                    continue
                
                # Avoid duplicates
                if href not in links:
                    links.append(href)
                
                if len(links) >= limit:
                    break
        
        return links
    
    def _scrape_article(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single Medium article.
        
        Args:
            article_url: URL of the article
        
        Returns:
            Article data dictionary or None if failed
        """
        try:
            response = self.session.get(article_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract article ID from URL
            # Medium URLs typically: https://medium.com/@author/title-articleid
            article_id = article_url.split('/')[-1].split('-')[-1] if '/' in article_url else article_url
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"
            
            # Extract subtitle/description
            subtitle_elem = soup.find('h2', class_='pw-subtitle-paragraph')
            subtitle = subtitle_elem.get_text(strip=True) if subtitle_elem else ""
            
            # Extract author
            author_elem = soup.find('a', attrs={'data-action': 'show-user-card'})
            author_username = author_elem.get_text(strip=True) if author_elem else "Unknown"
            
            # Extract tags (simplified)
            tags = []
            tag_elems = soup.find_all('a', href=lambda x: x and '/tag/' in str(x))
            for tag_elem in tag_elems[:5]:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
            
            # Extract claps (simplified - actual implementation may differ)
            claps = 0
            clap_elem = soup.find('button', attrs={'data-action': 'show-recommends'})
            if clap_elem:
                clap_text = clap_elem.get_text(strip=True)
                # Try to parse number from text
                import re
                match = re.search(r'(\d+)', clap_text)
                if match:
                    claps = int(match.group(1))
            
            # Extract reading time
            reading_time = 0
            time_elem = soup.find('span', string=lambda x: x and 'min read' in str(x))
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                import re
                match = re.search(r'(\d+)', time_text)
                if match:
                    reading_time = int(match.group(1))
            
            # Extract article content (simplified)
            content = ""
            article_body = soup.find('article')
            if article_body:
                paragraphs = article_body.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:10]])
            
            # Build idea dictionary
            idea = {
                'source_id': article_id,
                'title': title,
                'description': subtitle,
                'tags': self.format_tags(tags),
                'author': {
                    'username': author_username,
                    'followers': None  # Would need additional request
                },
                'metrics': {
                    'claps': claps,
                    'responses': 0,  # Would need additional scraping
                    'reading_time_min': reading_time,
                    'views': 0,  # Medium doesn't expose this publicly
                },
                'publish_date': datetime.now().isoformat(),
                'article_url': article_url,
                'article_content': content,
            }
            
            return idea
            
        except requests.RequestException as e:
            print(f"Error scraping article {article_url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error scraping article {article_url}: {e}")
            return None
