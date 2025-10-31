# ApplePodcastsSource

**Apple Podcasts scraper for PrismQ.IdeaInspiration - Collect podcast episodes and metadata**

## Overview

ApplePodcastsSource is a comprehensive scraper for collecting podcast episodes, metadata, and trending shows from Apple Podcasts. It uses the iTunes Search API to gather episode information, ratings, and engagement metrics.

## Features

- **Chart Scraping**: Get trending podcasts from Apple Podcasts charts
- **Category-Based Discovery**: Scrape podcasts by category or genre
- **Show-Based Scraping**: Get episodes from specific podcast shows
- **Comprehensive Metadata**: Ratings, reviews, duration, release dates
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **SQLite Storage**: Persistent storage with deduplication
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- Internet connection for API access

### Quick Start

```bash
# Navigate to the ApplePodcasts module
cd Sources/Content/Podcasts/ApplePodcasts

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (optional, defaults provided)
```

## Usage

### Command Line Interface

```bash
# Scrape from charts (trending podcasts)
python -m src.cli scrape-charts

# Scrape from charts with specific genre
python -m src.cli scrape-charts --genre comedy --top 10

# Scrape from category
python -m src.cli scrape-category --category "true crime" --top 15

# Scrape from specific show
python -m src.cli scrape-show --show "The Daily" --top 20
python -m src.cli scrape-show --show 1200361736 --top 10

# List collected episodes
python -m src.cli list --limit 20

# Show statistics
python -m src.cli stats

# Process unprocessed records to IdeaInspiration format
python -m src.cli process --limit 100 --output processed.json

# Clear database
python -m src.cli clear
```

### Python API

```python
from src.core.config import Config
from src.core.database import Database
from src.plugins.apple_charts import AppleChartsPlugin

# Initialize
config = Config()
db = Database(config.database_path)

# Scrape from charts
plugin = AppleChartsPlugin(config)
ideas = plugin.scrape_charts(genre='technology', top_n=10)

# Save to database
for idea in ideas:
    db.insert_idea(**idea)
```

## Configuration

Configuration is managed through environment variables in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database URL | `sqlite:///db.s3db` |
| `APPLE_PODCASTS_MAX_EPISODES` | Max episodes per show | `10` |
| `APPLE_PODCASTS_MAX_SHOWS` | Max shows from charts | `20` |
| `APPLE_PODCASTS_REGION` | Region code (us, gb, ca) | `us` |

## Data Model

Each episode is stored with the following structure:

```python
{
    'source': 'apple_podcasts',
    'source_id': 'episode_track_id',
    'title': 'Episode title',
    'description': 'Episode description',
    'tags': ['genre1', 'show_name'],
    'metrics': {
        'rating': 4.8,
        'rating_count': 1000,
        'duration_ms': 3600000,
        'release_date': '2025-01-15',
        'show': {
            'name': 'Show Name',
            'artist': 'Creator',
            'rating': 4.8
        },
        'engagement_estimate': 96.0
    }
}
```

## Architecture

```
ApplePodcasts/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database wrapper
│   │   ├── db_utils.py          # Database utilities
│   │   ├── metrics.py           # Universal metrics
│   │   ├── idea_processor.py   # IdeaInspiration processor
│   │   └── logging_config.py   # Logging setup
│   └── plugins/
│       ├── apple_charts.py      # Charts scraping
│       ├── apple_category.py   # Category scraping
│       └── apple_show.py        # Show scraping
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── module.json                  # Module metadata
```

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../../Scoring/)** - Content scoring

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Testing

```bash
# Run tests (when available)
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## API Reference

### iTunes Search API

This module uses the iTunes Search API, which has the following characteristics:

- **No API Key Required**: Free to use
- **Rate Limits**: Reasonable use, no hard limits documented
- **Endpoints**:
  - Search: `https://itunes.apple.com/search`
  - Lookup: `https://itunes.apple.com/lookup`

### Genres

Available podcast genres for filtering:
- arts, business, comedy, education, fiction
- government, health, history, kids, leisure
- music, news, religion, science, society
- sports, technology, true_crime, tv

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [_meta/docs/](_meta/docs/) directory
- **Issues**: Report via GitHub Issues

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
