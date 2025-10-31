"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Forums.HackerNews."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.hn_frontpage import HNFrontpagePlugin
from .plugins.hn_new import HNNewPlugin
from .plugins.hn_best import HNBestPlugin
from .plugins.hn_type import HNTypePlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ HackerNews Source - Gather idea inspirations from HackerNews."""
    pass


@main.command('scrape-frontpage')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of stories to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_frontpage(env_file, top, no_interactive):
    """Scrape top stories from HackerNews frontpage.
    
    Examples:
        python -m src.cli scrape-frontpage
        python -m src.cli scrape-frontpage --top 20
        python -m src.cli scrape-frontpage -t 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize HN frontpage plugin
        frontpage_plugin = HNFrontpagePlugin(config)
        
        # Scrape stories
        total_scraped = 0
        total_saved = 0
        
        # Determine number of stories to scrape
        stories_count = top if top else config.hn_frontpage_max_posts
        
        click.echo(f"Scraping top stories from HackerNews frontpage")
        click.echo(f"Number of stories to scrape: {stories_count}")
        click.echo("")
        
        try:
            ideas = frontpage_plugin.scrape_topstories(limit=stories_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} stories")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_hackernews(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='hackernews_frontpage',
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
            click.echo(f"Error scraping frontpage: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total stories found: {total_scraped}")
        click.echo(f"Total stories saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-new')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of stories to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_new(env_file, top, no_interactive):
    """Scrape newest stories from HackerNews.
    
    Examples:
        python -m src.cli scrape-new
        python -m src.cli scrape-new --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        new_plugin = HNNewPlugin(config)
        
        total_scraped = 0
        total_saved = 0
        
        stories_count = top if top else config.hn_new_max_posts
        
        click.echo(f"Scraping new stories from HackerNews")
        click.echo(f"Number of stories: {stories_count}")
        click.echo("")
        
        try:
            ideas = new_plugin.scrape_newstories(limit=stories_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} new stories")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_hackernews(idea['metrics'])
                
                success = db.insert_idea(
                    source='hackernews_new',
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
            click.echo(f"Error scraping new stories: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total stories found: {total_scraped}")
        click.echo(f"Total stories saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-best')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of stories to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_best(env_file, top, no_interactive):
    """Scrape best (algorithmically ranked) stories from HackerNews.
    
    Examples:
        python -m src.cli scrape-best
        python -m src.cli scrape-best --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        best_plugin = HNBestPlugin(config)
        
        total_scraped = 0
        total_saved = 0
        
        stories_count = top if top else config.hn_best_max_posts
        
        click.echo(f"Scraping best stories from HackerNews")
        click.echo(f"Number of stories: {stories_count}")
        click.echo("")
        
        try:
            ideas = best_plugin.scrape_beststories(limit=stories_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} best stories")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_hackernews(idea['metrics'])
                
                success = db.insert_idea(
                    source='hackernews_best',
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
            click.echo(f"Error scraping best stories: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total stories found: {total_scraped}")
        click.echo(f"Total stories saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-ask')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of posts to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_ask(env_file, top, no_interactive):
    """Scrape Ask HN posts from HackerNews.
    
    Examples:
        python -m src.cli scrape-ask
        python -m src.cli scrape-ask --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        type_plugin = HNTypePlugin(config)
        
        total_scraped = 0
        total_saved = 0
        
        posts_count = top if top else config.hn_type_max_posts
        
        click.echo(f"Scraping Ask HN posts from HackerNews")
        click.echo(f"Number of posts: {posts_count}")
        click.echo("")
        
        try:
            ideas = type_plugin.scrape_ask(limit=posts_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} Ask HN posts")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_hackernews(idea['metrics'])
                
                success = db.insert_idea(
                    source='hackernews_ask',
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
            click.echo(f"Error scraping Ask HN posts: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-show')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--top', '-t', type=int, help='Number of posts to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_show(env_file, top, no_interactive):
    """Scrape Show HN posts from HackerNews.
    
    Examples:
        python -m src.cli scrape-show
        python -m src.cli scrape-show --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        type_plugin = HNTypePlugin(config)
        
        total_scraped = 0
        total_saved = 0
        
        posts_count = top if top else config.hn_type_max_posts
        
        click.echo(f"Scraping Show HN posts from HackerNews")
        click.echo(f"Number of posts: {posts_count}")
        click.echo("")
        
        try:
            ideas = type_plugin.scrape_show(limit=posts_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} Show HN posts")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_hackernews(idea['metrics'])
                
                success = db.insert_idea(
                    source='hackernews_show',
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
            click.echo(f"Error scraping Show HN posts: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('list')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--source', '-s', help='Filter by source')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of records to display (default: 20)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def list_posts(env_file, source, limit, no_interactive):
    """List collected HackerNews posts from database.
    
    Examples:
        python -m src.cli list
        python -m src.cli list --source hackernews_frontpage --limit 50
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        ideas = db.get_all_ideas(limit=limit)
        
        # Filter by source if specified
        if source:
            ideas = [idea for idea in ideas if idea['source'] == source]
        
        click.echo(f"\nCollected HackerNews Posts ({len(ideas)} records):")
        click.echo("=" * 80)
        
        for idea in ideas:
            click.echo(f"\nTitle: {idea['title']}")
            click.echo(f"Source: {idea['source']}")
            click.echo(f"ID: {idea['source_id']}")
            click.echo(f"Score: {idea.get('score', 0):.2f}")
            click.echo(f"Tags: {idea.get('tags', '')}")
            if idea.get('description'):
                desc = idea['description'][:100]
                click.echo(f"Description: {desc}...")
            click.echo("-" * 80)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('stats')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show statistics about collected HackerNews posts.
    
    Examples:
        python -m src.cli stats
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        total = db.count_ideas()
        
        click.echo("\n=== HackerNews Collection Statistics ===\n")
        click.echo(f"Total posts collected: {total}")
        click.echo(f"\nBy source:")
        
        sources = ['hackernews_frontpage', 'hackernews_new', 'hackernews_best', 
                   'hackernews_ask', 'hackernews_show']
        for source in sources:
            count = db.count_by_source(source)
            if count > 0:
                click.echo(f"  {source}: {count}")
        
        click.echo(f"\nDatabase: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('process')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=100,
              help='Maximum number of records to process (default: 100)')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for processed ideas (JSON)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def process(env_file, limit, output, no_interactive):
    """Process HackerNews posts to IdeaInspiration format.
    
    Examples:
        python -m src.cli process
        python -m src.cli process --limit 100 --output ideas.json
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get unprocessed records
        records = db_utils.get_unprocessed_ideas(config.database_url, limit=limit)
        
        click.echo(f"\nProcessing {len(records)} HackerNews posts...")
        
        processed_ideas = []
        for record in records:
            idea = IdeaProcessor.process(record)
            processed_ideas.append(idea.to_dict())
            
            # Mark as processed
            db_utils.mark_as_processed(config.database_url, record['id'])
            
            click.echo(f"  ✓ Processed: {idea.title[:60]}...")
        
        click.echo(f"\nProcessed {len(processed_ideas)} ideas")
        
        # Save to file if output specified
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(processed_ideas, f, indent=2, ensure_ascii=False)
            click.echo(f"Saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('clear')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.confirmation_option(prompt='Are you sure you want to delete all collected posts?')
def clear(env_file, no_interactive):
    """Delete all collected HackerNews posts from database.
    
    Examples:
        python -m src.cli clear
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        deleted = db_utils.clear_all_ideas(config.database_url)
        
        click.echo(f"\nDeleted {deleted} posts from database")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
