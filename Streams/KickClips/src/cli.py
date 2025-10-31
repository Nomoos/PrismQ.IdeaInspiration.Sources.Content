"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Streams.KickClips."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins import KickTrendingPlugin, KickCategoryPlugin, KickStreamerPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Kick Clips Source - Gather idea inspirations from Kick clips."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--max-clips', '-n', type=int, default=None,
              help='Maximum number of clips to scrape')
def scrape_trending(env_file, no_interactive, max_clips):
    """Scrape trending clips from Kick.
    
    This command scrapes the most popular and trending clips currently on Kick.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = KickTrendingPlugin(config)
        
        # Scrape clips
        total_scraped = 0
        total_saved = 0
        
        click.echo("Scraping trending Kick clips...")
        
        try:
            ideas = plugin.scrape(max_clips=max_clips)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from Kick trending")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_kick(idea['metrics'])
                
                # Add universal metrics to idea
                idea['universal_metrics'] = universal_metrics.to_dict()
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='kick_trending',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Kick clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--category', '-c', required=True,
              help='Category slug to scrape (e.g., gaming, just-chatting)')
@click.option('--max-clips', '-n', type=int, default=None,
              help='Maximum number of clips to scrape')
def scrape_category(env_file, no_interactive, category, max_clips):
    """Scrape clips from a specific Kick category.
    
    This command scrapes clips from a specific category/game on Kick.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = KickCategoryPlugin(config, category_slug=category)
        
        # Scrape clips
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping Kick clips from category '{category}'...")
        
        try:
            ideas = plugin.scrape(max_clips=max_clips)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from category '{category}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_kick(idea['metrics'])
                
                # Add universal metrics to idea
                idea['universal_metrics'] = universal_metrics.to_dict()
                
                # Save to database
                success = db.insert_idea(
                    source='kick_category',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping category clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--streamer', '-s', required=True,
              help='Streamer username to scrape')
@click.option('--max-clips', '-n', type=int, default=None,
              help='Maximum number of clips to scrape')
def scrape_streamer(env_file, no_interactive, streamer, max_clips):
    """Scrape clips from a specific Kick streamer channel.
    
    This command scrapes clips from a specific streamer's channel on Kick.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = KickStreamerPlugin(config, streamer_username=streamer)
        
        # Scrape clips
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping Kick clips from streamer '{streamer}'...")
        
        try:
            ideas = plugin.scrape(max_clips=max_clips)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from streamer '{streamer}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_kick(idea['metrics'])
                
                # Add universal metrics to idea
                idea['universal_metrics'] = universal_metrics.to_dict()
                
                # Save to database
                success = db.insert_idea(
                    source='kick_streamer',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=idea['tags'],
                    score=universal_metrics.engagement_rate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping streamer clips: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show database statistics."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get statistics
        total = db.count_ideas()
        trending_count = db.count_by_source('kick_trending')
        category_count = db.count_by_source('kick_category')
        streamer_count = db.count_by_source('kick_streamer')
        
        click.echo(f"\n=== Kick Clips Database Statistics ===")
        click.echo(f"Database: {config.database_path}")
        click.echo(f"\nTotal clips: {total}")
        click.echo(f"  - Trending: {trending_count}")
        click.echo(f"  - Category: {category_count}")
        click.echo(f"  - Streamer: {streamer_count}")
        
        # Show top clips
        if total > 0:
            click.echo(f"\nTop 10 clips by engagement:")
            top_clips = db.get_all_ideas(limit=10, order_by='score')
            for i, clip in enumerate(top_clips, 1):
                score = clip.get('score', 0)
                title = clip.get('title', 'Untitled')
                source = clip.get('source', 'unknown')
                click.echo(f"  {i}. [{source}] {title[:60]} (score: {score:.2f})")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output JSON file path')
@click.option('--limit', '-l', type=int, default=100,
              help='Maximum number of ideas to export')
def export(env_file, no_interactive, output, limit):
    """Export ideas to JSON file in IdeaInspiration format."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get ideas
        ideas = db.get_all_ideas(limit=limit, order_by='score')
        
        # Transform to IdeaInspiration format
        idea_inspirations = []
        for idea in ideas:
            idea_obj = IdeaProcessor.process_database_record(idea)
            idea_inspirations.append(idea_obj.to_dict())
        
        # Write to file
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(idea_inspirations, f, indent=2, ensure_ascii=False)
        
        click.echo(f"Exported {len(idea_inspirations)} ideas to {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
