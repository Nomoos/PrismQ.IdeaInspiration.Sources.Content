"""TikTok Trending source plugin for scraping trending videos.

This plugin uses yt-dlp to scrape TikTok trending videos with comprehensive
metadata extraction.
"""

import json
import subprocess
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin


class TikTokTrendingPlugin(SourcePlugin):
    """Plugin for scraping ideas from TikTok trending page using yt-dlp."""
    
    def __init__(self, config):
        """Initialize TikTok trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if yt-dlp is available
        if not self._check_ytdlp():
            raise ValueError("yt-dlp is not installed. Install with: pip install yt-dlp")
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "tiktok_trending"
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is installed.
        
        Returns:
            True if yt-dlp is available
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def scrape(self, max_videos: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape trending TikTok videos.
        
        Args:
            max_videos: Number of videos to scrape (optional, uses config if not provided)
        
        Returns:
            List of idea dictionaries
        """
        ideas = []
        
        if max_videos is None:
            max_videos = getattr(self.config, 'tiktok_trending_max', 10)
        
        print(f"Scraping trending TikTok videos (max: {max_videos})...")
        
        # Note: TikTok trending scraping is challenging without official API
        # This is a placeholder implementation showing the architecture
        # Real implementation would require a working TikTok scraping library
        
        print("⚠️  TikTok trending scraping requires additional setup:")
        print("   - Consider using TikTokApi (unofficial)")
        print("   - Or playwright-based scraping")
        print("   - Respect TikTok's ToS and rate limits")
        
        # Placeholder: Would normally call TikTok API or scraping library here
        # Example structure for when implemented:
        # videos = self._fetch_trending_videos(max_videos)
        # for video in videos:
        #     idea = self._video_to_idea(video)
        #     ideas.append(idea)
        
        return ideas
    
    def _fetch_trending_videos(self, max_videos: int) -> List[Dict[str, Any]]:
        """Fetch trending videos from TikTok.
        
        This is a placeholder for the actual implementation.
        Real implementation would use TikTokApi or similar library.
        
        Args:
            max_videos: Maximum number of videos to fetch
            
        Returns:
            List of video data dictionaries
        """
        # Placeholder for actual TikTok API integration
        # Example using TikTokApi (unofficial):
        # from TikTokApi import TikTokApi
        # api = TikTokApi()
        # trending = api.trending.videos(count=max_videos)
        # return [video.as_dict for video in trending]
        
        return []
    
    def _video_to_idea(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TikTok video data to idea format.
        
        Args:
            video_data: TikTok video data
            
        Returns:
            Idea dictionary
        """
        # Extract basic info
        video_id = video_data.get('id', '')
        title = video_data.get('desc', '') or video_data.get('title', 'Untitled')
        description = video_data.get('desc', '')
        
        # Extract hashtags
        hashtags = []
        if 'challenges' in video_data:
            hashtags = [challenge.get('title', '') for challenge in video_data.get('challenges', [])]
        elif 'hashtags' in video_data:
            hashtags = video_data.get('hashtags', [])
        
        # Extract creator info
        creator = video_data.get('author', {})
        creator_username = creator.get('uniqueId', '') or creator.get('username', '')
        creator_followers = creator.get('followerCount', 0)
        creator_verified = creator.get('verified', False)
        
        # Extract engagement metrics
        stats = video_data.get('stats', {})
        view_count = stats.get('playCount', 0)
        like_count = stats.get('diggCount', 0)
        comment_count = stats.get('commentCount', 0)
        share_count = stats.get('shareCount', 0)
        save_count = stats.get('collectCount', 0)
        
        # Extract video info
        video_info = video_data.get('video', {})
        duration = video_info.get('duration', 0)
        
        # Extract music info
        music = video_data.get('music', {})
        music_title = music.get('title', '')
        
        # Build metrics dictionary
        metrics = {
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'share_count': share_count,
            'save_count': save_count,
            'engagement_rate': self._calculate_engagement_rate(view_count, like_count, comment_count, share_count),
            'platform_specific': {
                'video_id': video_id,
                'username': creator_username,
                'creator_followers': creator_followers,
                'creator_verified': creator_verified,
                'duration_seconds': duration,
                'music': music_title,
                'video_url': f"https://www.tiktok.com/@{creator_username}/video/{video_id}",
                'created_time': video_data.get('createTime', 0),
            }
        }
        
        return {
            'source_id': video_id,
            'title': title,
            'description': description,
            'tags': self.format_tags(hashtags),
            'metrics': metrics,
        }
    
    def _calculate_engagement_rate(self, views: int, likes: int, comments: int, shares: int) -> float:
        """Calculate engagement rate.
        
        Args:
            views: View count
            likes: Like count
            comments: Comment count
            shares: Share count
            
        Returns:
            Engagement rate as percentage
        """
        if views == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100
