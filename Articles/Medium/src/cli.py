"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Articles.Medium."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.medium_trending import MediumTrendingPlugin
from .plugins.medium_tag import MediumTagPlugin
from .plugins.medium_publication import MediumPublicationPlugin
from .plugins.medium_author import MediumAuthorPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Medium Source - Gather idea inspirations from Medium articles."""
    pass


@main.command('scrape-trending')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of articles to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_trending(env_file, top, no_interactive):
    """Scrape trending articles from Medium.
    
    This command scrapes trending articles from Medium.com with comprehensive
    metadata including claps, responses, reading time, and author information.
    
    Examples:
        python -m src.cli scrape-trending
        python -m src.cli scrape-trending --top 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Medium trending plugin
        try:
            trending_plugin = MediumTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from trending
        total_scraped = 0
        total_saved = 0
        
        # Determine number of articles to scrape
        articles_count = top if top else getattr(config, 'medium_trending_max_articles', 10)
        
        click.echo(f"Scraping trending articles from Medium")
        click.echo(f"Number of articles to scrape: {articles_count}")
        click.echo("")
        
        try:
            ideas = trending_plugin.scrape(top_n=articles_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} trending articles")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_medium(idea)
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='medium_trending',
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
            click.echo(f"Error scraping Medium trending: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total articles found: {total_scraped}")
        click.echo(f"Total articles saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-tag')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--tag', '-t', required=True, help='Tag to search for')
@click.option('--top', '-n', type=int, help='Number of articles to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_tag(env_file, tag, top, no_interactive):
    """Scrape articles by tag from Medium.
    
    This command scrapes articles with a specific tag from Medium.com.
    
    Examples:
        python -m src.cli scrape-tag --tag "artificial-intelligence"
        python -m src.cli scrape-tag --tag "startup" --top 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Medium tag plugin
        try:
            tag_plugin = MediumTagPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from tag
        total_scraped = 0
        total_saved = 0
        
        # Determine number of articles to scrape
        articles_count = top if top else getattr(config, 'medium_tag_max_articles', 10)
        
        click.echo(f"Scraping Medium articles with tag: '{tag}'")
        click.echo(f"Number of articles to scrape: {articles_count}")
        click.echo("")
        
        try:
            ideas = tag_plugin.scrape(tag=tag, top_n=articles_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} articles for tag '{tag}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_medium(idea)
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='medium_tag',
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
            click.echo(f"Error scraping Medium tag: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total articles found: {total_scraped}")
        click.echo(f"Total articles saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-publication')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--publication', '-p', required=True, help='Publication name or URL')
@click.option('--top', '-n', type=int, help='Number of articles to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_publication(env_file, publication, top, no_interactive):
    """Scrape articles from a Medium publication.
    
    This command scrapes articles from a specific Medium publication.
    
    Examples:
        python -m src.cli scrape-publication --publication "towards-data-science"
        python -m src.cli scrape-publication --publication "better-programming" --top 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Medium publication plugin
        try:
            publication_plugin = MediumPublicationPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from publication
        total_scraped = 0
        total_saved = 0
        
        # Determine number of articles to scrape
        articles_count = top if top else getattr(config, 'medium_publication_max_articles', 10)
        
        click.echo(f"Scraping Medium publication: '{publication}'")
        click.echo(f"Number of articles to scrape: {articles_count}")
        click.echo("")
        
        try:
            ideas = publication_plugin.scrape(publication=publication, top_n=articles_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} articles from publication '{publication}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_medium(idea)
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='medium_publication',
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
            click.echo(f"Error scraping Medium publication: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total articles found: {total_scraped}")
        click.echo(f"Total articles saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-author')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--author', '-a', required=True, help='Author username (with or without @)')
@click.option('--top', '-n', type=int, help='Number of articles to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_author(env_file, author, top, no_interactive):
    """Scrape articles by author from Medium.
    
    This command scrapes articles from a specific Medium author's profile.
    
    Examples:
        python -m src.cli scrape-author --author "@username"
        python -m src.cli scrape-author --author "username" --top 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Medium author plugin
        try:
            author_plugin = MediumAuthorPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from author
        total_scraped = 0
        total_saved = 0
        
        # Determine number of articles to scrape
        articles_count = top if top else getattr(config, 'medium_author_max_articles', 10)
        
        click.echo(f"Scraping Medium author: '{author}'")
        click.echo(f"Number of articles to scrape: {articles_count}")
        click.echo("")
        
        try:
            ideas = author_plugin.scrape(author=author, top_n=articles_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} articles from author '{author}'")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_medium(idea)
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='medium_author',
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
            click.echo(f"Error scraping Medium author: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total articles found: {total_scraped}")
        click.echo(f"Total articles saved: {total_saved}")
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
        ideas = db.get_all_ideas()
        
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
    """Process unprocessed Medium records to IdeaInspiration format.
    
    This command transforms MediumSource records into the standardized
    IdeaInspiration model format as defined in PrismQ.IdeaInspiration.Model.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db_utils.init_database(config.database_url)
        
        click.echo("Processing unprocessed Medium article records...")
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
