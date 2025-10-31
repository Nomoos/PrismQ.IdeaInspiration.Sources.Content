"""Tests for ApplePodcasts CLI module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from src.cli import main


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Create a mock config."""
    with patch('src.cli.Config') as mock:
        config = Mock()
        config.database_path = '/tmp/test.db'
        config.database_url = 'sqlite:///test.db'
        config.apple_podcasts_max_episodes = 10
        config.apple_podcasts_max_shows = 20
        config.apple_podcasts_region = 'us'
        mock.return_value = config
        yield mock


@pytest.fixture
def mock_database():
    """Create a mock database."""
    with patch('src.cli.Database') as mock:
        db = Mock()
        db.insert_idea = Mock(return_value=True)
        db.get_all_ideas = Mock(return_value=[])
        db.count_ideas = Mock(return_value=0)
        mock.return_value = db
        yield mock


class TestCLICommands:
    """Tests for CLI commands."""
    
    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'Apple Podcasts Source' in result.output
        assert 'scrape-charts' in result.output
        assert 'scrape-category' in result.output
        assert 'scrape-show' in result.output
    
    def test_version_option(self, runner):
        """Test version option."""
        result = runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    @patch('src.cli.AppleChartsPlugin')
    def test_scrape_charts_command(self, mock_plugin, runner, mock_config, mock_database):
        """Test scrape-charts command."""
        # Mock plugin to return test data
        plugin_instance = Mock()
        plugin_instance.scrape_charts = Mock(return_value=[
            {
                'source_id': '123',
                'title': 'Test Episode',
                'description': 'Test desc',
                'tags': ['comedy'],
                'metrics': {'rating': 4.5}
            }
        ])
        mock_plugin.return_value = plugin_instance
        
        result = runner.invoke(main, ['scrape-charts', '--no-interactive', '--top', '5'])
        
        assert result.exit_code == 0
        assert 'Scraping complete!' in result.output
    
    @patch('src.cli.AppleCategoryPlugin')
    def test_scrape_category_command(self, mock_plugin, runner, mock_config, mock_database):
        """Test scrape-category command."""
        # Mock plugin to return test data
        plugin_instance = Mock()
        plugin_instance.scrape_category = Mock(return_value=[
            {
                'source_id': '456',
                'title': 'Category Episode',
                'description': 'Test desc',
                'tags': ['business'],
                'metrics': {'rating': 4.8}
            }
        ])
        mock_plugin.return_value = plugin_instance
        
        result = runner.invoke(main, [
            'scrape-category',
            '--category', 'business',
            '--no-interactive',
            '--top', '10'
        ])
        
        assert result.exit_code == 0
        assert 'Scraping complete!' in result.output
    
    @patch('src.cli.AppleShowPlugin')
    def test_scrape_show_command(self, mock_plugin, runner, mock_config, mock_database):
        """Test scrape-show command."""
        # Mock plugin to return test data
        plugin_instance = Mock()
        plugin_instance.scrape_show = Mock(return_value=[
            {
                'source_id': '789',
                'title': 'Show Episode',
                'description': 'Test desc',
                'tags': ['technology'],
                'metrics': {'rating': 4.9}
            }
        ])
        mock_plugin.return_value = plugin_instance
        
        result = runner.invoke(main, [
            'scrape-show',
            '--show', 'Test Show',
            '--no-interactive',
            '--top', '15'
        ])
        
        assert result.exit_code == 0
        assert 'Scraping complete!' in result.output
    
    def test_list_command_empty(self, runner, mock_config, mock_database):
        """Test list command with no ideas."""
        result = runner.invoke(main, ['list', '--no-interactive'])
        
        assert result.exit_code == 0
        assert 'No ideas found' in result.output
    
    def test_list_command_with_ideas(self, runner, mock_config, mock_database):
        """Test list command with ideas."""
        # Mock database to return test ideas
        mock_database.return_value.get_all_ideas.return_value = [
            {
                'source': 'apple_podcasts',
                'source_id': '123',
                'title': 'Test Episode',
                'description': 'Test description',
                'tags': 'comedy,business'
            }
        ]
        
        result = runner.invoke(main, ['list', '--no-interactive', '--limit', '10'])
        
        assert result.exit_code == 0
        assert 'Collected Ideas' in result.output
        assert 'Test Episode' in result.output
    
    def test_stats_command_empty(self, runner, mock_config, mock_database):
        """Test stats command with no ideas."""
        result = runner.invoke(main, ['stats', '--no-interactive'])
        
        assert result.exit_code == 0
        assert 'No ideas collected' in result.output
    
    def test_stats_command_with_ideas(self, runner, mock_config, mock_database):
        """Test stats command with ideas."""
        # Mock database to return test ideas
        mock_database.return_value.get_all_ideas.return_value = [
            {'source': 'apple_podcasts_charts', 'title': 'Episode 1'},
            {'source': 'apple_podcasts_charts', 'title': 'Episode 2'},
            {'source': 'apple_podcasts_show', 'title': 'Episode 3'}
        ]
        
        result = runner.invoke(main, ['stats', '--no-interactive'])
        
        assert result.exit_code == 0
        assert 'Total Ideas: 3' in result.output
        assert 'Ideas by Source:' in result.output
    
    @patch('src.cli.db_utils')
    @patch('src.cli.IdeaProcessor')
    def test_process_command(self, mock_processor, mock_db_utils, runner, mock_config):
        """Test process command."""
        # Mock unprocessed records
        mock_db_utils.get_unprocessed_records.return_value = [
            {
                'id': 1,
                'source_id': '123',
                'title': 'Test Episode',
                'score_dictionary': {}
            }
        ]
        
        # Mock processor
        mock_idea = Mock()
        mock_idea.to_dict.return_value = {'title': 'Test Episode'}
        mock_processor.process.return_value = mock_idea
        
        result = runner.invoke(main, ['process', '--no-interactive'])
        
        assert result.exit_code == 0
        assert 'Processing complete!' in result.output
    
    @patch('src.cli.Path')
    def test_clear_command(self, mock_path, runner, mock_config):
        """Test clear command."""
        # Mock file existence
        mock_db_file = Mock()
        mock_db_file.exists.return_value = True
        mock_path.return_value = mock_db_file
        
        result = runner.invoke(main, ['clear', '--no-interactive'], input='y\n')
        
        assert result.exit_code == 0
        assert 'Database cleared' in result.output


class TestCLIOptions:
    """Tests for CLI options and parameters."""
    
    def test_scrape_charts_genre_option(self, runner, mock_config, mock_database):
        """Test --genre option for scrape-charts."""
        with patch('src.cli.AppleChartsPlugin') as mock_plugin:
            plugin_instance = Mock()
            plugin_instance.scrape_charts = Mock(return_value=[])
            mock_plugin.return_value = plugin_instance
            
            result = runner.invoke(main, [
                'scrape-charts',
                '--genre', 'technology',
                '--no-interactive'
            ])
            
            assert result.exit_code == 0
    
    def test_list_limit_option(self, runner, mock_config, mock_database):
        """Test --limit option for list command."""
        result = runner.invoke(main, [
            'list',
            '--limit', '50',
            '--no-interactive'
        ])
        
        assert result.exit_code == 0
    
    def test_list_source_filter(self, runner, mock_config, mock_database):
        """Test --source filter for list command."""
        # Mock database with multiple sources
        mock_database.return_value.get_all_ideas.return_value = [
            {'source': 'apple_podcasts_charts', 'title': 'Episode 1', 'source_id': '1', 'tags': None, 'description': ''},
            {'source': 'apple_podcasts_show', 'title': 'Episode 2', 'source_id': '2', 'tags': None, 'description': ''}
        ]
        
        result = runner.invoke(main, [
            'list',
            '--source', 'apple_podcasts_charts',
            '--no-interactive'
        ])
        
        # Should complete successfully
        assert result.exit_code == 0 or 'Episode' in result.output


class TestCLIErrorHandling:
    """Tests for CLI error handling."""
    
    def test_scrape_category_missing_category(self, runner):
        """Test scrape-category without category parameter."""
        result = runner.invoke(main, ['scrape-category', '--no-interactive'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_scrape_show_missing_show(self, runner):
        """Test scrape-show without show parameter."""
        result = runner.invoke(main, ['scrape-show', '--no-interactive'])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    @patch('src.cli.AppleChartsPlugin')
    def test_scrape_charts_api_error(self, mock_plugin, runner, mock_config, mock_database):
        """Test handling API errors during scraping."""
        # Mock plugin to raise an exception
        plugin_instance = Mock()
        plugin_instance.scrape_charts = Mock(side_effect=Exception("API Error"))
        mock_plugin.return_value = plugin_instance
        
        result = runner.invoke(main, ['scrape-charts', '--no-interactive'])
        
        # Should handle error gracefully
        assert 'Error' in result.output or result.exit_code != 0
