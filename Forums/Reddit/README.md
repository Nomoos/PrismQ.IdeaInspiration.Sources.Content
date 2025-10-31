# PrismQ Reddit Source

**Collect idea inspirations from Reddit** - trending posts, community discussions, and viral content.

Part of the [PrismQ.IdeaInspiration](https://github.com/Nomoos/PrismQ.IdeaInspiration) ecosystem for AI-powered content generation.

## Features

- 🔥 **Trending Posts**: Scrape from r/all and r/popular
- 🎯 **Subreddit-Specific**: Target specific communities
- 📈 **Rising Discovery**: Find posts gaining traction
- 🔍 **Keyword Search**: Search by topics and keywords
- 📊 **Universal Metrics**: Cross-platform engagement analytics
- 💾 **SQLite Storage**: Automatic deduplication
- 🔄 **IdeaInspiration Format**: Transform to standardized model

## Installation

### Prerequisites

- Python 3.8+
- Reddit API credentials ([Get them here](https://www.reddit.com/prefs/apps))

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration/Sources/Content/Forums/Reddit
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Reddit API**:
   - Create a Reddit app at https://www.reddit.com/prefs/apps
   - Click "create another app..." or "create app"
   - Select "script" as the app type
   - Copy the client ID and secret
   - Copy `.env.example` to `.env` and add your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=PrismQ.IdeaInspiration:Reddit:v1.0.0 (by /u/yourusername)
   ```

## Usage

### Scrape Trending Posts

```bash
# Scrape from r/all
python -m src.cli scrape-trending

# Scrape from specific subreddit
python -m src.cli scrape-trending --subreddit python --top 20

# Scrape from r/popular
python -m src.cli scrape-trending -s popular -t 15
```

### Scrape Specific Subreddit

```bash
# Scrape hot posts
python -m src.cli scrape-subreddit --subreddit startup

# Scrape top posts of the day
python -m src.cli scrape-subreddit -s entrepreneur --sort top --top 20

# Scrape new posts
python -m src.cli scrape-subreddit -s technology --sort new
```

### Scrape Rising Posts

```bash
# Find posts gaining traction (viral potential)
python -m src.cli scrape-rising

# From specific subreddit
python -m src.cli scrape-rising --subreddit Futurology --top 15
```

### Search by Keywords

```bash
# Search all of Reddit
python -m src.cli scrape-search --query "startup ideas"

# Search specific subreddit
python -m src.cli scrape-search -q "AI tools" -s artificial --top 20

# Sort by relevance, hot, top, new, or comments
python -m src.cli scrape-search -q "productivity" --sort top
```

### View Collected Posts

```bash
# List all posts
python -m src.cli list

# Filter by source
python -m src.cli list --source reddit_trending --limit 50
```

### Statistics

```bash
# Show collection statistics
python -m src.cli stats
```

### Process to IdeaInspiration Format

Transform collected posts to the standardized IdeaInspiration model:

```bash
# Process all unprocessed records
python -m src.cli process

# Process with limit and save to file
python -m src.cli process --limit 100 --output ideas.json
```

### Clear Database

```bash
# Delete all collected posts
python -m src.cli clear
```

## Architecture

This implementation follows SOLID principles and the established pattern from YouTubeShortsSource:

```
Reddit/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management (SRP)
│   │   ├── database.py             # Database wrapper
│   │   ├── db_utils.py             # Database operations
│   │   ├── metrics.py              # Universal metrics (OCP)
│   │   └── idea_processor.py      # IdeaInspiration transform (SRP)
│   └── plugins/
│       ├── __init__.py             # SourcePlugin base (ISP)
│       ├── reddit_trending.py      # Trending scraper (LSP)
│       ├── reddit_subreddit.py     # Subreddit scraper (LSP)
│       ├── reddit_rising.py        # Rising posts scraper (LSP)
│       └── reddit_search.py        # Search-based scraper (LSP)
├── requirements.txt
└── README.md
```

### SOLID Principles

- **Single Responsibility (SRP)**: Each class has one reason to change
  - `Config`: Configuration management only
  - `Database`: Database operations only
  - `IdeaProcessor`: Data transformation only
  
- **Open/Closed (OCP)**: Open for extension, closed for modification
  - `UniversalMetrics`: Add new platforms without changing core
  - Plugin architecture allows new scrapers without modifying base

- **Liskov Substitution (LSP)**: All plugins are substitutable
  - Every plugin extends `SourcePlugin` with consistent interface
  
- **Interface Segregation (ISP)**: Minimal plugin interface
  - Only `scrape()` and `get_source_name()` required
  
- **Dependency Inversion (DIP)**: Depend on abstractions
  - Plugins receive config via dependency injection
  - Database uses URL abstraction, not concrete paths

## Universal Metrics

Reddit posts are transformed to universal metrics for cross-platform comparison:

```python
{
    'platform': 'reddit',
    'view_count': 10000,
    'like_count': 5000,      # Reddit score
    'upvote_count': 5200,
    'comment_count': 250,
    'upvote_ratio': 0.95,
    'engagement_rate': 52.5,  # Calculated
    'score_per_hour': 208.3,  # Viral velocity indicator
    'award_count': 15,
    'award_types': ['gold', 'platinum', 'helpful'],
    'viral_velocity': 109.2,  # Combined metric
}
```

## Data Model

Reddit posts are stored with comprehensive metadata:

```python
{
    'source': 'reddit_trending',
    'source_id': 'abc123',
    'title': 'Amazing startup idea!',
    'description': 'Full post text...',
    'tags': 'startup,entrepreneur,Discussion',
    'metrics': {
        'score': 5000,
        'upvote_ratio': 0.95,
        'num_comments': 250,
        'author': {...},
        'subreddit': {...},
        'content': {...}
    }
}
```

## API Rate Limits

- Reddit API: **60 requests per minute** (authenticated)
- PRAW handles rate limiting automatically
- Read-only mode (no posting required)
- Respects Reddit ToS and subreddit rules

## Target Platform

Optimized for:
- **OS**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen
- **RAM**: 64GB DDR5

## Integration

Part of the PrismQ ecosystem:
- **PrismQ.IdeaInspiration**: Main orchestrator
- **Sources.Content.Shorts.YouTube**: YouTube Shorts source
- **StoryGenerator**: Automated content pipeline
- **Model**: Standardized data models

## Contributing

Follow PrismQ coding standards:
- PEP 8 style guide
- Type hints for all functions
- Google-style docstrings
- SOLID principles
- >80% test coverage (when tests exist)

## License

See LICENSE file in the repository root.

## Links

- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [PRAW Documentation](https://praw.readthedocs.io/)
- [PrismQ.IdeaInspiration](https://github.com/Nomoos/PrismQ.IdeaInspiration)
