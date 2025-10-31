"""Reddit Search plugin for keyword-based discovery."""

import praw
from typing import List, Dict, Any, Optional
from . import SourcePlugin


class RedditSearchPlugin(SourcePlugin):
    """Plugin for searching Reddit posts by keywords.
    
    Enables discovery of posts matching specific search criteria.
    """
    
    def __init__(self, config):
        """Initialize Reddit search plugin.
        
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
        return "reddit_search"
    
    def scrape(self, query: str = "", subreddit: str = "all", 
               limit: Optional[int] = None, sort: str = "relevance",
               by_flair: bool = False) -> List[Dict[str, Any]]:
        """Search Reddit posts by keyword.
        
        This is the base scrape() method that implements the SourcePlugin interface.
        
        Args:
            query: Search query or flair text
            subreddit: Subreddit to search in (default: 'all')
            limit: Maximum number of posts to return
            sort: Sort method - 'relevance', 'hot', 'top', 'new', 'comments'
            by_flair: If True, search by flair instead of keyword
            
        Returns:
            List of idea dictionaries
        """
        if by_flair:
            return self.scrape_by_flair(subreddit=subreddit, flair=query, limit=limit)
        
        return self.scrape_by_query(query=query, subreddit=subreddit, limit=limit, sort=sort)
    
    def scrape_by_query(self, query: str, subreddit: str = "all", 
                        limit: Optional[int] = None, sort: str = "relevance") -> List[Dict[str, Any]]:
        """Search Reddit posts by keyword.
        
        Args:
            query: Search query
            subreddit: Subreddit to search in (default: 'all')
            limit: Maximum number of posts to return
            sort: Sort method - 'relevance', 'hot', 'top', 'new', 'comments'
            
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if limit is None:
            limit = self.config.reddit_search_max_posts
        
        print(f"Searching r/{subreddit} for '{query}' (sort: {sort}, limit: {limit})...")
        
        try:
            sub = self.reddit.subreddit(subreddit)
            
            # Search posts
            for post in sub.search(query, sort=sort, limit=limit):
                idea = self._post_to_idea(post)
                if idea:
                    ideas.append(idea)
                    print(f"  ✓ {post.title[:60]}... (score: {post.score})")
        
        except Exception as e:
            print(f"Error searching r/{subreddit} for '{query}': {e}")
        
        return ideas
    
    def scrape_by_flair(self, subreddit: str, flair: str, 
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search posts by flair in a subreddit.
        
        Args:
            subreddit: Subreddit name
            flair: Flair text to search for
            limit: Maximum number of posts
            
        Returns:
            List of idea dictionaries
        """
        # Use search with flair filter
        query = f'flair:"{flair}"'
        return self.scrape(query, subreddit=subreddit, limit=limit)
    
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
