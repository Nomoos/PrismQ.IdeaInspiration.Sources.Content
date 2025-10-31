"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Shorts.TwitchClips."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.twitch_trending_plugin import TwitchTrendingPlugin
from .plugins.twitch_game_plugin import TwitchGamePlugin
from .plugins.twitch_streamer_plugin import TwitchStreamerPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Twitch Clips Source - Gather idea inspirations from Twitch clips."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--top-n', '-n', type=int, 
              help='Number of clips to scrape (overrides config)')
def scrape_trending(env_file, no_interactive, top_n):
    """Scrape trending clips from Twitch.
    
    This command scrapes the most viewed clips from the last 24 hours.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Twitch trending plugin
        try:
            twitch_plugin = TwitchTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Twitch
        total_scraped = 0
        total_saved = 0
        
        click.echo("Scraping trending Twitch clips...")
        
        try:
            ideas = twitch_plugin.scrape(top_n=top_n)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} clips from Twitch")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_twitch(idea['raw_data'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='twitch_clips',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.views_per_day or universal_metrics.view_count or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Twitch clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total clips found: {total_scraped}")
        click.echo(f"Total clips saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--game', '-g', type=str, 
              help='Game name to search (overrides config)')
@click.option('--top-n', '-n', type=int, 
              help='Number of clips to scrape (overrides config)')
def scrape_game(env_file, no_interactive, game, top_n):
    """Scrape clips from a specific game/category.
    
    This command scrapes clips filtered by game or category.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Twitch game plugin
        try:
            twitch_plugin = TwitchGamePlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Twitch
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping Twitch clips for game: {game or 'configured game'}...")
        
        try:
            ideas = twitch_plugin.scrape(game_name=game, top_n=top_n)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} clips from Twitch")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_twitch(idea['raw_data'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='twitch_clips',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.views_per_day or universal_metrics.view_count or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Twitch clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total clips found: {total_scraped}")
        click.echo(f"Total clips saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--streamer', '-s', type=str, 
              help='Streamer username to search (overrides config)')
@click.option('--top-n', '-n', type=int, 
              help='Number of clips to scrape (overrides config)')
def scrape_streamer(env_file, no_interactive, streamer, top_n):
    """Scrape clips from a specific streamer/channel.
    
    This command scrapes clips from a specific Twitch streamer.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Twitch streamer plugin
        try:
            twitch_plugin = TwitchStreamerPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Twitch
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping Twitch clips from streamer: {streamer or 'configured streamer'}...")
        
        try:
            ideas = twitch_plugin.scrape(streamer_name=streamer, top_n=top_n)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} clips from Twitch")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_twitch(idea['raw_data'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='twitch_clips',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.views_per_day or universal_metrics.view_count or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Twitch clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total clips found: {total_scraped}")
        click.echo(f"Total clips saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--source', type=str, 
              help='Filter by source')
@click.option('--limit', '-l', type=int, default=10,
              help='Number of ideas to list')
def list_ideas(env_file, source, limit):
    """List ideas from the database.
    
    This command lists stored ideas from the database.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=False)
        
        # Get ideas from database
        ideas = db_utils.get_all_ideas(config.database_url, source=source)
        
        if not ideas:
            click.echo("No ideas found in database")
            return
        
        # Limit results
        ideas = ideas[:limit]
        
        click.echo(f"\nFound {len(ideas)} ideas:\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. [{idea['source']}] {idea['title']}")
            click.echo(f"   ID: {idea['source_id']}")
            click.echo(f"   Score: {idea.get('score', 'N/A')}")
            click.echo(f"   Created: {idea['created_at']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
