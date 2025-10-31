"""Tests for YouTube trending plugin."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src import YouTubeTrendingPlugin


class TestYouTubeTrendingPlugin:
    """Test YouTube trending plugin functionality."""
    
    def test_initialization(self):
        """Test plugin initialization."""
        config = Mock()
        
        # Mock yt-dlp check to return True
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            assert plugin.config == config
            assert plugin.get_source_name() == "youtube_trending"
    
    def test_initialization_without_ytdlp(self):
        """Test plugin initialization fails without yt-dlp."""
        config = Mock()
        
        # Mock yt-dlp check to return False
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=False):
            with pytest.raises(ValueError, match="yt-dlp is not installed"):
                YouTubeTrendingPlugin(config)
    
    def test_shorts_max_duration(self):
        """Test that SHORTS_MAX_DURATION is set correctly."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            assert plugin.SHORTS_MAX_DURATION == 180
    
    def test_shorts_fetch_multiplier(self):
        """Test that SHORTS_FETCH_MULTIPLIER is set correctly."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            assert plugin.SHORTS_FETCH_MULTIPLIER == 3


class TestCheckYtdlp:
    """Test yt-dlp availability checking."""
    
    def test_check_ytdlp_available(self):
        """Test checking when yt-dlp is available."""
        config = Mock()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            plugin = YouTubeTrendingPlugin(config)
            assert plugin._check_ytdlp() is True
    
    def test_check_ytdlp_not_found(self):
        """Test checking when yt-dlp is not installed."""
        config = Mock()
        
        with patch('subprocess.run', side_effect=FileNotFoundError):
            with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=False):
                with pytest.raises(ValueError):
                    YouTubeTrendingPlugin(config)
    
    def test_check_ytdlp_timeout(self):
        """Test checking when yt-dlp times out."""
        config = Mock()
        
        with patch('subprocess.run', side_effect=Exception("Timeout")):
            with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=False):
                with pytest.raises(ValueError):
                    YouTubeTrendingPlugin(config)


class TestParseSrtToText:
    """Test SRT subtitle parsing."""
    
    def test_parse_simple_srt(self):
        """Test parsing simple SRT content."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello world

2
00:00:02,000 --> 00:00:04,000
This is a test
"""
            result = plugin._parse_srt_to_text(srt_content)
            assert "Hello world" in result
            assert "This is a test" in result
            assert "-->" not in result
            assert "00:00:00" not in result
    
    def test_parse_empty_srt(self):
        """Test parsing empty SRT content."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            result = plugin._parse_srt_to_text("")
            assert result == ""
    
    def test_parse_srt_filters_numbers(self):
        """Test that subtitle sequence numbers are filtered out."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            srt_content = """1
00:00:00,000 --> 00:00:02,000
Text line
"""
            result = plugin._parse_srt_to_text(srt_content)
            # Should not contain standalone "1"
            assert result.strip() == "Text line"
    
    def test_parse_srt_filters_timestamps(self):
        """Test that timestamps are filtered out."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            srt_content = """1
00:00:00,000 --> 00:00:02,000
Subtitle text
"""
            result = plugin._parse_srt_to_text(srt_content)
            assert "-->" not in result
            assert "00:00:00" not in result


class TestFormatDurationIso8601:
    """Test ISO 8601 duration formatting."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero duration."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            assert plugin._format_duration_iso8601(0) == "PT0S"
    
    def test_format_seconds_only(self):
        """Test formatting duration with only seconds."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            assert plugin._format_duration_iso8601(45) == "PT45S"
    
    def test_format_minutes_and_seconds(self):
        """Test formatting duration with minutes and seconds."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            assert plugin._format_duration_iso8601(90) == "PT1M30S"
            assert plugin._format_duration_iso8601(125) == "PT2M5S"
    
    def test_format_exact_minutes(self):
        """Test formatting duration that's exact minutes."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            assert plugin._format_duration_iso8601(60) == "PT1M0S"
            assert plugin._format_duration_iso8601(120) == "PT2M0S"
    
    def test_format_negative_duration(self):
        """Test formatting negative duration."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            assert plugin._format_duration_iso8601(-10) == "PT0S"


class TestExtractTags:
    """Test tag extraction from metadata."""
    
    def test_extract_basic_tags(self):
        """Test extracting basic tags."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'channel': 'TestChannel',
                'categories': ['Entertainment'],
                'tags': ['tag1', 'tag2']
            }
            
            result = plugin._extract_tags(metadata)
            assert 'youtube_shorts' in result
            assert 'trending' in result
            assert 'TestChannel' in result
    
    def test_extract_tags_with_uploader(self):
        """Test extracting tags when uploader is used instead of channel."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'uploader': 'UploaderName',
                'tags': []
            }
            
            result = plugin._extract_tags(metadata)
            assert 'UploaderName' in result
    
    def test_extract_tags_with_categories(self):
        """Test extracting tags with categories."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'categories': ['Gaming', 'Technology'],
                'tags': []
            }
            
            result = plugin._extract_tags(metadata)
            assert 'category_Gaming' in result
            # Only first 2 categories
            assert 'category_Technology' in result
    
    def test_extract_tags_limits_video_tags(self):
        """Test that video tags are limited to 5."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7']
            }
            
            result = plugin._extract_tags(metadata)
            # Should have base tags + max 5 video tags
            tag_list = result.split(',')
            # youtube_shorts, trending + 5 video tags = 7
            assert len([t for t in tag_list if t.startswith('tag')]) <= 5


class TestMetadataToIdea:
    """Test converting metadata to idea format."""
    
    def test_metadata_to_idea_basic(self):
        """Test basic metadata to idea conversion."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'id': 'test123',
                'title': 'Test Video',
                'description': 'Test description',
                'view_count': 1000,
                'like_count': 100,
                'comment_count': 50,
                'duration': 60,
                'width': 1080,
                'height': 1920,
                'channel': 'TestChannel',
                'upload_date': '20240101'
            }
            
            idea = plugin._metadata_to_idea(metadata)
            
            assert idea is not None
            assert idea['source_id'] == 'test123'
            assert idea['title'] == 'Test Video'
            assert idea['description'] == 'Test description'
            assert 'metrics' in idea
            assert 'tags' in idea
    
    def test_metadata_to_idea_engagement_rate(self):
        """Test engagement rate calculation."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'id': 'test123',
                'title': 'Test Video',
                'view_count': 1000,
                'like_count': 100,
                'comment_count': 50,
                'duration': 60
            }
            
            idea = plugin._metadata_to_idea(metadata)
            
            # Engagement rate = (likes + comments) / views * 100
            # (100 + 50) / 1000 * 100 = 15.0
            enhanced_metrics = idea['metrics']['enhanced_metrics']
            assert enhanced_metrics['engagement_rate'] == 15.0
    
    def test_metadata_to_idea_zero_views(self):
        """Test handling zero views."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'id': 'test123',
                'title': 'Test Video',
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'duration': 60
            }
            
            idea = plugin._metadata_to_idea(metadata)
            
            enhanced_metrics = idea['metrics']['enhanced_metrics']
            assert enhanced_metrics['engagement_rate'] == 0.0
    
    def test_metadata_to_idea_with_subtitle(self):
        """Test metadata with subtitle text."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'id': 'test123',
                'title': 'Test Video',
                'view_count': 100,
                'duration': 60,
                'subtitle_text': 'This is subtitle text'
            }
            
            idea = plugin._metadata_to_idea(metadata)
            
            enhanced_metrics = idea['metrics']['enhanced_metrics']
            assert enhanced_metrics['subtitle_text'] == 'This is subtitle text'
            assert enhanced_metrics['subtitles_available'] is True
    
    def test_metadata_to_idea_without_subtitle(self):
        """Test metadata without subtitle text."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            metadata = {
                'id': 'test123',
                'title': 'Test Video',
                'view_count': 100,
                'duration': 60
            }
            
            idea = plugin._metadata_to_idea(metadata)
            
            enhanced_metrics = idea['metrics']['enhanced_metrics']
            assert enhanced_metrics['subtitle_text'] is None
            assert enhanced_metrics['subtitles_available'] is False


class TestScrapeTrending:
    """Test scrape_trending method."""
    
    def test_scrape_trending_basic(self):
        """Test basic trending scraping."""
        config = Mock()
        config.youtube_trending_max_shorts = 10
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            # Mock the internal methods
            with patch.object(plugin, '_get_trending_videos', return_value=['vid1', 'vid2']):
                with patch.object(plugin, '_extract_video_metadata', return_value={
                    'id': 'vid1',
                    'title': 'Test',
                    'view_count': 100,
                    'duration': 60
                }):
                    with patch.object(plugin, '_metadata_to_idea', return_value={
                        'source_id': 'vid1',
                        'title': 'Test',
                        'metrics': {}
                    }):
                        ideas = plugin.scrape_trending(top_n=2)
                        
                        assert len(ideas) == 2
    
    def test_scrape_trending_with_config_default(self):
        """Test trending scraping uses config default."""
        config = Mock()
        config.youtube_trending_max_shorts = 5
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, '_get_trending_videos', return_value=[]) as mock_get:
                plugin.scrape_trending()
                
                # Should use config default
                mock_get.assert_called_once()
    
    def test_scrape_trending_no_videos_found(self):
        """Test trending scraping when no videos found."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, '_get_trending_videos', return_value=[]):
                ideas = plugin.scrape_trending(top_n=10)
                
                assert ideas == []


class TestScrapeByKeyword:
    """Test scrape_by_keyword method."""
    
    def test_scrape_by_keyword_basic(self):
        """Test basic keyword scraping."""
        config = Mock()
        config.youtube_keyword_max_shorts = 10
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, '_search_by_keyword', return_value=['vid1']):
                with patch.object(plugin, '_extract_video_metadata', return_value={
                    'id': 'vid1',
                    'title': 'Test',
                    'view_count': 100,
                    'duration': 60
                }):
                    with patch.object(plugin, '_metadata_to_idea', return_value={
                        'source_id': 'vid1',
                        'title': 'Test',
                        'metrics': {}
                    }):
                        ideas = plugin.scrape_by_keyword('test keyword', top_n=1)
                        
                        assert len(ideas) == 1
    
    def test_scrape_by_keyword_no_results(self):
        """Test keyword scraping with no results."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, '_search_by_keyword', return_value=[]):
                ideas = plugin.scrape_by_keyword('nonexistent', top_n=10)
                
                assert ideas == []


class TestScrapeMethod:
    """Test main scrape method."""
    
    def test_scrape_defaults_to_trending(self):
        """Test that scrape defaults to trending."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, 'scrape_trending', return_value=[]) as mock_trending:
                plugin.scrape()
                
                mock_trending.assert_called_once()
    
    def test_scrape_with_trending_flag(self):
        """Test scrape with trending flag."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, 'scrape_trending', return_value=[]) as mock_trending:
                plugin.scrape(trending=True)
                
                mock_trending.assert_called_once()
    
    def test_scrape_with_keyword(self):
        """Test scrape with keyword."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            with patch.object(plugin, 'scrape_by_keyword', return_value=[]) as mock_keyword:
                plugin.scrape(keyword='test')
                
                mock_keyword.assert_called_once_with('test', top_n=None)


class TestExtractVideoMetadata:
    """Test _extract_video_metadata method."""
    
    def test_filters_long_videos(self):
        """Test that videos longer than 180s are filtered."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            # Mock a long video (> 180 seconds)
            with patch('subprocess.run'):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('builtins.open', create=True) as mock_open:
                        import json
                        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                            'id': 'long_vid',
                            'duration': 300  # 5 minutes - too long
                        })
                        
                        with patch('pathlib.Path.unlink'):
                            result = plugin._extract_video_metadata('long_vid')
                            
                            assert result is None
    
    def test_accepts_short_videos(self):
        """Test that videos under 180s are accepted."""
        config = Mock()
        
        with patch.object(YouTubeTrendingPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeTrendingPlugin(config)
            
            # Mock a short video
            with patch('subprocess.run'):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('pathlib.Path.glob', return_value=[]):
                        with patch('builtins.open', create=True) as mock_open:
                            import json
                            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                                'id': 'short_vid',
                                'duration': 60,  # 1 minute - acceptable
                                'width': 1080,
                                'height': 1920
                            })
                            
                            with patch('pathlib.Path.unlink'):
                                result = plugin._extract_video_metadata('short_vid')
                                
                                assert result is not None
                                assert result['duration'] == 60
