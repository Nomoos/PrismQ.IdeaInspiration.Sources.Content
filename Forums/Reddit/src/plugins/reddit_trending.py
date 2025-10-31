"""Reddit Trending plugin for scraping r/all and r/popular trending posts."""

import praw
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class RedditTrendingPlugin(SourcePlugin):
    """Plugin for scraping trending posts from r/all and r/popular.
    
    Uses PRAW (Python Reddit API Wrapper) to access Reddit's official API.
    Follows Open/Closed Principle (OCP) - open for extension, closed for modification.
    """
    
    def __init__(self, config):
        """Initialize Reddit trending plugin.
        
        Args:
            config: Configuration object with Reddit credentials
            
        Raises:
            ValueError: If PRAW is not installed or credentials are missing
        """
        super().__init__(config)
        
        # Validate Reddit credentials
        if not config.reddit_client_id or not config.reddit_client_secret:
            raise ValueError(
                "Reddit API credentials required. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in .env file. Get credentials from "
                "https://www.reddit.com/prefs/apps"
            )
        
        # Initialize PRAW Reddit instance
        try:
            self.reddit = praw.Reddit(
                client_id=config.reddit_client_id,
                client_secret=config.reddit_client_secret,
                user_agent=config.reddit_user_agent
            )
            # Set read-only mode
            self.reddit.read_only = True
        except Exception as e:
            raise ValueError(f"Failed to initialize Reddit API: {e}")
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "reddit_trending"
    
    def scrape(self, subreddit: str = "all", limit: Optional[int] = None, 
               popular: bool = False) -> List[Dict[str, Any]]:
        """Scrape trending posts from specified subreddit.
        
        This is the base scrape() method that implements the SourcePlugin interface.
        
        Args:
            subreddit: Subreddit name (default: 'all' for r/all)
            limit: Maximum number of posts to scrape (uses config if not provided)
            popular: If True, scrape from r/popular instead
            
        Returns:
            List of idea dictionaries
        """
        if popular:
            return self.scrape_popular(limit=limit)
        
        return self.scrape_trending(subreddit=subreddit, limit=limit)
    
    def scrape_trending(self, subreddit: str = "all", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape trending posts from specified subreddit.
        
        Args:
            subreddit: Subreddit name (default: 'all' for r/all)
            limit: Maximum number of posts to scrape (uses config if not provided)
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.reddit_trending_max_posts
        
        print(f"Scraping {limit} trending posts from r/{subreddit}...")
        
        try:
            # Get subreddit
            sub = self.reddit.subreddit(subreddit)
            
            # Scrape hot/trending posts
            for post in sub.hot(limit=limit):
                # Convert post to idea format
                idea = self._post_to_idea(post)
                if idea:
                    ideas.append(idea)
                    print(f"  ✓ {post.title[:60]}... (score: {post.score})")
        
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
        
        return ideas
    
    def scrape_popular(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape trending posts from r/popular.
        
        Args:
            limit: Maximum number of posts to scrape
            
        Returns:
            List of idea dictionaries
        """
        return self.scrape(subreddit="popular", limit=limit)
    
    def _post_to_idea(self, post) -> Optional[Dict[str, Any]]:
        """Convert Reddit post to idea dictionary.
        
        Args:
            post: PRAW Submission object
            
        Returns:
            Idea dictionary or None if conversion fails
        """
        try:
            # Extract tags: subreddit, flair, and basic keywords from title
            tags = [post.subreddit.display_name]
            
            # Add flair if available
            if post.link_flair_text:
                tags.append(post.link_flair_text)
            
            # Build metrics dictionary
            metrics = {
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'ups': post.ups,
                'total_awards_received': post.total_awards_received,
                'num_views': getattr(post, 'view_count', 0) or 0,
                'all_awardings': post.all_awardings if hasattr(post, 'all_awardings') else [],
                'created_utc': post.created_utc,
            }
            
            # Add author info if available
            if post.author:
                metrics['author'] = {
                    'name': post.author.name,
                    'link_karma': getattr(post.author, 'link_karma', 0),
                    'comment_karma': getattr(post.author, 'comment_karma', 0),
                }
            
            # Add subreddit info
            metrics['subreddit'] = {
                'name': post.subreddit.display_name,
                'subscribers': post.subreddit.subscribers,
                'type': getattr(post.subreddit, 'subreddit_type', 'public'),
            }
            
            # Add content info
            metrics['content'] = {
                'type': 'text' if post.is_self else 'link',
                'url': post.url if not post.is_self else None,
                'domain': post.domain,
            }
            
            return {
                'source_id': post.id,
                'title': post.title,
                'description': post.selftext if post.is_self else post.url,
                'tags': self.format_tags(tags),
                'metrics': metrics,
            }
        
        except Exception as e:
            print(f"  ✗ Error converting post: {e}")
            return None
