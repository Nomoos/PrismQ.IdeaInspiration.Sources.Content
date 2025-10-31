"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Shorts.InstagramReels."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.instagram_explore import InstagramExplorePlugin
from .plugins.instagram_hashtag import InstagramHashtagPlugin
from .plugins.instagram_creator import InstagramCreatorPlugin
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Instagram Reels Source - Gather idea inspirations from Instagram Reels."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--max-reels', '-n', type=int, default=None,
              help='Maximum number of reels to scrape')
def scrape_explore(env_file, no_interactive, max_reels):
    """Scrape reels from Instagram explore/trending page."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        try:
            plugin = InstagramExplorePlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape reels
        click.echo("Scraping Instagram explore reels...")
        
        try:
            reels = plugin.scrape(max_reels=max_reels)
            click.echo(f"Found {len(reels)} reels from explore page")
            
            # Process and save each reel
            total_saved = 0
            for reel in reels:
                # Convert Instagram metrics to universal metrics
                universal_metrics = UniversalMetrics.from_instagram(reel)
                
                # Save to database
                success = db.insert_idea(
                    source=plugin.get_source_name(),
                    source_id=reel['source_id'],
                    title=reel['title'],
                    description=reel['description'],
                    tags=plugin.format_tags(reel.get('tags', [])),
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
            click.echo(f"Saved {total_saved} new reels to database")
            click.echo(f"Skipped {len(reels) - total_saved} duplicates")
            
        except Exception as e:
            click.echo(f"Error during scraping: {e}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.option('--hashtag', '-t', type=str, required=True,
              help='Hashtag to search (without #)')
@click.option('--max-reels', '-n', type=int, default=None,
              help='Maximum number of reels to scrape')
def scrape_hashtag(env_file, no_interactive, hashtag, max_reels):
    """Scrape reels by hashtag."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            plugin = InstagramHashtagPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        click.echo(f"Scraping Instagram reels for hashtag: #{hashtag}")
        
        try:
            reels = plugin.scrape(hashtag=hashtag, max_reels=max_reels)
            click.echo(f"Found {len(reels)} reels for #{hashtag}")
            
            total_saved = 0
            for reel in reels:
                universal_metrics = UniversalMetrics.from_instagram(reel)
                
                success = db.insert_idea(
                    source=plugin.get_source_name(),
                    source_id=reel['source_id'],
                    title=reel['title'],
                    description=reel['description'],
                    tags=plugin.format_tags(reel.get('tags', [])),
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
            click.echo(f"Saved {total_saved} new reels to database")
            click.echo(f"Skipped {len(reels) - total_saved} duplicates")
            
        except Exception as e:
            click.echo(f"Error during scraping: {e}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.option('--username', '-u', type=str, required=True,
              help='Instagram username')
@click.option('--max-reels', '-n', type=int, default=None,
              help='Maximum number of reels to scrape')
def scrape_creator(env_file, no_interactive, username, max_reels):
    """Scrape reels from a creator's profile."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            plugin = InstagramCreatorPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        click.echo(f"Scraping Instagram reels from @{username}")
        
        try:
            reels = plugin.scrape(username=username, max_reels=max_reels)
            click.echo(f"Found {len(reels)} reels from @{username}")
            
            total_saved = 0
            for reel in reels:
                universal_metrics = UniversalMetrics.from_instagram(reel)
                
                success = db.insert_idea(
                    source=plugin.get_source_name(),
                    source_id=reel['source_id'],
                    title=reel['title'],
                    description=reel['description'],
                    tags=plugin.format_tags(reel.get('tags', [])),
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
            click.echo(f"Saved {total_saved} new reels to database")
            click.echo(f"Skipped {len(reels) - total_saved} duplicates")
            
        except Exception as e:
            click.echo(f"Error during scraping: {e}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def process(env_file, no_interactive):
    """Process unprocessed reels to IdeaInspiration format."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get unprocessed records
        records = db.get_unprocessed_records()
        
        if not records:
            click.echo("No unprocessed reels found")
            return
        
        click.echo(f"Processing {len(records)} unprocessed reels...")
        
        # Process records
        ideas = IdeaProcessor.process_records(records)
        
        # Mark as processed
        for record in records:
            db.mark_as_processed(record['id'])
        
        click.echo(f"Processed {len(ideas)} reels")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Display database statistics."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        stats = db.get_stats()
        
        click.echo("Database Statistics")
        click.echo("=" * 40)
        click.echo(f"Total reels: {stats['total']}")
        click.echo(f"Processed: {stats['processed']}")
        click.echo(f"Unprocessed: {stats['unprocessed']}")
        click.echo("\nReels by source:")
        for source, count in stats['by_source'].items():
            click.echo(f"  {source}: {count}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.option('--output', '-o', type=click.Path(), default='instagram_reels.json',
              help='Output JSON file')
@click.option('--limit', '-l', type=int, default=100,
              help='Maximum number of reels to export')
def export(env_file, no_interactive, output, limit):
    """Export reels to JSON file."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get ideas
        records = db.get_all_ideas(limit=limit, order_by='score')
        
        if not records:
            click.echo("No reels found to export")
            return
        
        # Process to IdeaInspiration format
        ideas = IdeaProcessor.process_records(records)
        
        # Export to JSON
        json_output = IdeaProcessor.to_json(ideas)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        
        click.echo(f"Exported {len(ideas)} reels to {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
