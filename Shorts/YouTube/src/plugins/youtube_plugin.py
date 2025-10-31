"""YouTube source plugin for scraping idea inspirations from Shorts."""

from typing import List, Dict, Any
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from . import SourcePlugin, IdeaInspiration


class YouTubePlugin(SourcePlugin):
    """Plugin for scraping ideas from YouTube Shorts."""

    def __init__(self, config):
        """Initialize YouTube plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not config.youtube_api_key:
            raise ValueError("YouTube API key not configured")
        
        # Initialize YouTube API client
        self.youtube = build('youtube', 'v3', developerKey=config.youtube_api_key)

    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "youtube"

    def scrape(self) -> List[IdeaInspiration]:
        """Scrape ideas from YouTube Shorts.
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        try:
            # Search for YouTube Shorts
            # Note: YouTube Shorts are videos up to 3 minutes (180 seconds)
            search_response = self.youtube.search().list(
                q='#Shorts OR #YouTubeShorts ideas startup business',
                part='id,snippet',
                maxResults=self.config.youtube_max_results,
                type='video',
                videoDuration='short',  # Videos less than 4 minutes
                order='viewCount'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return ideas
            
            # Get detailed statistics for videos
            videos_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            for video in videos_response.get('items', []):
                # Filter for actual Shorts (<= 3 minutes / 180 seconds)
                duration = video['contentDetails']['duration']
                if not self._is_short(duration):
                    continue
                
                snippet = video['snippet']
                statistics = video['statistics']
                
                # Extract tags
                tags = self._extract_tags(snippet)
                
                # Build metadata dictionary with string values for SQLite compatibility
                metadata = {
                    'video_id': video['id'],
                    'channel_id': snippet.get('channelId', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'duration': duration,
                    'view_count': str(statistics.get('viewCount', 0)),
                    'like_count': str(statistics.get('likeCount', 0)),
                    'comment_count': str(statistics.get('commentCount', 0)),
                    'category_id': snippet.get('categoryId', ''),
                }
                
                # Create IdeaInspiration using from_video factory method
                idea = IdeaInspiration.from_video(
                    title=snippet['title'],
                    description=snippet.get('description', ''),
                    subtitle_text='',  # YouTube API doesn't provide captions directly
                    keywords=tags,
                    metadata=metadata,
                    source_id=video['id'],
                    source_url=f"https://www.youtube.com/watch?v={video['id']}",
                    source_created_by=snippet.get('channelTitle', ''),
                    source_created_at=snippet.get('publishedAt', '')
                )
                ideas.append(idea)
                
        except HttpError as e:
            print(f"YouTube API error: {e}")
        except Exception as e:
            print(f"Error scraping YouTube: {e}")
        
        return ideas

    def _extract_tags(self, snippet: Dict[str, Any]) -> List[str]:
        """Extract tags from YouTube video snippet.
        
        Args:
            snippet: Video snippet from YouTube API
            
        Returns:
            List of tag strings
        """
        tags = ['youtube_shorts']
        
        # Add channel name
        if 'channelTitle' in snippet:
            tags.append(snippet['channelTitle'])
        
        # Add category if available
        if 'categoryId' in snippet:
            tags.append(f"category_{snippet['categoryId']}")
        
        # Add video tags if available
        if 'tags' in snippet:
            tags.extend(snippet['tags'][:5])  # Limit to first 5 tags
        
        return self.format_tags(tags)

    @staticmethod
    def _is_short(duration: str) -> bool:
        """Check if video duration indicates a Short (<= 3 minutes / 180 seconds).
        
        Args:
            duration: ISO 8601 duration string (e.g., 'PT45S', 'PT1M30S', 'PT2M45S')
            
        Returns:
            True if video is a Short
        """
        import re
        
        # Parse ISO 8601 duration
        match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return False
        
        minutes = int(match.group(1) or 0)
        seconds = int(match.group(2) or 0)
        
        total_seconds = minutes * 60 + seconds
        return total_seconds <= 180
