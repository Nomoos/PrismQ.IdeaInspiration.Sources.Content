"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Podcasts.ApplePodcasts."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.apple_charts import AppleChartsPlugin
from .plugins.apple_category import AppleCategoryPlugin
from .plugins.apple_show import AppleShowPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Apple Podcasts Source - Gather idea inspirations from Apple Podcasts."""
    pass


@main.command('scrape-charts')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--genre', '-g', default='all', help='Genre/category filter (default: all)')
@click.option('--top', '-t', type=int, help='Number of shows to scrape (default: config or 20)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_charts(env_file, genre, top, no_interactive):
    """Scrape ideas from Apple Podcasts charts.
    
    This command scrapes trending podcasts from Apple Podcasts charts
    using the iTunes Search API.
    
    Examples:
        python -m src.cli scrape-charts
        python -m src.cli scrape-charts --genre comedy --top 10
        python -m src.cli scrape-charts --genre technology --top 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Apple Charts plugin
        charts_plugin = AppleChartsPlugin(config)
        
        # Scrape from charts
        total_scraped = 0
        total_saved = 0
        
        # Determine number of shows to scrape
        shows_count = top if top else config.apple_podcasts_max_shows
        
        click.echo(f"Scraping from Apple Podcasts charts")
        click.echo(f"Genre: {genre}")
        click.echo(f"Number of shows: {shows_count}")
        click.echo("")
        
        try:
            ideas = charts_plugin.scrape_charts(genre=genre, top_n=shows_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from charts")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_apple_podcasts(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='apple_podcasts_charts',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']) if idea['tags'] else None,
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Apple Podcasts charts: {e}", err=True)
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
@click.option('--category', '-c', required=True, help='Category name or term')
@click.option('--top', '-t', type=int, help='Number of shows to scrape (default: config or 20)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_category(env_file, category, top, no_interactive):
    """Scrape ideas from a specific Apple Podcasts category.
    
    This command scrapes podcasts from a specific category using the
    iTunes Search API.
    
    Examples:
        python -m src.cli scrape-category --category "true crime"
        python -m src.cli scrape-category --category business --top 15
        python -m src.cli scrape-category --category technology --top 10
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Apple Category plugin
        category_plugin = AppleCategoryPlugin(config)
        
        # Scrape from category
        total_scraped = 0
        total_saved = 0
        
        # Determine number of shows to scrape
        shows_count = top if top else config.apple_podcasts_max_shows
        
        click.echo(f"Scraping from Apple Podcasts category: {category}")
        click.echo(f"Number of shows: {shows_count}")
        click.echo("")
        
        try:
            ideas = category_plugin.scrape_category(category=category, top_n=shows_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from category")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_apple_podcasts(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='apple_podcasts_category',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']) if idea['tags'] else None,
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Apple Podcasts category: {e}", err=True)
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
@click.option('--show', '-s', required=True, help='Show name or iTunes collection ID')
@click.option('--top', '-t', type=int, help='Number of episodes to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_show(env_file, show, top, no_interactive):
    """Scrape ideas from a specific podcast show.
    
    This command scrapes episodes from a specific podcast show using the
    iTunes Search API. You can specify the show by name or iTunes collection ID.
    
    Examples:
        python -m src.cli scrape-show --show "The Daily"
        python -m src.cli scrape-show --show 1200361736 --top 20
        python -m src.cli scrape-show --show "Serial" --top 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Apple Show plugin
        show_plugin = AppleShowPlugin(config)
        
        # Scrape from show
        total_scraped = 0
        total_saved = 0
        
        # Determine number of episodes to scrape
        episodes_count = top if top else config.apple_podcasts_max_episodes
        
        # Convert show to int if it's a number
        try:
            show_id = int(show)
        except ValueError:
            show_id = show
        
        click.echo(f"Scraping from Apple Podcasts show: {show}")
        click.echo(f"Number of episodes: {episodes_count}")
        click.echo("")
        
        try:
            ideas = show_plugin.scrape_show(show_id=show_id, top_n=episodes_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} episodes from show")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_apple_podcasts(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='apple_podcasts_show',
                    source_id=idea['source_id'],
                    title=idea['title'],
                    description=idea['description'],
                    tags=','.join(idea['tags']) if idea['tags'] else None,
                    score=universal_metrics.engagement_estimate or 0.0,
                    score_dictionary=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Apple Podcasts show: {e}", err=True)
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
              help='Maximum number of ideas to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected ideas."""
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
            click.echo("No ideas found.")
            return
        
        # Display ideas
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Ideas ({len(ideas)} total)")
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
    """Show statistics about collected ideas."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all ideas
        ideas = db.get_all_ideas(limit=10000)
        
        if not ideas:
            click.echo("No ideas collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_source = {}
        
        for idea in ideas:
            source = idea['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Idea Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Ideas: {total}\n")
        click.echo(f"Ideas by Source:")
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
    """Process unprocessed Apple Podcasts records to IdeaInspiration format.
    
    This command transforms ApplePodcastsSource records into the standardized
    IdeaInspiration model format as defined in PrismQ.IdeaInspiration.Model.
    
    The transformation includes:
    - Converting Apple Podcasts metadata to universal format
    - Extracting transcripts as content (if available)
    - Mapping tags to keywords
    - Building standardized metadata dictionary
    - Setting source_type to AUDIO
    
    Records are marked as processed=True after successful transformation.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db_utils.init_database(config.database_url)
        
        click.echo("Processing unprocessed Apple Podcasts records...")
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
@click.confirmation_option(prompt='Are you sure you want to clear all ideas?')
def clear(env_file, no_interactive):
    """Clear all ideas from the database."""
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
