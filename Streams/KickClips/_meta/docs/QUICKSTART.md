# KickClipsSource Quick Start Guide

## Installation

```bash
cd Sources/Content/Streams/KickClips
pip install -r requirements.txt
```

## Basic Usage

### 1. Scrape Trending Clips

```bash
# Scrape top 50 trending clips
python -m src.cli scrape-trending --max-clips 50

# Non-interactive mode
python -m src.cli scrape-trending --max-clips 50 --no-interactive
```

### 2. Scrape Category Clips

```bash
# Scrape clips from gaming category
python -m src.cli scrape-category --category gaming --max-clips 30

# Scrape clips from just-chatting category
python -m src.cli scrape-category --category just-chatting --max-clips 20
```

### 3. Scrape Streamer Clips

```bash
# Scrape clips from specific streamer
python -m src.cli scrape-streamer --streamer xqc --max-clips 25
```

### 4. View Statistics

```bash
# Show database statistics
python -m src.cli stats
```

Output example:
```
=== Kick Clips Database Statistics ===
Database: /path/to/kick_clips.db

Total clips: 100
  - Trending: 50
  - Category: 30
  - Streamer: 20

Top 10 clips by engagement:
  1. [kick_trending] Amazing Gaming Moment (score: 15.50)
  2. [kick_category] Epic Play in Gaming (score: 12.30)
  ...
```

### 5. Export to JSON

```bash
# Export top 100 clips to JSON
python -m src.cli export --output ideas.json --limit 100
```

## Python API Usage

```python
from src import Config, Database, KickTrendingPlugin, UniversalMetrics

# Initialize
config = Config()
db = Database(config.database_path)

# Scrape trending clips
plugin = KickTrendingPlugin(config)
ideas = plugin.scrape(max_clips=50)

# Process each clip
for idea in ideas:
    # Calculate metrics
    metrics = UniversalMetrics.from_kick(idea['metrics'])
    
    # Save to database
    db.insert_idea(
        source='kick_trending',
        source_id=idea['source_id'],
        title=idea['title'],
        description=idea['description'],
        tags=idea['tags'],
        score=metrics.engagement_rate or 0.0,
        score_dictionary=metrics.to_dict()
    )

print(f"Saved {len(ideas)} clips")
```

## Configuration

Edit `.env` file to customize settings:

```bash
# Database
DATABASE_URL=sqlite:///kick_clips.db

# Scraping limits
KICK_TRENDING_MAX_CLIPS=50
KICK_CATEGORY_MAX_CLIPS=50
KICK_STREAMER_MAX_CLIPS=50

# Rate limiting
REQUEST_DELAY=1.0
MAX_RETRIES=3
REQUEST_TIMEOUT=30
```

## Common Categories

Popular Kick categories to scrape:
- `gaming` - General gaming content
- `just-chatting` - Talk shows and discussions
- `music` - Music performances
- `creative` - Art and creative content
- `sports` - Sports commentary
- `politics` - Political discussions

## Tips

1. **Start Small**: Begin with `--max-clips 10` to test
2. **Rate Limiting**: Increase `REQUEST_DELAY` if you get blocked
3. **Database**: Use `stats` command to monitor your collection
4. **Export**: Export to JSON for integration with other tools

## Troubleshooting

### Cloudflare Blocking
If you encounter Cloudflare blocks:
- Increase `REQUEST_DELAY` in `.env`
- Wait before retrying
- Consider using a VPN

### Empty Results
If scraping returns no clips:
- Verify category/streamer exists on Kick.com
- Check your internet connection
- Try a different scraping method

### Database Errors
If you encounter database errors:
- Ensure write permissions for database file
- Check available disk space
- Verify SQLite installation

## Next Steps

1. Integrate with Classification module for content categorization
2. Use Scoring module to rank clips
3. Feed into content generation pipeline
4. Build automated monitoring workflows

## Support

For issues or questions, see:
- Main README: `README.md`
- Issue tracker: `_meta/issues/`
