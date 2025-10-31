# Twitch Clips Source Module

**Platform-optimized Twitch Clips scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping Twitch clips with comprehensive metadata extraction and universal metrics collection. It follows SOLID principles for better maintainability and extensibility, mirroring the architecture established in the YouTube Shorts source.

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
- All Twitch plugins (`TwitchTrendingPlugin`, `TwitchGamePlugin`, `TwitchStreamerPlugin`) can substitute `SourcePlugin`

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
TwitchClips/
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
│       ├── twitch_trending_plugin.py  # Trending clips scraper
│       ├── twitch_game_plugin.py      # Game/category scraper
│       └── twitch_streamer_plugin.py  # Streamer channel scraper
├── tests/                          # Unit and integration tests
├── _meta/                          # Module metadata
│   ├── docs/                       # Comprehensive documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   └── research/                   # Research and experiments
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Features

### Scraping Modes

1. **Trending Clips** (`src/plugins/twitch_trending_plugin.py`)
   - Scrapes most viewed clips from the last 24 hours
   - Uses Twitch Helix API
   - Requires OAuth authentication

2. **Game-Based Scraping** (`src/plugins/twitch_game_plugin.py`)
   - Scrapes clips filtered by game/category
   - Discovers trending content for specific games
   - Game-based content discovery

3. **Streamer-Based Scraping** (`src/plugins/twitch_streamer_plugin.py`)
   - Scrapes clips from specific streamers/channels
   - Creator-focused content collection
   - Channel-specific analytics

### Universal Metrics

All scraped clips are enriched with cross-platform metrics:

- **Engagement Metrics**: Views, likes, comments, shares
- **Performance Metrics**: Views per day/hour, engagement rate
- **Content Metadata**: Duration, language, game/category
- **Creator Info**: Broadcaster, creator, partner status
- **Contextual Data**: VOD offset, timestamp, game context

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Configuration

The module uses a `.env` file for configuration. Create one in your PrismQ_WD directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///db.s3db

# Twitch API Credentials (from https://dev.twitch.tv/console/apps)
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_CLIENT_SECRET=your_client_secret_here

# Scraping Configuration
TWITCH_TRENDING_MAX_CLIPS=10
TWITCH_GAME_NAME=League of Legends
TWITCH_GAME_MAX_CLIPS=10
TWITCH_STREAMER_NAME=ninja
TWITCH_STREAMER_MAX_CLIPS=10
```

### Getting Twitch API Credentials

1. Go to https://dev.twitch.tv/console/apps
2. Register a new application
3. Copy the Client ID and Client Secret
4. Add them to your `.env` file

## Usage

### Command Line Interface

#### Scrape Trending Clips

```bash
# Scrape trending clips (uses config defaults)
python -m Sources.Content.Shorts.TwitchClips scrape-trending

# Scrape specific number of clips
python -m Sources.Content.Shorts.TwitchClips scrape-trending --top-n 20

# Use custom .env file
python -m Sources.Content.Shorts.TwitchClips scrape-trending --env-file /path/to/.env
```

#### Scrape by Game/Category

```bash
# Scrape clips for a specific game
python -m Sources.Content.Shorts.TwitchClips scrape-game --game "League of Legends" --top-n 15

# Use configured game
python -m Sources.Content.Shorts.TwitchClips scrape-game
```

#### Scrape by Streamer

```bash
# Scrape clips from a specific streamer
python -m Sources.Content.Shorts.TwitchClips scrape-streamer --streamer ninja --top-n 20

# Use configured streamer
python -m Sources.Content.Shorts.TwitchClips scrape-streamer
```

#### List Stored Ideas

```bash
# List all ideas
python -m Sources.Content.Shorts.TwitchClips list-ideas

# List specific number of ideas
python -m Sources.Content.Shorts.TwitchClips list-ideas --limit 20

# Filter by source
python -m Sources.Content.Shorts.TwitchClips list-ideas --source twitch_clips
```

### Python API

```python
from Sources.Content.Shorts.TwitchClips.src.core.config import Config
from Sources.Content.Shorts.TwitchClips.src.core.database import Database
from Sources.Content.Shorts.TwitchClips.src.plugins.twitch_trending_plugin import TwitchTrendingPlugin

# Initialize
config = Config()
db = Database(config.database_path)

# Scrape trending clips
plugin = TwitchTrendingPlugin(config)
ideas = plugin.scrape(top_n=10)

# Save to database
for idea in ideas:
    db.insert_idea(
        source='twitch_clips',
        source_id=idea['source_id'],
        title=idea['title'],
        description=idea['description'],
        tags=idea['tags']
    )
```

## Data Model

### Clip Metadata

```python
{
    'source': 'twitch_clips',
    'source_id': 'clip_id',
    'title': 'Amazing Play!',
    'description': 'Twitch clip from Ninja\'s stream of Fortnite',
    'tags': 'Fortnite,Ninja,twitch,clip,gaming',
    'metrics': {
        'view_count': 100000,
        'duration': 30,
        'created_at': '2025-01-15T10:30:00Z',
        'broadcaster_name': 'Ninja',
        'game_name': 'Fortnite',
        'language': 'en',
        'vod_offset': 3600
    }
}
```

### Universal Metrics

```python
{
    'platform': 'twitch',
    'content_type': 'clip',
    'view_count': 100000,
    'duration_seconds': 30,
    'views_per_day': 5000,
    'views_per_hour': 208,
    'platform_specific': {
        'clip_id': 'abc123',
        'broadcaster_id': '123456',
        'broadcaster_name': 'Ninja',
        'game_id': '33214',
        'game_name': 'Fortnite',
        'language': 'en',
        'vod_offset': 3600
    }
}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

## API Rate Limits

- Twitch Helix API: 800 requests per minute
- OAuth token expires after ~60 days
- Automatic token refresh implemented

## Best Practices

1. **API Credentials**: Keep your Twitch credentials secure
2. **Rate Limiting**: The module respects Twitch API rate limits
3. **Error Handling**: All API calls have proper error handling
4. **Deduplication**: Database automatically prevents duplicate clips
5. **Metrics**: All clips are enriched with universal metrics for cross-platform analysis

## Contributing

See `_meta/docs/CONTRIBUTING.md` for contribution guidelines.

## License

See LICENSE file for details.

## Related Modules

- **YouTubeShortsSource**: YouTube Shorts scraper (similar architecture)
- **PrismQ.IdeaInspiration.Model**: Unified data model
- **PrismQ.IdeaInspiration.Classification**: Content classification

## Support

For issues, questions, or contributions:
- Open an issue in `_meta/issues/new/`
- Check existing issues in `_meta/issues/`
- Review documentation in `_meta/docs/`
