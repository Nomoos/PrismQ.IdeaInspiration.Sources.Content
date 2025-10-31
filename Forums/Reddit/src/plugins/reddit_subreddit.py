"""Reddit Subreddit plugin for scraping specific subreddit posts."""

import praw
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class RedditSubredditPlugin(SourcePlugin):
    """Plugin for scraping posts from specific subreddits.
    
    Supports hot, new, and top posts from any subreddit.
    """
    
    def __init__(self, config):
        """Initialize Reddit subreddit plugin.
        
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
                "REDDIT_CLIENT_SECRET in .env file."
            )
        
        # Initialize PRAW Reddit instance
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
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "reddit_subreddit"
    
    def scrape(self, subreddit: str = "all", limit: Optional[int] = None, 
               sort: str = "hot", time_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape posts from a specific subreddit.
        
        This is the base scrape() method that implements the SourcePlugin interface.
        
        Args:
            subreddit: Subreddit name (without r/ prefix)
            limit: Maximum number of posts to scrape
            sort: Sort method - 'hot', 'new', 'top', 'rising'
            time_filter: Time filter for 'top' sort - 'hour', 'day', 'week', 'month', 'year', 'all'
            
        Returns:
            List of idea dictionaries
        """
        if sort == "top" and time_filter:
            return self.scrape_top(subreddit=subreddit, time_filter=time_filter, limit=limit)
        
        return self.scrape_by_sort(subreddit=subreddit, limit=limit, sort=sort)
    
    def scrape_by_sort(self, subreddit: str, limit: Optional[int] = None, 
                       sort: str = "hot") -> List[Dict[str, Any]]:
        """Scrape posts from a specific subreddit with given sort method.
        
        Args:
            subreddit: Subreddit name (without r/ prefix)
            limit: Maximum number of posts to scrape
            sort: Sort method - 'hot', 'new', 'top', 'rising'
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.reddit_subreddit_max_posts
        
        print(f"Scraping {limit} {sort} posts from r/{subreddit}...")
        
        try:
            # Get subreddit
            sub = self.reddit.subreddit(subreddit)
            
            # Get posts based on sort method
            if sort == "hot":
                posts = sub.hot(limit=limit)
            elif sort == "new":
                posts = sub.new(limit=limit)
            elif sort == "top":
                posts = sub.top(limit=limit, time_filter="day")
            elif sort == "rising":
                posts = sub.rising(limit=limit)
            else:
                print(f"Invalid sort method: {sort}, using 'hot'")
                posts = sub.hot(limit=limit)
            
            # Convert posts to ideas
            for post in posts:
                idea = self._post_to_idea(post)
                if idea:
                    ideas.append(idea)
                    print(f"  ✓ {post.title[:60]}... (score: {post.score})")
        
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
        
        return ideas
    
    def scrape_top(self, subreddit: str, time_filter: str = "day", 
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape top posts from subreddit.
        
        Args:
            subreddit: Subreddit name
            time_filter: Time filter - 'hour', 'day', 'week', 'month', 'year', 'all'
            limit: Maximum number of posts
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.reddit_subreddit_max_posts
        
        print(f"Scraping {limit} top posts from r/{subreddit} ({time_filter})...")
        
        try:
            sub = self.reddit.subreddit(subreddit)
            posts = sub.top(limit=limit, time_filter=time_filter)
            
            for post in posts:
                idea = self._post_to_idea(post)
                if idea:
                    ideas.append(idea)
                    print(f"  ✓ {post.title[:60]}... (score: {post.score})")
        
        except Exception as e:
            print(f"Error scraping top posts from r/{subreddit}: {e}")
        
        return ideas
    
    def _post_to_idea(self, post) -> Optional[Dict[str, Any]]:
        """Convert Reddit post to idea dictionary.
        
        Args:
            post: PRAW Submission object
            
        Returns:
            Idea dictionary or None if conversion fails
        """
        try:
            # Extract tags
            tags = [post.subreddit.display_name]
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
            
            # Add author info
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
