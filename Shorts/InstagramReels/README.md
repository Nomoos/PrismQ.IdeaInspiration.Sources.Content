# Instagram Reels Source Module

**Platform-optimized Instagram Reels scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping Instagram Reels content with comprehensive metadata extraction and universal metrics collection. Built following SOLID principles for maintainability and extensibility.

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
- All Instagram plugins can substitute `SourcePlugin`

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
InstagramReels/
├── src/
│   ├── __init__.py                 # Main module exports
│   ├── cli.py                      # Command-line interface
│   ├── core/                       # Core utilities (SRP)
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── db_utils.py             # Database utilities
│   │   ├── metrics.py              # Universal metrics calculation
│   │   └── idea_processor.py      # IdeaInspiration transformation
│   └── plugins/                    # Scraper plugins (OCP, LSP, ISP)
│       ├── __init__.py             # SourcePlugin base class
│       ├── instagram_explore.py    # Explore/trending scraper
│       ├── instagram_hashtag.py    # Hashtag scraper
│       └── instagram_creator.py    # Creator profile scraper
├── _meta/                          # Module metadata
│   ├── docs/                       # Documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   └── tests/                      # Unit and integration tests
├── requirements.txt                # Python dependencies
├── module.json                     # Module configuration
├── .env.example                    # Environment configuration template
└── README.md                       # This file
```

## Features

### Scraping Modes

1. **Explore/Trending Scraping** (`src/plugins/instagram_explore.py`)
   - Scrapes from Instagram explore page
   - Discovers viral and trending content
   - No specific targeting required

2. **Hashtag-Based Scraping** (`src/plugins/instagram_hashtag.py`)
   - Search reels by hashtag
   - Targeted content discovery
   - Multiple hashtag support

3. **Creator Profile Scraping** (`src/plugins/instagram_creator.py`)
   - Scrape reels from specific creators
   - Track creator content
   - Analyze creator performance

### Key Capabilities

- **Comprehensive Metadata**: Caption, hashtags, location, audio, creator info
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **Engagement Analytics**: Plays, likes, comments, saves, shares
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
# Navigate to the InstagramReels module
cd Sources/Content/Shorts/InstagramReels

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (Instagram credentials if needed, database path, etc.)

# Run a scrape command
python -m src.cli scrape-hashtag --hashtag "reels"
```

## Usage

### Command Line Interface

```bash
# Explore/trending page scraping
python -m src.cli scrape-explore --max-reels 50

# Hashtag-based scraping
python -m src.cli scrape-hashtag --hashtag "startup" --max-reels 50

# Creator profile scraping
python -m src.cli scrape-creator --username "creator_username" --max-reels 50

# Process reels to IdeaInspiration format
python -m src.cli process

# View database statistics
python -m src.cli stats

# Export to JSON
python -m src.cli export --output reels.json --limit 100
```

### Python API

```python
from src import Config, Database, InstagramHashtagPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use a scraper plugin (Polymorphism via SourcePlugin)
plugin = InstagramHashtagPlugin(config)
reels = plugin.scrape(hashtag="startup")

# Process metrics
for reel in reels:
    metrics = UniversalMetrics.from_instagram(reel)
    print(f"Engagement rate: {metrics.engagement_rate}%")
    
    # Save to database
    db.insert_idea(
        source=plugin.get_source_name(),
        source_id=reel['source_id'],
        title=reel['title'],
        description=reel['description'],
        tags=plugin.format_tags(reel.get('tags', [])),
        score=metrics.engagement_rate or 0.0,
        score_dictionary=metrics.to_dict()
    )
```

## Configuration

Configuration is managed through `.env` file. See `.env.example` for all available options:

```bash
# Database Configuration
DATABASE_PATH=./instagram_reels.db

# Instagram Scraping Settings
INSTAGRAM_MAX_REELS=50
INSTAGRAM_EXPLORE_MAX_REELS=50
INSTAGRAM_HASHTAG_MAX_REELS=50
INSTAGRAM_CREATOR_MAX_REELS=50

# Instagram Authentication (Optional)
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=

# Reel Constraints
MAX_REEL_DURATION=90
```

## Data Model

Each reel is stored with the following structure:

```python
{
    'source': 'instagram_reels',
    'source_id': 'reel_shortcode',
    'title': 'Caption text',
    'description': 'Full caption with hashtags',
    'tags': ['hashtag1', 'hashtag2'],
    'creator': {
        'username': 'creator_username',
        'followers': 50000,
        'verified': False
    },
    'metrics': {
        'plays': 500000,
        'likes': 25000,
        'comments': 1000,
        'saves': 500,
        'shares': 200
    },
    'reel': {
        'duration': 25,
        'audio': 'Original audio - username',
        'location': 'City, Country',
        'filters': []
    },
    'universal_metrics': {
        'engagement_rate': 5.2,
        'plays_per_hour': 5000,
        'viral_velocity': 7.8
    }
}
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest _meta/tests/

# Run with coverage
pytest --cov=src --cov-report=html _meta/tests/

# Run specific test file
pytest _meta/tests/test_instagram_hashtag.py -v
```

## Design Patterns Used

1. **Abstract Factory Pattern**: `SourcePlugin` as factory interface
2. **Strategy Pattern**: Different scraping strategies via plugins
3. **Dependency Injection**: Config and Database injected into components
4. **Repository Pattern**: Database abstraction for data access
5. **Builder Pattern**: Config builder for environment setup

## Integration with PrismQ Ecosystem

This module integrates with:

- **PrismQ.IdeaInspiration.Model** - Data model for IdeaInspiration
- **PrismQ.IdeaInspiration.Classification** - Content classification
- **PrismQ.IdeaInspiration.Scoring** - Content scoring

Use `IdeaProcessor` to transform scraped data to the standardized format.

## Important Notes

### Instagram API Limitations

- Instagram has strict rate limiting and anti-bot measures
- Authentication may be required for full access
- Respect Instagram's Terms of Service and robots.txt
- Be cautious with scraping frequency to avoid account restrictions
- Consider using official Instagram API when available

### Scraping Best Practices

- Use reasonable delays between requests
- Limit scraping frequency
- Respect rate limits
- Don't scrape excessively from a single account
- Store session data securely
- Handle CAPTCHAs and errors gracefully

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See `_meta/docs/` directory
- **Issues**: Report via GitHub Issues
- **Contributing**: Follow SOLID principles and existing patterns

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
