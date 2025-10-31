# WebArticleSource

**General web article scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping article content from various web sources with comprehensive metadata extraction. It supports multiple scraping methods:

- **URL-based scraping**: Direct article extraction from URLs
- **RSS/Atom feeds**: Automatic article discovery and extraction from feeds
- **XML sitemaps**: Bulk article discovery from sitemaps

## Features

### Content Extraction
- **Full Article Text**: Clean text extraction using trafilatura and newspaper3k
- **Metadata**: Title, author, publication date, tags, description
- **Article Metrics**: Word count, reading time, quality scores
- **Universal Metrics**: Engagement rates, freshness scores, social metrics

### Scraping Methods
- **URL Scraping**: Extract individual articles directly
- **RSS Feeds**: Parse feeds and extract articles automatically  
- **Sitemaps**: Discover and scrape articles from XML sitemaps
- **Multi-source Aggregation**: Combine articles from multiple sources

### Data Quality
- **Content Deduplication**: URL-based hashing prevents duplicates
- **Quality Scoring**: Automatic quality assessment based on multiple factors
- **Freshness Tracking**: Time-based relevance scoring
- **SQLite Storage**: Persistent storage with full metadata

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the WebArticles module
cd Sources/Content/Articles/WebArticles

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (optional)
```

## Usage

### Scrape from URLs

```bash
# Scrape a single article
python -m src.cli scrape-url --url https://example.com/article

# Scrape multiple articles
python -m src.cli scrape-url --url https://example.com/article1 --url https://example.com/article2

# Scrape from a file of URLs
python -m src.cli scrape-url --file urls.txt
```

### Scrape from RSS Feeds

```bash
# Scrape from a single feed
python -m src.cli scrape-rss --feed https://example.com/rss

# Scrape from multiple feeds with limit
python -m src.cli scrape-rss --feed https://example.com/rss1 --feed https://example.com/rss2 --max 20

# Scrape from a file of feeds
python -m src.cli scrape-rss --file feeds.txt --max 15
```

### Scrape from Sitemaps

```bash
# Scrape from sitemap
python -m src.cli scrape-sitemap --sitemap https://example.com/sitemap.xml

# Scrape from multiple sitemaps
python -m src.cli scrape-sitemap --file sitemaps.txt --max 20
```

### List and Manage Articles

```bash
# List collected articles
python -m src.cli list --limit 50

# Filter by source
python -m src.cli list --source web_article_rss

# Show statistics
python -m src.cli stats

# Process articles to IdeaInspiration format
python -m src.cli process --limit 100 --output ideas.json

# Clear database
python -m src.cli clear
```

## Architecture

```
WebArticles/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database wrapper
│   │   ├── db_utils.py           # Database utilities
│   │   ├── metrics.py            # Universal metrics
│   │   └── idea_processor.py    # IdeaInspiration transformer
│   └── plugins/
│       ├── __init__.py           # Plugin base class
│       ├── article_url.py        # URL scraping plugin
│       ├── article_rss.py        # RSS feed plugin
│       └── article_sitemap.py   # Sitemap plugin
├── _meta/
│   ├── tests/                    # Unit tests
│   └── docs/                     # Documentation
├── requirements.txt              # Dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Data Model

Articles are stored with the following structure:

```python
{
    'source': 'web_article',
    'source_id': 'url_hash',
    'title': 'Article Title',
    'description': 'Article summary',
    'content': 'Full article text',
    'tags': 'tag1,tag2,tag3',
    'author': 'Author Name',
    'url': 'https://example.com/article',
    'published_at': '2025-01-01T00:00:00',
    'score': 8.5,  # Quality score
    'score_dictionary': {
        'word_count': 1200,
        'reading_time_min': 6,
        'quality_score': 8.5,
        'freshness_score': 0.95,
        'engagement_rate': 3.2,
        'social_score': 7.5
    }
}
```

## Dependencies

Core libraries:
- **trafilatura**: Article text extraction (primary)
- **newspaper3k**: Article extraction (fallback)
- **feedparser**: RSS/Atom feed parsing
- **beautifulsoup4**: HTML parsing
- **requests**: HTTP requests
- **sqlalchemy**: Database management
- **click**: CLI framework

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../Scoring/)** - Content scoring

## Configuration

Environment variables (in `.env`):

```bash
# Database
DATABASE_URL=sqlite:///web_articles.s3db

# Scraping settings
WEB_ARTICLE_MAX_ARTICLES=10
WEB_ARTICLE_TIMEOUT=30
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Working directory
WORKING_DIRECTORY=/path/to/PrismQ_WD
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
