# Kick Clips Source Module

**Platform-optimized Kick clips scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping Kick clips content with comprehensive metadata extraction and universal metrics collection. It follows SOLID principles for better maintainability and extensibility.

Kick is a growing streaming platform and provides alternative content to Twitch. As a newer platform, content discovery may be easier with less saturation.

## Architecture (SOLID Principles)

The module follows SOLID design principles:

### Single Responsibility Principle (SRP)
- `Config`: Handles configuration management only
- `Database`: Manages database operations only
- `UniversalMetrics`: Calculates and normalizes metrics only
- `IdeaProcessor`: Transforms data to IdeaInspiration format only
- Each plugin handles one specific scraping source

### Open/Closed Principle (OCP)
- `SourcePlugin` is an abstract base class open for extension
- New scrapers can be added by extending `SourcePlugin` without modifying existing code

### Liskov Substitution Principle (LSP)
- All Kick plugins (`KickTrendingPlugin`, `KickCategoryPlugin`, `KickStreamerPlugin`) can substitute `SourcePlugin`

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
KickClips/
├── src/
│   ├── __init__.py                 # Main module exports
│   ├── cli.py                      # Command-line interface
│   ├── core/                       # Core utilities (SRP)
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── db_utils.py             # Database utilities
│   │   ├── logging_config.py       # Logging configuration
│   │   ├── metrics.py              # Universal metrics calculation
│   │   └── idea_processor.py      # IdeaInspiration transformation
│   └── plugins/                    # Scraper plugins (OCP, LSP, ISP)
│       ├── __init__.py             # SourcePlugin base class
│       ├── kick_trending.py        # Trending clips scraper
│       ├── kick_category.py        # Category-based scraper
│       └── kick_streamer.py        # Streamer channel scraper
├── _meta/                          # Module metadata
│   ├── docs/                       # Comprehensive documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   └── research/                   # Research and experiments
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package configuration
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Features

### Scraping Modes

1. **Trending Clips** (`src/plugins/kick_trending.py`)
   - Scrapes trending/featured clips
   - Discovers viral content
   - No authentication required

2. **Category-Based Scraping** (`src/plugins/kick_category.py`)
   - Scrapes clips from specific categories
   - Filter by game/topic
   - Targeted content discovery

3. **Streamer Channel Scraping** (`src/plugins/kick_streamer.py`)
   - Scrapes clips from specific streamers
   - Follow favorite creators
   - Channel-specific insights

### Key Capabilities

- **Comprehensive Metadata**: Title, description, category, streamer info
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **Engagement Analytics**: Views, likes, reactions, engagement rates
- **Deduplication**: Prevents duplicate entries using (source, source_id) constraint
- **SQLite Storage**: Persistent storage with complete metadata
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the KickClips module
cd Sources/Content/Streams/KickClips

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (Database path, scraping settings, etc.)

# Run a scrape command
python -m src.cli scrape-trending --max-clips 50
```

## Usage

### Command Line Interface

```bash
# Scrape trending clips
python -m src.cli scrape-trending --max-clips 50

# Scrape clips from a specific category
python -m src.cli scrape-category --category gaming --max-clips 30

# Scrape clips from a specific streamer
python -m src.cli scrape-streamer --streamer xqc --max-clips 20

# View database statistics
python -m src.cli stats

# Export to JSON (IdeaInspiration format)
python -m src.cli export --output ideas.json --limit 100
```

### Python API

```python
from src import Config, Database, KickTrendingPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use a scraper plugin (Polymorphism via SourcePlugin)
plugin = KickTrendingPlugin(config)
ideas = plugin.scrape(max_clips=50)

# Process metrics
for idea in ideas:
    metrics = UniversalMetrics.from_kick(idea['metrics'])
    print(f"Engagement rate: {metrics.engagement_rate}%")
    
    # Save to database
    db.insert_idea(
        source=plugin.get_source_name(),
        source_id=idea['source_id'],
        title=idea['title'],
        description=idea['description'],
        tags=idea['tags'],
        score=metrics.engagement_rate or 0.0,
        score_dictionary=metrics.to_dict()
    )
```

## Configuration

Configuration is managed through `.env` file. See `.env.example` for all available options:

```bash
# Database Configuration
DATABASE_URL=sqlite:///kick_clips.db

# Kick Scraping Configuration
KICK_TRENDING_MAX_CLIPS=50
KICK_CATEGORY_MAX_CLIPS=50
KICK_STREAMER_MAX_CLIPS=50

# Scraping Behavior
REQUEST_DELAY=1.0          # Delay between requests (seconds)
MAX_RETRIES=3              # Maximum retries for failed requests
REQUEST_TIMEOUT=30         # Timeout for HTTP requests (seconds)
```

## Data Model

### Kick Clip Data Structure

```python
{
    'source': 'kick_clips',
    'source_id': 'clip_id',
    'title': 'Clip title',
    'description': 'Category and streamer info',
    'tags': ['category', 'streamer'],
    'streamer': {
        'username': 'streamer_name',
        'followers': 10000,
        'verified': False
    },
    'category': {
        'name': 'Category Name',
        'id': 'category_id'
    },
    'metrics': {
        'views': 50000,
        'reactions': 200,
        'likes': 200,
        'comments': 0,
        'shares': 0
    },
    'clip': {
        'duration': 45,
        'language': 'en',
        'created_at': '2025-01-15T10:30:00Z'
    },
    'universal_metrics': {
        'engagement_rate': 0.4,
        'views_per_hour': 500,
        'viral_velocity': 5.5
    }
}
```

## API/Scraping Approach

This module uses the unofficial Kick API:

- **Base URL**: `https://kick.com/api/v2`
- **Cloudflare Bypass**: Uses `cloudscraper` library
- **Rate Limiting**: Configurable delays between requests
- **Error Handling**: Automatic retries with exponential backoff

**Note**: Since Kick doesn't have an official public API, this implementation:
- Uses reverse-engineered endpoints
- May break if Kick updates their API
- Respects rate limits to avoid IP blocks
- Follows ethical scraping practices

## Design Patterns Used

1. **Abstract Factory Pattern**: `SourcePlugin` as factory interface
2. **Strategy Pattern**: Different scraping strategies via plugins
3. **Dependency Injection**: Config and Database injected into components
4. **Repository Pattern**: Database abstraction for data access
5. **Builder Pattern**: Config builder for environment setup

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../Scoring/)** - Content scoring

Use `IdeaProcessor` to transform scraped data to the standardized format.

## Performance Considerations

- **Rate Limiting**: Configurable delays prevent IP blocks
- **Batch Processing**: Process ideas in batches to minimize database writes
- **Caching**: Config and database connections are reused
- **Memory Management**: Large datasets are processed iteratively
- **Cloudflare Bypass**: Uses cloudscraper for reliable access

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Troubleshooting

### Common Issues

1. **Cloudflare Blocking**: If you get blocked, try:
   - Increasing `REQUEST_DELAY`
   - Using a VPN
   - Waiting before retrying

2. **Empty Results**: If scraping returns no clips:
   - Verify the category/streamer exists
   - Check if Kick's API structure changed
   - Enable debug logging

3. **Database Errors**: If you encounter database issues:
   - Ensure write permissions for database file
   - Check disk space
   - Verify SQLite is properly installed

## Contributing

See [_meta/docs/CONTRIBUTING.md](_meta/docs/CONTRIBUTING.md) for contribution guidelines.

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [_meta/docs/](_meta/docs/) directory
- **Issues**: Report via GitHub Issues

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
