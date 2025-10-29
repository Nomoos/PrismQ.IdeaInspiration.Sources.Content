# YouTube Shorts Source Module

**Platform-optimized YouTube Shorts scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping YouTube Shorts content with comprehensive metadata extraction and universal metrics collection. It has been reorganized following SOLID principles for better maintainability and extensibility.

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
- All YouTube plugins (`YouTubePlugin`, `YouTubeChannelPlugin`, `YouTubeTrendingPlugin`) can substitute `SourcePlugin`

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
YouTube/
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
│       ├── youtube_plugin.py       # YouTube API scraper
│       ├── youtube_channel_plugin.py  # Channel-based scraper
│       └── youtube_trending_plugin.py # Trending page scraper
├── tests/                          # Unit and integration tests
├── _meta/                          # Module metadata
│   ├── docs/                       # Comprehensive documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   └── research/                   # Research and experiments
├── scripts/                        # Utility scripts
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package configuration
├── .env.example                    # Environment configuration template
└── README.md                       # This file
```

## Features

### Scraping Modes

1. **YouTube API Search** (`src/plugins/youtube_plugin.py`)
   - Uses YouTube Data API v3
   - Search-based scraping with keywords
   - Requires API key (quota limited)

2. **Channel-Based Scraping** (`src/plugins/youtube_channel_plugin.py`)
   - Uses yt-dlp for channel scraping
   - No API quota limits
   - Rich metadata including subtitles
   - Engagement analytics

3. **Trending Scraping** (`src/plugins/youtube_trending_plugin.py`)
   - Scrapes from YouTube trending page
   - No API key required
   - Discovery of viral content

### Key Capabilities

- **Comprehensive Metadata**: Title, description, tags, statistics, channel info
- **Subtitle Extraction**: Automatic subtitle download and parsing
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **Engagement Analytics**: Views per day/hour, engagement rates, ratios
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
# Navigate to the YouTube module
cd Sources/Content/Shorts/YouTube

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (YouTube API key, database path, etc.)

# Run a scrape command
python -m src.cli scrape-channel --channel-url "https://youtube.com/@channel"
```

## Usage

### Command Line Interface

```bash
# YouTube API search (legacy - quota limited)
python -m src.cli scrape

# Channel-based scraping (recommended)
python -m src.cli scrape-channel --channel-url "https://youtube.com/@channel"

# Trending page scraping
python -m src.cli scrape-trending --max-results 50

# Keyword search
python -m src.cli scrape-keyword --query "startup ideas"

# Process ideas to IdeaInspiration format
python -m src.cli process

# View database statistics
python -m src.cli stats

# Export to JSON
python -m src.cli export --output ideas.json
```

### Python API

```python
from src import Config, Database, YouTubeChannelPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use a scraper plugin (Polymorphism via SourcePlugin)
plugin = YouTubeChannelPlugin(config)
ideas = plugin.scrape()

# Process metrics
for idea in ideas:
    metrics = UniversalMetrics.from_youtube(idea['metrics'])
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
# YouTube API Configuration
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_MAX_RESULTS=50

# Database Configuration
DATABASE_PATH=./youtube_shorts.db

# Scraping Configuration  
MAX_VIDEO_LENGTH=180  # 3 minutes for Shorts
MIN_ASPECT_RATIO=0.5  # Vertical format validation

# Working Directory
WORKING_DIR=./
```

See [_meta/docs/CONFIGURATION.md](_meta/docs/CONFIGURATION.md) for detailed configuration guide.

## Documentation

- **[Configuration Guide](_meta/docs/CONFIGURATION.md)** - Working directories, .env management
- **[Metrics Documentation](_meta/docs/METRICS.md)** - Universal metrics system
- **[YouTube Data Model](_meta/docs/YTB_DATA_MODEL.md)** - Complete database schema
- **[Data Collection Guide](_meta/docs/DATA_COLLECTION_GUIDE.md)** - What data we collect
- **[Scraping Best Practices](_meta/docs/SCRAPING_BEST_PRACTICES.md)** - Safety and re-scraping
- **[Windows Quickstart](_meta/docs/WINDOWS_QUICKSTART.md)** - Windows-specific setup
- **[Contributing](_meta/docs/CONTRIBUTING.md)** - How to contribute

For a complete list of documentation, see [_meta/docs/](_meta/docs/).

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_youtube_channel_plugin.py -v
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

## Performance Considerations

- **API Rate Limiting**: YouTube API has daily quota limits (use yt-dlp alternatives)
- **Batch Processing**: Process ideas in batches to minimize database writes
- **Caching**: Config and database connections are reused
- **Memory Management**: Large datasets are processed iteratively

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report via GitHub Issues
- **Contributing**: See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
