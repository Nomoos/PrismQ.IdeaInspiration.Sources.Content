"""Command-line interface for PrismQ.IdeaInspiration.Sources.Content.Articles.WebArticleSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .core.database import Database
from .core.metrics import UniversalMetrics
from .plugins.article_url import ArticleUrlPlugin
from .plugins.article_rss import ArticleRssPlugin
from .plugins.article_sitemap import ArticleSitemapPlugin
from .core import db_utils
from .core.idea_processor import IdeaProcessor


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Web Article Source - Gather idea inspirations from web articles."""
    pass


@main.command('scrape-url')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--url', '-u', multiple=True, help='Article URL to scrape (can be specified multiple times)')
@click.option('--file', '-f', type=click.Path(exists=True), 
              help='File containing URLs (one per line)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_url(env_file, url, file, no_interactive):
    """Scrape articles from specific URLs.
    
    Examples:
        python -m src.cli scrape-url --url https://example.com/article1
        python -m src.cli scrape-url --file urls.txt
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Collect URLs
        urls = list(url) if url else []
        if file:
            with open(file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        
        if not urls:
            click.echo("Error: No URLs provided. Use --url or --file", err=True)
            sys.exit(1)
        
        # Initialize plugin
        try:
            url_plugin = ArticleUrlPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape articles
        total_scraped = 0
        total_saved = 0
        
        click.echo(f"Scraping {len(urls)} article(s)...")
        click.echo("")
        
        try:
            articles = url_plugin.scrape(urls)
            total_scraped = len(articles)
            click.echo(f"\nFound {len(articles)} articles")
            
            # Process and save each article
            for article in articles:
                # Convert metrics to universal format
                universal_metrics = UniversalMetrics.from_article(article)
                
                # Save to database
                success = db.insert_article(
                    source=article.get('source', 'web_article'),
                    source_id=article['source_id'],
                    title=article['title'],
                    description=article.get('description'),
                    content=article.get('content', {}).get('text'),
                    tags=','.join(article.get('tags', [])),
                    author=article.get('author', {}).get('name') if isinstance(article.get('author'), dict) else article.get('author'),
                    url=article.get('url'),
                    published_at=article.get('published_at'),
                    score=universal_metrics.quality_score or 0.0,
                    score_dictionary=json.dumps(universal_metrics.to_dict())
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping articles: {e}", err=True)
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


@main.command('scrape-rss')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--feed', '-f', multiple=True, help='RSS/Atom feed URL (can be specified multiple times)')
@click.option('--file', type=click.Path(exists=True), 
              help='File containing feed URLs (one per line)')
@click.option('--max', '-m', type=int, help='Maximum articles per feed (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_rss(env_file, feed, file, max, no_interactive):
    """Scrape articles from RSS/Atom feeds.
    
    Examples:
        python -m src.cli scrape-rss --feed https://example.com/rss
        python -m src.cli scrape-rss --file feeds.txt --max 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Collect feed URLs
        feed_urls = list(feed) if feed else []
        if file:
            with open(file, 'r') as f:
                feed_urls.extend([line.strip() for line in f if line.strip()])
        
        if not feed_urls:
            click.echo("Error: No feed URLs provided. Use --feed or --file", err=True)
            sys.exit(1)
        
        # Initialize plugin
        try:
            rss_plugin = ArticleRssPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape articles
        total_scraped = 0
        total_saved = 0
        
        max_articles = max if max else getattr(config, 'web_article_max_articles', 10)
        
        click.echo(f"Scraping from {len(feed_urls)} RSS feed(s)")
        click.echo(f"Maximum articles per feed: {max_articles}")
        click.echo("")
        
        try:
            articles = rss_plugin.scrape(feed_urls, max_articles)
            total_scraped = len(articles)
            click.echo(f"\nFound {len(articles)} articles")
            
            # Process and save each article
            for article in articles:
                # Convert metrics to universal format
                universal_metrics = UniversalMetrics.from_article(article)
                
                # Save to database
                success = db.insert_article(
                    source=article.get('source', 'web_article_rss'),
                    source_id=article['source_id'],
                    title=article['title'],
                    description=article.get('description'),
                    content=article.get('content', {}).get('text'),
                    tags=','.join(article.get('tags', [])),
                    author=article.get('author', {}).get('name') if isinstance(article.get('author'), dict) else article.get('author'),
                    url=article.get('url'),
                    published_at=article.get('published_at'),
                    score=universal_metrics.quality_score or 0.0,
                    score_dictionary=json.dumps(universal_metrics.to_dict())
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping RSS feeds: {e}", err=True)
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


@main.command('scrape-sitemap')
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--sitemap', '-s', multiple=True, help='Sitemap URL (can be specified multiple times)')
@click.option('--file', '-f', type=click.Path(exists=True), 
              help='File containing sitemap URLs (one per line)')
@click.option('--max', '-m', type=int, help='Maximum articles per sitemap (default: config or 10)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_sitemap(env_file, sitemap, file, max, no_interactive):
    """Scrape articles from XML sitemaps.
    
    Examples:
        python -m src.cli scrape-sitemap --sitemap https://example.com/sitemap.xml
        python -m src.cli scrape-sitemap --file sitemaps.txt --max 15
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Collect sitemap URLs
        sitemap_urls = list(sitemap) if sitemap else []
        if file:
            with open(file, 'r') as f:
                sitemap_urls.extend([line.strip() for line in f if line.strip()])
        
        if not sitemap_urls:
            click.echo("Error: No sitemap URLs provided. Use --sitemap or --file", err=True)
            sys.exit(1)
        
        # Initialize plugin
        try:
            sitemap_plugin = ArticleSitemapPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape articles
        total_scraped = 0
        total_saved = 0
        
        max_articles = max if max else getattr(config, 'web_article_max_articles', 10)
        
        click.echo(f"Scraping from {len(sitemap_urls)} sitemap(s)")
        click.echo(f"Maximum articles per sitemap: {max_articles}")
        click.echo("")
        
        try:
            articles = sitemap_plugin.scrape(sitemap_urls, max_articles)
            total_scraped = len(articles)
            click.echo(f"\nFound {len(articles)} articles")
            
            # Process and save each article
            for article in articles:
                # Convert metrics to universal format
                universal_metrics = UniversalMetrics.from_article(article)
                
                # Save to database
                success = db.insert_article(
                    source=article.get('source', 'web_article_sitemap'),
                    source_id=article['source_id'],
                    title=article['title'],
                    description=article.get('description'),
                    content=article.get('content', {}).get('text'),
                    tags=','.join(article.get('tags', [])),
                    author=article.get('author', {}).get('name') if isinstance(article.get('author'), dict) else article.get('author'),
                    url=article.get('url'),
                    published_at=article.get('published_at'),
                    score=universal_metrics.quality_score or 0.0,
                    score_dictionary=json.dumps(universal_metrics.to_dict())
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping sitemaps: {e}", err=True)
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
              help='Maximum number of articles to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected articles."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get articles
        articles = db.get_all_articles(limit=limit)
        
        # Filter by source if specified
        if source:
            articles = [article for article in articles if article['source'] == source]
        
        if not articles:
            click.echo("No articles found.")
            return
        
        # Display articles
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Articles ({len(articles)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, article in enumerate(articles, 1):
            click.echo(f"{i}. [{article['source'].upper()}] {article['title']}")
            if article.get('author'):
                click.echo(f"   Author: {article['author']}")
            if article.get('url'):
                click.echo(f"   URL: {article['url']}")
            if article.get('tags'):
                click.echo(f"   Tags: {article['tags']}")
            if article.get('description'):
                desc = article['description'][:150]
                if len(article['description']) > 150:
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
    """Show statistics about collected articles."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all articles
        articles = db.get_all_articles(limit=10000)
        
        if not articles:
            click.echo("No articles collected yet.")
            return
        
        # Calculate statistics
        total = len(articles)
        by_source = {}
        
        for article in articles:
            source = article['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Article Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Articles: {total}\n")
        click.echo(f"Articles by Source:")
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
              help='Disable interactive prompts for missing configuration')
@click.option('--limit', '-l', type=int, default=None,
              help='Maximum number of records to process (default: all unprocessed)')
@click.option('--output', '-o', type=click.Path(),
              help='Optional output file path to save processed ideas as JSON')
def process(env_file, no_interactive, limit, output):
    """Process unprocessed article records to IdeaInspiration format.
    
    This command transforms WebArticleSource records into the standardized
    IdeaInspiration model format as defined in PrismQ.IdeaInspiration.Model.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db_utils.init_database(config.database_url)
        
        click.echo("Processing unprocessed article records...")
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
@click.confirmation_option(prompt='Are you sure you want to clear all articles?')
def clear(env_file, no_interactive):
    """Clear all articles from the database."""
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
