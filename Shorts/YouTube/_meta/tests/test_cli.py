"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json
from src import cli


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_env():
    """Create a temporary .env file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("DATABASE_PATH=test.db\n")
        f.write("DATABASE_URL=sqlite:///test.db\n")
        env_path = f.name
    yield env_path
    Path(env_path).unlink(missing_ok=True)


class TestMainCommand:
    """Test main CLI command."""
    
    def test_main_command(self, runner):
        """Test main command shows help."""
        result = runner.invoke(cli.main, ['--help'])
        assert result.exit_code == 0
        assert 'PrismQ YouTube Shorts Source' in result.output
    
    def test_main_version(self, runner):
        """Test version option."""
        result = runner.invoke(cli.main, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output


class TestScrapeCommand:
    """Test scrape command."""
    
    def test_scrape_help(self, runner):
        """Test scrape command help."""
        result = runner.invoke(cli.scrape, ['--help'])
        assert result.exit_code == 0
        assert 'Scrape ideas from YouTube Shorts' in result.output
    
    def test_scrape_shows_warning(self, runner):
        """Test that scrape command shows deprecation warning."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubePlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape.return_value = []
                    
                    result = runner.invoke(cli.scrape, ['--no-interactive'])
                    
                    assert 'WARNING' in result.output
                    assert 'legacy' in result.output.lower()
    
    def test_scrape_with_env_file(self, runner, temp_env):
        """Test scrape command with env file."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubePlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape.return_value = []
                    
                    result = runner.invoke(cli.scrape, [
                        '--env-file', temp_env,
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
    
    def test_scrape_handles_plugin_error(self, runner):
        """Test scrape handles plugin initialization error."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubePlugin', side_effect=ValueError("API key missing")):
                    mock_config.return_value.database_path = 'test.db'
                    
                    result = runner.invoke(cli.scrape, ['--no-interactive'])
                    
                    assert result.exit_code == 1
                    assert 'Error' in result.output


class TestScrapeChannelCommand:
    """Test scrape-channel command."""
    
    def test_scrape_channel_help(self, runner):
        """Test scrape-channel command help."""
        result = runner.invoke(cli.scrape_channel, ['--help'])
        assert result.exit_code == 0
        assert 'Scrape ideas from a specific YouTube channel' in result.output
    
    def test_scrape_channel_with_url(self, runner):
        """Test scrape-channel with channel URL."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeChannelPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_config.return_value.youtube_channel_max_shorts = 10
                    mock_plugin.return_value.scrape.return_value = []
                    
                    result = runner.invoke(cli.scrape_channel, [
                        '--channel', '@testchannel',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    assert '@testchannel' in result.output
    
    def test_scrape_channel_with_top_n(self, runner):
        """Test scrape-channel with custom top_n."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeChannelPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape.return_value = []
                    
                    result = runner.invoke(cli.scrape_channel, [
                        '--channel', '@testchannel',
                        '--top', '20',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    assert '20' in result.output
    
    def test_scrape_channel_without_channel_specified(self, runner):
        """Test scrape-channel without channel specified."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_config.return_value.youtube_channel_url = None
                
                result = runner.invoke(cli.scrape_channel, ['--no-interactive'])
                
                assert result.exit_code == 1
                assert 'No channel specified' in result.output
    
    def test_scrape_channel_handles_ytdlp_error(self, runner):
        """Test scrape-channel handles yt-dlp not installed."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeChannelPlugin', side_effect=ValueError("yt-dlp is not installed")):
                    mock_config.return_value.database_path = 'test.db'
                    
                    result = runner.invoke(cli.scrape_channel, [
                        '--channel', '@test',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 1
                    assert 'yt-dlp' in result.output


class TestScrapeTrendingCommand:
    """Test scrape-trending command."""
    
    def test_scrape_trending_help(self, runner):
        """Test scrape-trending command help."""
        result = runner.invoke(cli.scrape_trending, ['--help'])
        assert result.exit_code == 0
        assert 'Scrape ideas from YouTube trending Shorts' in result.output
    
    def test_scrape_trending_basic(self, runner):
        """Test basic scrape-trending execution."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeTrendingPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape_trending.return_value = []
                    
                    result = runner.invoke(cli.scrape_trending, ['--no-interactive'])
                    
                    assert result.exit_code == 0
                    assert 'trending' in result.output.lower()
    
    def test_scrape_trending_with_top_n(self, runner):
        """Test scrape-trending with custom top_n."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeTrendingPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape_trending.return_value = []
                    
                    result = runner.invoke(cli.scrape_trending, [
                        '--top', '15',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    assert '15' in result.output


class TestScrapeKeywordCommand:
    """Test scrape-keyword command."""
    
    def test_scrape_keyword_help(self, runner):
        """Test scrape-keyword command help."""
        result = runner.invoke(cli.scrape_keyword, ['--help'])
        assert result.exit_code == 0
        assert 'Scrape ideas from YouTube by keyword search' in result.output
    
    def test_scrape_keyword_basic(self, runner):
        """Test basic scrape-keyword execution."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeTrendingPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape_by_keyword.return_value = []
                    
                    result = runner.invoke(cli.scrape_keyword, [
                        '--keyword', 'test keyword',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    assert 'test keyword' in result.output
    
    def test_scrape_keyword_requires_keyword(self, runner):
        """Test that scrape-keyword requires keyword parameter."""
        result = runner.invoke(cli.scrape_keyword, ['--no-interactive'])
        
        assert result.exit_code != 0
        # Click will show missing option error
    
    def test_scrape_keyword_with_top_n(self, runner):
        """Test scrape-keyword with custom top_n."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeTrendingPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_plugin.return_value.scrape_by_keyword.return_value = []
                    
                    result = runner.invoke(cli.scrape_keyword, [
                        '--keyword', 'test',
                        '--top', '25',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    assert '25' in result.output


class TestListCommand:
    """Test list command."""
    
    def test_list_help(self, runner):
        """Test list command help."""
        result = runner.invoke(cli.list, ['--help'])
        assert result.exit_code == 0
        assert 'List collected ideas' in result.output
    
    def test_list_empty_database(self, runner):
        """Test list with empty database."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = []
                
                result = runner.invoke(cli.list, ['--no-interactive'])
                
                assert result.exit_code == 0
                assert 'No ideas found' in result.output
    
    def test_list_with_ideas(self, runner):
        """Test list with ideas in database."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = [
                    {
                        'source': 'youtube',
                        'source_id': '123',
                        'title': 'Test Video',
                        'description': 'Test description',
                        'tags': 'tag1,tag2'
                    }
                ]
                
                result = runner.invoke(cli.list, ['--no-interactive'])
                
                assert result.exit_code == 0
                assert 'Test Video' in result.output
                assert 'YOUTUBE' in result.output
    
    def test_list_with_limit(self, runner):
        """Test list with custom limit."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = []
                
                result = runner.invoke(cli.list, ['--limit', '10', '--no-interactive'])
                
                assert result.exit_code == 0
    
    def test_list_with_source_filter(self, runner):
        """Test list with source filter."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = [
                    {'source': 'youtube', 'source_id': '1', 'title': 'Video 1', 'description': '', 'tags': ''},
                    {'source': 'youtube_channel', 'source_id': '2', 'title': 'Video 2', 'description': '', 'tags': ''}
                ]
                
                result = runner.invoke(cli.list, [
                    '--source', 'youtube',
                    '--no-interactive'
                ])
                
                assert result.exit_code == 0


class TestStatsCommand:
    """Test stats command."""
    
    def test_stats_help(self, runner):
        """Test stats command help."""
        result = runner.invoke(cli.stats, ['--help'])
        assert result.exit_code == 0
        assert 'Show statistics' in result.output
    
    def test_stats_empty_database(self, runner):
        """Test stats with empty database."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = []
                
                result = runner.invoke(cli.stats, ['--no-interactive'])
                
                assert result.exit_code == 0
                assert 'No ideas collected' in result.output
    
    def test_stats_with_ideas(self, runner):
        """Test stats with ideas in database."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                mock_config.return_value.database_path = 'test.db'
                mock_db.return_value.get_all_ideas.return_value = [
                    {'source': 'youtube', 'source_id': '1', 'title': 'Video 1'},
                    {'source': 'youtube', 'source_id': '2', 'title': 'Video 2'},
                    {'source': 'youtube_channel', 'source_id': '3', 'title': 'Video 3'}
                ]
                
                result = runner.invoke(cli.stats, ['--no-interactive'])
                
                assert result.exit_code == 0
                assert 'Total Ideas: 3' in result.output
                assert 'Ideas by Source:' in result.output


class TestProcessCommand:
    """Test process command."""
    
    def test_process_help(self, runner):
        """Test process command help."""
        result = runner.invoke(cli.process, ['--help'])
        assert result.exit_code == 0
        assert 'Process unprocessed YouTube Shorts records' in result.output
    
    def test_process_no_unprocessed_records(self, runner):
        """Test process with no unprocessed records."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.core.db_utils.init_database'):
                with patch('src.core.db_utils.get_unprocessed_records', return_value=[]):
                    mock_config.return_value.database_url = 'sqlite:///test.db'
                    
                    result = runner.invoke(cli.process, ['--no-interactive'])
                    
                    assert result.exit_code == 0
                    assert 'No unprocessed records found' in result.output
    
    def test_process_with_records(self, runner):
        """Test process with unprocessed records."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.core.db_utils.init_database'):
                with patch('src.core.db_utils.get_unprocessed_records') as mock_get:
                    with patch('src.core.db_utils.mark_as_processed'):
                        with patch('src.cli.IdeaProcessor.process') as mock_process:
                            mock_config.return_value.database_url = 'sqlite:///test.db'
                            mock_get.return_value = [
                                {'id': 1, 'title': 'Test Video', 'source_id': '123'}
                            ]
                            
                            mock_idea = Mock()
                            mock_idea.to_dict.return_value = {'title': 'Test Video'}
                            mock_process.return_value = mock_idea
                            
                            result = runner.invoke(cli.process, ['--no-interactive'])
                            
                            assert result.exit_code == 0
                            assert 'Processed: Test Video' in result.output
    
    def test_process_with_limit(self, runner):
        """Test process with limit parameter."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.core.db_utils.init_database'):
                with patch('src.core.db_utils.get_unprocessed_records') as mock_get:
                    mock_config.return_value.database_url = 'sqlite:///test.db'
                    mock_get.return_value = []
                    
                    result = runner.invoke(cli.process, [
                        '--limit', '5',
                        '--no-interactive'
                    ])
                    
                    assert result.exit_code == 0
                    mock_get.assert_called_once_with('sqlite:///test.db', limit=5)
    
    def test_process_with_output_file(self, runner):
        """Test process with output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / 'output.json'
            
            with patch('src.cli.Config') as mock_config:
                with patch('src.core.db_utils.init_database'):
                    with patch('src.core.db_utils.get_unprocessed_records') as mock_get:
                        with patch('src.core.db_utils.mark_as_processed'):
                            with patch('src.cli.IdeaProcessor.process') as mock_process:
                                mock_config.return_value.database_url = 'sqlite:///test.db'
                                mock_get.return_value = [
                                    {'id': 1, 'title': 'Test', 'source_id': '123'}
                                ]
                                
                                mock_idea = Mock()
                                mock_idea.to_dict.return_value = {'title': 'Test'}
                                mock_process.return_value = mock_idea
                                
                                result = runner.invoke(cli.process, [
                                    '--output', str(output_file),
                                    '--no-interactive'
                                ])
                                
                                assert result.exit_code == 0
                                assert output_file.exists()


class TestClearCommand:
    """Test clear command."""
    
    def test_clear_help(self, runner):
        """Test clear command help."""
        result = runner.invoke(cli.clear, ['--help'])
        assert result.exit_code == 0
        assert 'Clear all ideas from the database' in result.output
    
    def test_clear_database(self, runner, temp_db):
        """Test clearing database."""
        # Create a test database file
        Path(temp_db).touch()
        
        with patch('src.cli.Config') as mock_config:
            mock_config.return_value.database_path = temp_db
            
            # Automatically confirm
            result = runner.invoke(cli.clear, [
                '--no-interactive',
                '--yes'  # Auto-confirm
            ], input='y\n')
            
            assert result.exit_code == 0
    
    def test_clear_nonexistent_database(self, runner):
        """Test clearing nonexistent database."""
        with patch('src.cli.Config') as mock_config:
            mock_config.return_value.database_path = '/nonexistent/path.db'
            
            result = runner.invoke(cli.clear, [
                '--no-interactive',
                '--yes'
            ], input='y\n')
            
            assert result.exit_code == 0
            assert 'does not exist' in result.output


class TestCommandIntegration:
    """Test command integration scenarios."""
    
    def test_scrape_and_list_workflow(self, runner):
        """Test workflow of scraping and listing ideas."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database') as mock_db:
                with patch('src.cli.YouTubeChannelPlugin') as mock_plugin:
                    mock_config.return_value.database_path = 'test.db'
                    mock_config.return_value.youtube_channel_max_shorts = 10
                    
                    # Mock scraping
                    mock_plugin.return_value.scrape.return_value = [
                        {
                            'source_id': '123',
                            'title': 'Test Video',
                            'description': 'Test',
                            'tags': 'tag1',
                            'metrics': {}
                        }
                    ]
                    
                    # Scrape
                    result1 = runner.invoke(cli.scrape_channel, [
                        '--channel', '@test',
                        '--no-interactive'
                    ])
                    assert result1.exit_code == 0
                    
                    # List
                    mock_db.return_value.get_all_ideas.return_value = [
                        {
                            'source': 'youtube_channel',
                            'source_id': '123',
                            'title': 'Test Video',
                            'description': 'Test',
                            'tags': 'tag1'
                        }
                    ]
                    
                    result2 = runner.invoke(cli.list, ['--no-interactive'])
                    assert result2.exit_code == 0


class TestErrorHandling:
    """Test error handling in CLI commands."""
    
    def test_config_error_handling(self, runner):
        """Test handling of config errors."""
        with patch('src.cli.Config', side_effect=Exception("Config error")):
            result = runner.invoke(cli.scrape, ['--no-interactive'])
            
            assert result.exit_code == 1
            assert 'Error' in result.output
    
    def test_database_error_handling(self, runner):
        """Test handling of database errors."""
        with patch('src.cli.Config') as mock_config:
            with patch('src.cli.Database', side_effect=Exception("Database error")):
                mock_config.return_value.database_path = 'test.db'
                
                result = runner.invoke(cli.list, ['--no-interactive'])
                
                assert result.exit_code == 1
                assert 'Error' in result.output
