# SpotifyPodcasts Source Module

**Spotify podcasts scraper for PrismQ.IdeaInspiration**

## Overview

This module provides tools for scraping podcast episodes from Spotify with comprehensive metadata extraction. It supports trending podcasts, category-based discovery, and show-specific scraping.

## Features

- **Trending Podcasts**: Scrape popular podcast episodes
- **Category Discovery**: Find podcasts by category (business, comedy, true crime, etc.)
- **Show Episodes**: Scrape episodes from specific podcast shows
- **Comprehensive Metadata**: Episode info, duration, release date, show details
- **Deduplication**: Prevents duplicate entries
- **SQLite Storage**: Persistent storage with complete metadata
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites

- Python 3.10 or higher
- Spotify Developer Account (for API credentials)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get Spotify API credentials:
   - Visit https://developer.spotify.com/dashboard
   - Create a new app
   - Copy Client ID and Client Secret

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your Spotify credentials
```

## Usage

### Scrape Trending Episodes

```bash
python -m SpotifyPodcasts scrape-trending
python -m SpotifyPodcasts scrape-trending --top 20 --market GB
```

### Scrape by Category

```bash
python -m SpotifyPodcasts scrape-category --category "business"
python -m SpotifyPodcasts scrape-category --category "true crime" --top 15
```

### Scrape Specific Show

```bash
python -m SpotifyPodcasts scrape-show --show-id "4rOoJ6Egrf8K2IrywzwOMk"
python -m SpotifyPodcasts scrape-show --show-id "spotify:show:4rOoJ6Egrf8K2IrywzwOMk" --top 20
```

### List Collected Episodes

```bash
python -m SpotifyPodcasts list
python -m SpotifyPodcasts list --limit 50
python -m SpotifyPodcasts list --source spotify_trending
```

### View Statistics

```bash
python -m SpotifyPodcasts stats
```

### Process to IdeaInspiration Format

```bash
python -m SpotifyPodcasts process
python -m SpotifyPodcasts process --limit 10 --output ideas.json
```

## Architecture

```
SpotifyPodcasts/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database wrapper
│   │   ├── db_utils.py           # Database utilities
│   │   ├── metrics.py            # Universal metrics
│   │   └── idea_processor.py    # IdeaInspiration transformer
│   └── plugins/
│       ├── spotify_trending.py   # Trending podcasts plugin
│       ├── spotify_category.py   # Category-based plugin
│       └── spotify_show.py       # Show-specific plugin
├── _meta/
│   └── tests/                    # Test suite
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── module.json                   # Module metadata
└── README.md                     # This file
```

## Data Model

```python
{
    'source': 'spotify_podcasts',
    'source_id': 'episode_id',
    'title': 'Episode title',
    'description': 'Episode description',
    'tags': ['category', 'show_name', 'publisher'],
    'show': {
        'name': 'Show Name',
        'publisher': 'Publisher',
        'total_episodes': 100
    },
    'metrics': {
        'duration_ms': 3600000,
        'release_date': '2025-01-15',
        'language': 'en',
        'explicit': False
    },
    'universal_metrics': {
        'engagement_estimate': 5.0
    }
}
```

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../../../Scoring/)** - Content scoring

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See module documentation
- **Issues**: Report via GitHub Issues

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
