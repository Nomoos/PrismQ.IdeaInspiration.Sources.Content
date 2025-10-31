# PrismQ Medium Articles Source

**Platform-optimized article scraper for Medium.com with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping article content from Medium.com with comprehensive metadata extraction. It supports multiple scraping methods including trending articles, tag-based discovery, publication scraping, and author profiles.

## Features

### Scraping Methods
- **Trending Articles** - Discover trending articles across Medium
- **Tag-Based Search** - Find articles by specific tags
- **Publication Scraping** - Collect articles from Medium publications
- **Author Profiles** - Scrape articles from specific authors

### Data Collection
- Article metadata (title, subtitle, content, tags, reading time)
- Author information (username, followers when available)
- Engagement metrics (claps, responses)
- Full article text extraction
- Universal metrics normalization

### Key Capabilities
- **Comprehensive Metadata**: Title, author, tags, read time, claps, responses
- **Engagement Analytics**: Claps per day, viral velocity, engagement rate
- **Content Extraction**: Full article text and structure
- **Deduplication**: Prevents duplicate entries in database
- **SQLite Storage**: Persistent storage with complete metadata
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the Medium module
cd Sources/Content/Articles/Medium

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (optional, defaults will be used)
```

## Usage

### Scrape Trending Articles

```bash
# Scrape 10 trending articles (default)
python -m src.cli scrape-trending

# Scrape 20 trending articles
python -m src.cli scrape-trending --top 20
```

### Scrape Articles by Tag

```bash
# Scrape articles with a specific tag
python -m src.cli scrape-tag --tag "artificial-intelligence"

# Scrape 15 articles with tag
python -m src.cli scrape-tag --tag "startup" --top 15
```

### Scrape Articles from Publication

```bash
# Scrape from a Medium publication
python -m src.cli scrape-publication --publication "towards-data-science"

# Scrape with custom limit
python -m src.cli scrape-publication --publication "better-programming" --top 20
```

### Scrape Articles by Author

```bash
# Scrape from an author's profile
python -m src.cli scrape-author --author "@username"

# Alternative without @
python -m src.cli scrape-author --author "username" --top 15
```

### List Collected Ideas

```bash
# List all ideas (last 20)
python -m src.cli list

# List with custom limit
python -m src.cli list --limit 50

# Filter by source
python -m src.cli list --source medium_trending
```

### View Statistics

```bash
# Show collection statistics
python -m src.cli stats
```

### Process to IdeaInspiration Format

```bash
# Process all unprocessed records
python -m src.cli process

# Process with limit
python -m src.cli process --limit 10

# Save processed ideas to JSON
python -m src.cli process --output ideas.json
```

### Clear Database

```bash
# Clear all collected ideas (requires confirmation)
python -m src.cli clear
```

## Configuration

Configuration is managed through the `.env` file. Key settings:

```env
# Database
DATABASE_URL=sqlite:///db.s3db

# Scraping Limits
MEDIUM_TRENDING_MAX_ARTICLES=10
MEDIUM_TAG_MAX_ARTICLES=10
MEDIUM_AUTHOR_MAX_ARTICLES=10
MEDIUM_PUBLICATION_MAX_ARTICLES=10

# Request Settings
REQUEST_TIMEOUT=30
REQUEST_DELAY=1
```

## Architecture

```
Medium/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database wrapper
│   │   ├── db_utils.py           # Database utilities
│   │   ├── metrics.py            # Universal metrics
│   │   ├── logging_config.py     # Logging configuration
│   │   └── idea_processor.py     # IdeaInspiration processor
│   └── plugins/
│       ├── __init__.py           # Plugin base class
│       ├── medium_trending.py    # Trending scraper
│       ├── medium_tag.py         # Tag-based scraper
│       ├── medium_publication.py # Publication scraper
│       └── medium_author.py      # Author scraper
├── _meta/                        # Metadata and tests
├── requirements.txt              # Dependencies
├── pyproject.toml                # Project configuration
├── module.json                   # Module metadata
└── README.md                     # This file
```

## Data Model

Articles are stored with comprehensive metadata:

```python
{
    'source': 'medium',
    'source_id': 'article_id',
    'title': 'Article title',
    'description': 'Article subtitle and excerpt',
    'tags': 'tag1,tag2,topic',
    'author': {
        'username': 'author_name',
        'followers': 10000
    },
    'metrics': {
        'claps': 5000,
        'responses': 50,
        'reading_time_min': 8
    },
    'universal_metrics': {
        'engagement_rate': 1.0,
        'claps_per_day': 500,
        'viral_velocity': 6.5
    }
}
```

## Integration with PrismQ Ecosystem

This module integrates with:
- **[PrismQ.IdeaInspiration.Model](../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../Scoring/)** - Content scoring

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Notes

- **Web Scraping**: This module uses web scraping as Medium doesn't provide an official API for content discovery
- **Rate Limiting**: Respect Medium's servers with appropriate delays between requests
- **Reliability**: Medium's HTML structure may change; selectors may need updates
- **Completeness**: Some metrics (like exact view counts) are not publicly available

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [_meta/docs/](_meta/docs/) directory
- **Issues**: Report via GitHub Issues

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
