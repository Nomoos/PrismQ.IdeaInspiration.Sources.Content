"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Forums.Reddit."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.reddit_trending import RedditTrendingPlugin
from .plugins.reddit_subreddit import RedditSubredditPlugin
from .plugins.reddit_rising import RedditRisingPlugin
from .plugins.reddit_search import RedditSearchPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Reddit Source - Gather idea inspirations from Reddit."""
    pass


@main.command('scrape-trending')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--subreddit', '-s', default='all',
              help='Subreddit to scrape (default: all)')
@click.option('--top', '-t', type=int, help='Number of posts to scrape (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_trending(env_file, subreddit, top, no_interactive):
    """Scrape trending posts from Reddit.
    
    Examples:
        python -m src.cli scrape-trending
        python -m src.cli scrape-trending --subreddit python --top 20
        python -m src.cli scrape-trending -s startup -t 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Reddit trending plugin
        try:
            trending_plugin = RedditTrendingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape posts
        total_scraped = 0
        total_saved = 0
        
        # Determine number of posts to scrape
        posts_count = top if top else config.reddit_trending_max_posts
        
        click.echo(f"Scraping trending posts from r/{subreddit}")
        click.echo(f"Number of posts to scrape: {posts_count}")
        click.echo("")
        
        try:
            ideas = trending_plugin.scrape_trending(subreddit=subreddit, limit=posts_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} trending posts")
            
            # Process and save each idea
            for idea in ideas:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_reddit(idea['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_idea(
                    source='reddit_trending',
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
            click.echo(f"Error scraping trending posts: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command('scrape-subreddit')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--subreddit', '-s', required=True, 
              help='Subreddit to scrape')
@click.option('--top', '-t', type=int, help='Number of posts to scrape')
@click.option('--sort', type=click.Choice(['hot', 'new', 'top', 'rising']), default='hot',
              help='Sort method (default: hot)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_subreddit(env_file, subreddit, top, sort, no_interactive):
    """Scrape posts from a specific subreddit.
    
    Examples:
        python -m src.cli scrape-subreddit --subreddit python
        python -m src.cli scrape-subreddit -s startup --sort top --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            subreddit_plugin = RedditSubredditPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        total_scraped = 0
        total_saved = 0
        
        posts_count = top if top else config.reddit_subreddit_max_posts
        
        click.echo(f"Scraping r/{subreddit} ({sort})")
        click.echo(f"Number of posts: {posts_count}")
        click.echo("")
        
        try:
            ideas = subreddit_plugin.scrape_by_sort(subreddit=subreddit, limit=posts_count, sort=sort)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} posts")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_reddit(idea['metrics'])
                
                success = db.insert_idea(
                    source='reddit_subreddit',
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
            click.echo(f"Error scraping subreddit: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-rising')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--subreddit', '-s', default='all',
              help='Subreddit to scrape (default: all)')
@click.option('--top', '-t', type=int, help='Number of posts to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_rising(env_file, subreddit, top, no_interactive):
    """Scrape rising posts from Reddit.
    
    Rising posts are quickly gaining traction, indicating viral potential.
    
    Examples:
        python -m src.cli scrape-rising
        python -m src.cli scrape-rising --subreddit startup --top 15
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            rising_plugin = RedditRisingPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        total_scraped = 0
        total_saved = 0
        
        posts_count = top if top else config.reddit_rising_max_posts
        
        click.echo(f"Scraping rising posts from r/{subreddit}")
        click.echo(f"Number of posts: {posts_count}")
        click.echo("")
        
        try:
            ideas = rising_plugin.scrape_rising(subreddit=subreddit, limit=posts_count)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} rising posts")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_reddit(idea['metrics'])
                
                success = db.insert_idea(
                    source='reddit_rising',
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
            click.echo(f"Error scraping rising posts: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command('scrape-search')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--subreddit', '-s', default='all',
              help='Subreddit to search in (default: all)')
@click.option('--top', '-t', type=int, help='Number of posts to scrape')
@click.option('--sort', type=click.Choice(['relevance', 'hot', 'top', 'new', 'comments']), 
              default='relevance', help='Sort method')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def scrape_search(env_file, query, subreddit, top, sort, no_interactive):
    """Search Reddit posts by keyword.
    
    Examples:
        python -m src.cli scrape-search --query "startup ideas"
        python -m src.cli scrape-search -q "AI" -s artificial --top 20
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        try:
            search_plugin = RedditSearchPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        total_scraped = 0
        total_saved = 0
        
        posts_count = top if top else config.reddit_search_max_posts
        
        click.echo(f"Searching r/{subreddit} for '{query}'")
        click.echo(f"Sort: {sort}, Limit: {posts_count}")
        click.echo("")
        
        try:
            ideas = search_plugin.scrape_by_query(query=query, subreddit=subreddit, 
                                                   limit=posts_count, sort=sort)
            total_scraped = len(ideas)
            click.echo(f"\nFound {len(ideas)} posts")
            
            for idea in ideas:
                universal_metrics = UniversalMetrics.from_reddit(idea['metrics'])
                
                success = db.insert_idea(
                    source='reddit_search',
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
            click.echo(f"Error searching Reddit: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total posts found: {total_scraped}")
        click.echo(f"Total posts saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of ideas to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
def list(env_file, limit, source, no_interactive):
    """List collected Reddit posts."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        ideas = db.get_all_ideas(limit=limit)
        
        if source:
            ideas = [idea for idea in ideas if idea['source'] == source]
        
        if not ideas:
            click.echo("No posts found.")
            return
        
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Reddit Posts ({len(ideas)} total)")
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
              help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show statistics about collected Reddit posts."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        ideas = db.get_all_ideas()
        
        if not ideas:
            click.echo("No posts collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_source = {}
        
        for idea in ideas:
            source = idea['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Reddit Post Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Posts: {total}\n")
        click.echo(f"Posts by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts')
@click.option('--limit', '-l', type=int, default=None,
              help='Maximum number of records to process (default: all unprocessed)')
@click.option('--output', '-o', type=click.Path(),
              help='Optional output file path to save processed ideas as JSON')
def process(env_file, no_interactive, limit, output):
    """Process unprocessed Reddit records to IdeaInspiration format.
    
    This command transforms RedditSource records into the standardized
    IdeaInspiration model format as defined in PrismQ.IdeaInspiration.Model.
    """
    try:
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db_utils.init_database(config.database_url)
        
        click.echo("Processing unprocessed Reddit records...")
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
              help='Disable interactive prompts')
@click.confirmation_option(prompt='Are you sure you want to clear all posts?')
def clear(env_file, no_interactive):
    """Clear all Reddit posts from the database."""
    try:
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
