"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Shorts.TikTok."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.tiktok_trending import TikTokTrendingPlugin
from .plugins.tiktok_hashtag import TikTokHashtagPlugin
from .plugins.tiktok_creator import TikTokCreatorPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ TikTok Source - Gather idea inspirations from TikTok videos."""
    pass


@main.command('scrape-trending')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--max-videos', '-m', type=int, help='Maximum videos to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_trending(env_file, max_videos, no_interactive):
    """Scrape ideas from TikTok trending videos.
    
    This command scrapes trending TikTok videos with comprehensive metadata
    including engagement metrics, creator info, and content details.
    
    Examples:
        python -m src.cli scrape-trending
        python -m src.cli scrape-trending --max-videos 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize TikTok trending plugin
        try:
            trending_plugin = TikTokTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from TikTok trending
        total_scraped = 0
        total_saved = 0
        
        click.echo("Scraping TikTok trending videos...")
        
        try:
            ideas = trending_plugin.scrape(max_videos=max_videos)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from TikTok trending")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_tiktok(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='tiktok_trending',
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
            click.echo(f"Error scraping TikTok trending: {e}", err=True)
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-hashtag')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--hashtag', '-h', help='Hashtag to scrape (without #)')
@click.option('--max-videos', '-m', type=int, help='Maximum videos to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_hashtag(env_file, hashtag, max_videos, no_interactive):
    """Scrape ideas from TikTok by hashtag.
    
    This command scrapes TikTok videos with a specific hashtag, extracting
    comprehensive metadata and engagement metrics.
    
    Examples:
        python -m src.cli scrape-hashtag --hashtag startup
        python -m src.cli scrape-hashtag --hashtag tech --max-videos 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize TikTok hashtag plugin
        try:
            if hashtag:
                hashtag_plugin = TikTokHashtagPlugin(config, hashtag=hashtag)
            else:
                hashtag_plugin = TikTokHashtagPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nSpecify hashtag with --hashtag or set TIKTOK_HASHTAG in .env", err=True)
            sys.exit(1)
        
        # Scrape from TikTok hashtag
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping TikTok hashtag: #{hashtag_plugin.hashtag}...")
        
        try:
            ideas = hashtag_plugin.scrape(max_videos=max_videos)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from TikTok hashtag #{hashtag_plugin.hashtag}")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_tiktok(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source=f'tiktok_hashtag_{hashtag_plugin.hashtag}',
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
            click.echo(f"Error scraping TikTok hashtag: {e}", err=True)
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-creator')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--username', '-u', help='TikTok creator username (without @)')
@click.option('--max-videos', '-m', type=int, help='Maximum videos to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_creator(env_file, username, max_videos, no_interactive):
    """Scrape ideas from a specific TikTok creator.
    
    This command scrapes videos from a TikTok creator's profile with
    comprehensive metadata extraction.
    
    Examples:
        python -m src.cli scrape-creator --username creator123
        python -m src.cli scrape-creator --username creator123 --max-videos 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize TikTok creator plugin
        try:
            if username:
                creator_plugin = TikTokCreatorPlugin(config, username=username)
            else:
                creator_plugin = TikTokCreatorPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nSpecify username with --username or set TIKTOK_CREATOR_USERNAME in .env", err=True)
            sys.exit(1)
        
        # Scrape from TikTok creator
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping TikTok creator: @{creator_plugin.username}...")
        
        try:
            ideas = creator_plugin.scrape(max_videos=max_videos)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} ideas from TikTok creator @{creator_plugin.username}")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_tiktok(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source=f'tiktok_creator_{creator_plugin.username}',
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
            click.echo(f"Error scraping TikTok creator: {e}", err=True)
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total ideas found: {total_scraped}")
        click.echo(f"Total ideas saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('process')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def process(env_file, no_interactive):
    """Process TikTok ideas to IdeaInspiration format.
    
    This command transforms TikTokSource database records into the
    standardized IdeaInspiration model format.
    
    Examples:
        python -m src.cli process
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all unprocessed ideas
        ideas = db.get_all_ideas(processed=False)
        
        click.echo(f"Processing {len(ideas)} unprocessed ideas...")
        
        processed_count = 0
        for idea in ideas:
            try:
                # Transform to IdeaInspiration format
                idea_inspiration = IdeaProcessor.process(idea)
                
                # Mark as processed
                db.mark_processed(idea['source'], idea['source_id'])
                processed_count += 1
                
                # Print summary
                click.echo(f"  [{processed_count}/{len(ideas)}] Processed: {idea['title'][:50]}...")
                
            except ValueError as e:
                click.echo(f"  Error processing idea {idea.get('source_id')}: {e}", err=True)
                continue
        
        click.echo(f"\nProcessing complete!")
        click.echo(f"Total processed: {processed_count}/{len(ideas)}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('stats')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Display database statistics.
    
    Examples:
        python -m src.cli stats
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get statistics
        statistics = db.get_statistics()
        
        click.echo("\n=== TikTok Source Database Statistics ===\n")
        click.echo(f"Total ideas: {statistics['total']}")
        click.echo(f"Processed: {statistics['processed']}")
        click.echo(f"Unprocessed: {statistics['unprocessed']}")
        
        if statistics['by_source']:
            click.echo("\nIdeas by source:")
            for source, count in statistics['by_source'].items():
                click.echo(f"  {source}: {count}")
        
        click.echo(f"\nDatabase: {config.database_path}\n")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('export')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--output', '-o', type=click.Path(), 
              default='tiktok_ideas.json',
              help='Output JSON file path (default: tiktok_ideas.json)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def export(env_file, output, no_interactive):
    """Export ideas to JSON file.
    
    Examples:
        python -m src.cli export
        python -m src.cli export --output my_ideas.json
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all ideas
        ideas = db.get_all_ideas()
        
        click.echo(f"Exporting {len(ideas)} ideas to {output}...")
        
        # Convert to JSON-serializable format
        export_data = []
        for idea in ideas:
            # Parse score_dictionary if it's a string
            score_dict = idea.get('score_dictionary')
            if isinstance(score_dict, str):
                try:
                    score_dict = json.loads(score_dict)
                except json.JSONDecodeError:
                    score_dict = {}
            
            export_data.append({
                'id': idea.get('id'),
                'source': idea.get('source'),
                'source_id': idea.get('source_id'),
                'title': idea.get('title'),
                'description': idea.get('description'),
                'tags': idea.get('tags'),
                'score': idea.get('score'),
                'metrics': score_dict,
                'processed': idea.get('processed'),
                'created_at': str(idea.get('created_at')),
                'updated_at': str(idea.get('updated_at')),
            })
        
        # Write to file
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        click.echo(f"\nExport complete!")
        click.echo(f"Total exported: {len(export_data)}")
        click.echo(f"Output file: {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
