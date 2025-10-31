"""Reddit Rising plugin for scraping rising posts."""

import praw
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class RedditRisingPlugin(SourcePlugin):
    """Plugin for scraping rising posts from Reddit.
    
    Rising posts are posts that are quickly gaining traction,
    making them good indicators of viral potential.
    """
    
    def __init__(self, config):
        """Initialize Reddit rising plugin.
        
        Args:
            config: Configuration object with Reddit credentials
        """
        super().__init__(config)
        
        # Validate credentials
        if not config.reddit_client_id or not config.reddit_client_secret:
            raise ValueError("Reddit API credentials required.")
        
        # Initialize PRAW
        try:
            self.reddit = praw.Reddit(
                client_id=config.reddit_client_id,
                client_secret=config.reddit_client_secret,
                user_agent=config.reddit_user_agent
            )
            self.reddit.read_only = True
        except Exception as e:
            raise ValueError(f"Failed to initialize Reddit API: {e}")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "reddit_rising"
    
    def scrape(self, subreddit: str = "all", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape rising posts from specified subreddit.
        
        This is the base scrape() method that implements the SourcePlugin interface.
        Rising posts are posts that are quickly gaining traction,
        making them good indicators of viral potential.
        
        Args:
            subreddit: Subreddit name (default: 'all')
            limit: Maximum number of posts to scrape
            
        Returns:
            List of idea dictionaries
        """
        return self.scrape_rising(subreddit=subreddit, limit=limit)
    
    def scrape_rising(self, subreddit: str = "all", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape rising posts from specified subreddit.
        
        Args:
            subreddit: Subreddit name (default: 'all')
            limit: Maximum number of posts to scrape
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.reddit_rising_max_posts
        
        print(f"Scraping {limit} rising posts from r/{subreddit}...")
        
        try:
            sub = self.reddit.subreddit(subreddit)
            
            # Get rising posts
            for post in sub.rising(limit=limit):
                idea = self._post_to_idea(post)
                if idea:
                    ideas.append(idea)
                    print(f"  ✓ {post.title[:60]}... (score: {post.score})")
        
        except Exception as e:
            print(f"Error scraping rising posts from r/{subreddit}: {e}")
        
        return ideas
    
    def _post_to_idea(self, post) -> Optional[Dict[str, Any]]:
        """Convert Reddit post to idea dictionary."""
        try:
            tags = [post.subreddit.display_name]
            if post.link_flair_text:
                tags.append(post.link_flair_text)
            
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
            
            if post.author:
                metrics['author'] = {
                    'name': post.author.name,
                    'link_karma': getattr(post.author, 'link_karma', 0),
                    'comment_karma': getattr(post.author, 'comment_karma', 0),
                }
            
            metrics['subreddit'] = {
                'name': post.subreddit.display_name,
                'subscribers': post.subreddit.subscribers,
                'type': getattr(post.subreddit, 'subreddit_type', 'public'),
            }
            
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
