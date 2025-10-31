# PrismQ HackerNews Source

**Collect idea inspirations from HackerNews** - trending stories, Ask HN, Show HN, and high-quality tech discussions.

Part of the [PrismQ.IdeaInspiration](https://github.com/Nomoos/PrismQ.IdeaInspiration) ecosystem for AI-powered content generation.

## Features

- 🔥 **Top Stories**: Scrape front page trending stories
- 🆕 **New Stories**: Discover newest submissions
- ⭐ **Best Stories**: Algorithmically ranked quality content
- ❓ **Ask HN**: Question and discussion posts
- 💡 **Show HN**: Project and product launches
- 📊 **Universal Metrics**: Cross-platform engagement analytics
- 💾 **SQLite Storage**: Automatic deduplication
- 🔄 **IdeaInspiration Format**: Transform to standardized model

## Installation

### Prerequisites

- Python 3.8+
- No API credentials required (uses public HackerNews API)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration/Sources/Content/Forums/HackerNews
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure (optional)**:
   - Copy `.env.example` to `.env` and customize settings
   - Configuration is optional - sensible defaults are provided

## Usage

### Scrape Top Stories

```bash
# Scrape front page top stories
python -m src.cli scrape-frontpage

# Scrape specific number of top stories
python -m src.cli scrape-frontpage --top 20
python -m src.cli scrape-frontpage -t 15
```

### Scrape New Stories

```bash
# Discover newest stories
python -m src.cli scrape-new

# Scrape specific number of new stories
python -m src.cli scrape-new --top 20
```

### Scrape Best Stories

```bash
# Scrape algorithmically ranked best stories
python -m src.cli scrape-best

# Scrape specific number
python -m src.cli scrape-best --top 20
```

### Scrape Ask HN Posts

```bash
# Scrape Ask HN questions and discussions
python -m src.cli scrape-ask

# Scrape specific number
python -m src.cli scrape-ask --top 10
```

### Scrape Show HN Posts

```bash
# Scrape Show HN project/product launches
python -m src.cli scrape-show

# Scrape specific number
python -m src.cli scrape-show --top 10
```

### View Collected Posts

```bash
# List all posts
python -m src.cli list

# Filter by source
python -m src.cli list --source hackernews_frontpage --limit 50
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

This implementation follows SOLID principles and the established pattern from Reddit and YouTube sources:

```
HackerNews/
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
│       ├── hn_frontpage.py         # Frontpage scraper (LSP)
│       ├── hn_new.py               # New stories scraper (LSP)
│       ├── hn_best.py              # Best stories scraper (LSP)
│       └── hn_type.py              # Type-based scraper (Ask/Show HN) (LSP)
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

HackerNews posts are transformed to universal metrics for cross-platform comparison:

```python
{
    'platform': 'hackernews',
    'content_type': 'story',
    'like_count': 500,           # HN score as "likes"
    'comment_count': 150,        # Total descendants
    'descendants_count': 150,
    'engagement_rate': 30.0,     # comments/score ratio
    'points_per_hour': 100,      # Viral velocity indicator
    'viral_velocity': 300.0,     # Combined metric
    'hours_since_post': 5.0,
}
```

## Data Model

HackerNews posts are stored with comprehensive metadata:

```python
{
    'source': 'hackernews_frontpage',
    'source_id': '12345678',
    'title': 'Show HN: My startup idea',
    'description': 'Post text content...',
    'tags': 'story,Show HN,ycombinator.com',
    'metrics': {
        'score': 500,
        'descendants': 150,
        'type': 'story',
        'by': 'username',
        'time': 1234567890,
        'url': 'https://example.com'
    }
}
```

## API Information

- **HackerNews API**: https://github.com/HackerNews/API
- **Firebase-based API** with real-time updates
- **No authentication required**
- **No explicit rate limits** (be respectful)
- **Free and public access**

### API Endpoints

- `/v0/topstories.json` - Top 500 stories
- `/v0/newstories.json` - Newest stories
- `/v0/beststories.json` - Best stories (algorithmically ranked)
- `/v0/item/{id}.json` - Individual item details

## Target Platform

Optimized for:
- **OS**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen
- **RAM**: 64GB DDR5

## Integration

Part of the PrismQ ecosystem:
- **PrismQ.IdeaInspiration**: Main orchestrator
- **Sources.Content.Forums.Reddit**: Reddit source
- **Sources.Content.Shorts.YouTube**: YouTube Shorts source
- **StoryGenerator**: Automated content pipeline
- **Model**: Standardized data models

## Configuration

All configuration is optional. Default values:

```env
# Database
DATABASE_URL=sqlite:///db.s3db

# Scraping limits
HN_FRONTPAGE_MAX_POSTS=10
HN_NEW_MAX_POSTS=10
HN_BEST_MAX_POSTS=10
HN_TYPE_MAX_POSTS=10

# API settings
HN_API_BASE_URL=https://hacker-news.firebaseio.com/v0
HN_REQUEST_TIMEOUT=10
```

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

- [HackerNews API Documentation](https://github.com/HackerNews/API)
- [PrismQ.IdeaInspiration](https://github.com/Nomoos/PrismQ.IdeaInspiration)
- [HackerNews](https://news.ycombinator.com)

## Why HackerNews?

HackerNews provides:
- **High-quality tech content** with strong community curation
- **Startup and innovation focus** perfect for IdeaInspiration
- **Simple, reliable API** no authentication required
- **Ask/Show HN posts** excellent for discovering new projects and ideas
- **Active community** of tech professionals and entrepreneurs
