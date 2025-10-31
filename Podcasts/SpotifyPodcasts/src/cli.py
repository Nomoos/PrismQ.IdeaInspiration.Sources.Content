"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Podcasts.SpotifyPodcasts."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.spotify_trending import SpotifyTrendingPlugin
from .plugins.spotify_category import SpotifyCategoryPlugin
from .plugins.spotify_show import SpotifyShowPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Spotify Podcasts Source - Gather idea inspirations from Spotify podcasts."""
    pass


@main.command('scrape-trending')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of episodes to scrape (default: config or 10)')
@click.option('--market', '-m', default='US', help='Market/region code (default: US)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_trending(env_file, top, market, no_interactive):
    """Scrape trending podcast episodes from Spotify.
    
    This command uses Spotify Web API to scrape trending/popular podcast episodes
    with comprehensive metadata extraction.
    
    Examples:
        python -m src.cli scrape-trending
        python -m src.cli scrape-trending --top 20 --market GB
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Spotify trending plugin
        try:
            trending_plugin = SpotifyTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nInstall spotipy with: pip install spotipy", err=True)
            sys.exit(1)
        
        # Scrape from trending
        total_scraped = 0
        total_saved = 0
        
        # Determine number of episodes to scrape
        episodes_count = top if top else getattr(config, 'spotify_trending_max_episodes', 10)
        
        click.echo(f"Scraping trending podcast episodes from Spotify")
        click.echo(f"Market: {market}")
        click.echo(f"Number of episodes to scrape: {episodes_count}")
        click.echo("")
        
        try:
            ideas = trending_plugin.scrape(top_n=episodes_count, market=market)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from trending")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_spotify(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='spotify_trending',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']),
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping trending podcasts: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total episodes found: {total_scraped}")
        click.echo(f"Total episodes saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-category')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--category', '-c', required=True, help='Category name (e.g., "business", "comedy")')
@click.option('--top', '-t', type=int, help='Number of episodes to scrape (default: config or 10)')
@click.option('--market', '-m', default='US', help='Market/region code (default: US)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_category(env_file, category, top, market, no_interactive):
    """Scrape podcast episodes from a specific category.
    
    This command searches for podcasts in a specific category and scrapes
    their latest episodes.
    
    Examples:
        python -m src.cli scrape-category --category "business"
        python -m src.cli scrape-category --category "true crime" --top 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Spotify category plugin
        try:
            category_plugin = SpotifyCategoryPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nInstall spotipy with: pip install spotipy", err=True)
            sys.exit(1)
        
        # Scrape from category
        total_scraped = 0
        total_saved = 0
        
        # Determine number of episodes to scrape
        episodes_count = top if top else getattr(config, 'spotify_category_max_episodes', 10)
        
        click.echo(f"Scraping podcast episodes from category: {category}")
        click.echo(f"Market: {market}")
        click.echo(f"Number of episodes to scrape: {episodes_count}")
        click.echo("")
        
        try:
            ideas = category_plugin.scrape(category=category, top_n=episodes_count, market=market)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from category '{category}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_spotify(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='spotify_category',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']),
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping category: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total episodes found: {total_scraped}")
        click.echo(f"Total episodes saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-show')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--show-id', '-s', required=True, help='Spotify show ID or URI')
@click.option('--top', '-t', type=int, help='Number of episodes to scrape (default: config or 10)')
@click.option('--market', '-m', default='US', help='Market/region code (default: US)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_show(env_file, show_id, top, market, no_interactive):
    """Scrape episodes from a specific podcast show.
    
    This command scrapes episodes from a specific podcast show by its
    Spotify ID or URI.
    
    Examples:
        python -m src.cli scrape-show --show-id "4rOoJ6Egrf8K2IrywzwOMk"
        python -m src.cli scrape-show --show-id "spotify:show:4rOoJ6Egrf8K2IrywzwOMk" --top 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Spotify show plugin
        try:
            show_plugin = SpotifyShowPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nInstall spotipy with: pip install spotipy", err=True)
            sys.exit(1)
        
        # Scrape from show
        total_scraped = 0
        total_saved = 0
        
        # Determine number of episodes to scrape
        episodes_count = top if top else getattr(config, 'spotify_show_max_episodes', 10)
        
        click.echo(f"Scraping episodes from show: {show_id}")
        click.echo(f"Market: {market}")
        click.echo(f"Number of episodes to scrape: {episodes_count}")
        click.echo("")
        
        try:
            ideas = show_plugin.scrape(show_id=show_id, top_n=episodes_count, market=market)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from show")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_spotify(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='spotify_show',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']),
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping show: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total episodes found: {total_scraped}")
        click.echo(f"Total episodes saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of episodes to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected podcast episodes."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get ideas
        ideas = db.get_all_ideas(limit=limit)
        
        # Filter by source if specified
        if source:
            ideas = [idea for idea in ideas if idea['source'] == source]
        
        if not ideas:
            click.echo("No podcast episodes found.")
            return
        
        # Display ideas
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Podcast Episodes ({len(ideas)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. [{idea['source'].upper()}] {idea['title']}")
            click.echo(f"   ID: {idea['source_id']}")
            if idea['tags']:
                click.echo(f"   Tags: {idea['tags']}")
            if idea['description']:
                desc = idea['description'][:150]
                if len(idea['description']) > 150:
                    desc += "..."
                click.echo(f"   Description: {desc}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Show statistics about collected podcast episodes."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all ideas
        ideas = db.get_all_ideas()
        
        if not ideas:
            click.echo("No podcast episodes collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_source = {}
        
        for idea in ideas:
            source = idea['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Podcast Episode Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Episodes: {total}\n")
        click.echo(f"Episodes by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source.capitalize()}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--limit', '-l', type=int, default=None,
              help='Maximum number of records to process (default: all unprocessed)')
@click.option('--output', '-o', type=click.Path(),
              help='Optional output file path to save processed ideas as JSON')
def process(env_file, no_interactive, limit, output):
    """Process unprocessed podcast records to IdeaInspiration format.
    
    This command transforms SpotifyPodcastsSource records into the standardized
    IdeaInspiration model format as defined in PrismQ.IdeaInspiration.Model.
    
    Records are marked as processed=True after successful transformation.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db_utils.init_database(config.database_url)
        
        click.echo("Processing unprocessed podcast records...")
        click.echo()
        
        # Get unprocessed records
        unprocessed_records = db_utils.get_unprocessed_records(config.database_url, limit=limit)
        total_unprocessed = len(unprocessed_records)
        
        if total_unprocessed == 0:
            click.echo("No unprocessed records found.")
            return
        
        click.echo(f"Found {total_unprocessed} unprocessed record(s)")
        click.echo()
        
        # Process records
        processed_count = 0
        failed_count = 0
        processed_ideas = []
        
        for record in unprocessed_records:
            try:
                # Transform to IdeaInspiration
                idea = IdeaProcessor.process(record)
                
                # Mark as processed
                db_utils.mark_as_processed(config.database_url, record['id'])
                
                processed_count += 1
                processed_ideas.append(idea.to_dict())
                
                click.echo(f"✓ Processed: {record['title'][:60]}...")
                
            except Exception as e:
                failed_count += 1
                click.echo(f"✗ Failed: {record['title'][:60]}... - {e}", err=True)
        
        click.echo()
        click.echo("=" * 60)
        click.echo(f"Processing complete!")
        click.echo(f"Total processed: {processed_count}")
        if failed_count > 0:
            click.echo(f"Total failed: {failed_count}")
        click.echo(f"Database: {config.database_url}")
        
        # Save to output file if specified
        if output and processed_ideas:
            output_path = Path(output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_ideas, f, indent=2, ensure_ascii=False)
            click.echo(f"Saved processed ideas to: {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all podcast episodes?')
def clear(env_file, no_interactive):
    """Clear all podcast episodes from the database."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Delete database file
        db_path = Path(config.database_path)
        if db_path.exists():
            db_path.unlink()
            click.echo(f"Database cleared: {config.database_path}")
        else:
            click.echo("Database does not exist.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
