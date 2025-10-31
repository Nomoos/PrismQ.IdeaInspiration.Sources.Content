# TikTok Source Module

**Platform-optimized TikTok scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping TikTok content with comprehensive metadata extraction and universal metrics collection. It follows SOLID principles for better maintainability and extensibility.

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
- All TikTok plugins (`TikTokTrendingPlugin`, `TikTokHashtagPlugin`, `TikTokCreatorPlugin`) can substitute `SourcePlugin`

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
TikTok/
├── src/
│   ├── __init__.py                 # Main module exports
│   ├── cli.py                      # Command-line interface
│   ├── core/                       # Core utilities (SRP)
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database wrapper
│   │   ├── db_utils.py             # Database utilities
│   │   ├── metrics.py              # Universal metrics calculation
│   │   └── idea_processor.py      # IdeaInspiration transformation
│   └── plugins/                    # Scraper plugins (OCP, LSP, ISP)
│       ├── __init__.py             # SourcePlugin base class
│       ├── tiktok_trending.py      # Trending scraper
│       ├── tiktok_hashtag.py       # Hashtag scraper
│       └── tiktok_creator.py       # Creator scraper
├── tests/                          # Unit and integration tests
├── _meta/                          # Module metadata
│   ├── docs/                       # Comprehensive documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   └── research/                   # Research and experiments
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package configuration
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore patterns
└── README.md                       # This file
```

## Features

### Scraping Modes

1. **Trending Scraping** (`src/plugins/tiktok_trending.py`)
   - Scrapes from TikTok trending page
   - Discovers viral content
   - No API key required (when properly implemented)

2. **Hashtag-Based Scraping** (`src/plugins/tiktok_hashtag.py`)
   - Search by hashtags/challenges
   - Track trending sounds and challenges
   - Hashtag analytics

3. **Creator Channel Scraping** (`src/plugins/tiktok_creator.py`)
   - Scrapes from specific creator profiles
   - Creator analytics
   - Video history analysis

### Key Capabilities

- **Comprehensive Metadata**: Title, description, hashtags, music, effects
- **Creator Information**: Username, follower count, verification status
- **Engagement Metrics**: Views, likes, shares, comments, saves
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **Engagement Analytics**: Engagement rate, views per day/hour, viral velocity
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
# Navigate to the TikTok module
cd Sources/Content/Shorts/TikTok

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (Database path, scraping limits, etc.)

# Run a scrape command
python -m src.cli scrape-trending --max-videos 10
```

## Usage

### Command Line Interface

```bash
# Trending page scraping
python -m src.cli scrape-trending --max-videos 20

# Hashtag search
python -m src.cli scrape-hashtag --hashtag startup --max-videos 15

# Creator channel scraping
python -m src.cli scrape-creator --username creator123 --max-videos 10

# Process ideas to IdeaInspiration format
python -m src.cli process

# View database statistics
python -m src.cli stats

# Export to JSON
python -m src.cli export --output tiktok_ideas.json
```

### Python API

```python
from src import Config, Database, TikTokTrendingPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use a scraper plugin (Polymorphism via SourcePlugin)
plugin = TikTokTrendingPlugin(config)
ideas = plugin.scrape()

# Process metrics
for idea in ideas:
    metrics = UniversalMetrics.from_tiktok(idea['metrics'])
    print(f"Engagement rate: {metrics.engagement_rate}%")
    
    # Save to database with universal metrics
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
DATABASE_URL=sqlite:///tiktok.s3db

# TikTok Trending Configuration
TIKTOK_TRENDING_MAX=10

# TikTok Hashtag Configuration
TIKTOK_HASHTAG=startup
TIKTOK_HASHTAG_MAX=10

# TikTok Creator Configuration
TIKTOK_CREATOR_USERNAME=
TIKTOK_CREATOR_MAX=10

# Rate Limiting
TIKTOK_RATE_LIMIT_DELAY=2

# Working Directory (auto-configured)
WORKING_DIRECTORY=
```

## Implementation Status

⚠️ **Note**: This module provides the complete architecture and infrastructure for TikTok scraping. However, the actual scraping implementation requires additional setup:

### Next Steps for Full Implementation

1. **Choose a TikTok Scraping Library**:
   - TikTokApi (unofficial Python library)
   - playwright-based scraping
   - Other community solutions

2. **Implement Scraping Methods**:
   - Update `_fetch_trending_videos()` in `tiktok_trending.py`
   - Update `_fetch_hashtag_videos()` in `tiktok_hashtag.py`
   - Update `_fetch_creator_videos()` in `tiktok_creator.py`

3. **Add Authentication** (if needed):
   - Handle TikTok login/sessions
   - Manage cookies and tokens

4. **Implement Rate Limiting**:
   - Add delays between requests
   - Implement retry logic
   - Handle anti-scraping measures

### API/Scraping Considerations

- TikTok API has strict rate limits
- Consider unofficial libraries for scraping
- Respect robots.txt and ToS
- Implement proper rate limiting
- Handle anti-scraping measures (rotating IPs, user agents)

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_config.py -v
```

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
- **Contributing**: See CONTRIBUTING.md

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
