# Kick Clips Data Model

## Database Schema

### KickClipsSource Table

```sql
CREATE TABLE KickClipsSource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,           -- Source type: kick_trending, kick_category, kick_streamer
    source_id TEXT NOT NULL,        -- Unique clip ID from Kick
    title TEXT NOT NULL,            -- Clip title
    description TEXT,               -- Generated description (category, streamer)
    tags TEXT,                      -- Comma-separated tags
    score REAL,                     -- Engagement rate score
    score_dictionary TEXT,          -- JSON string of universal metrics
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, source_id)       -- Prevent duplicates
);
```

## Data Structure

### Idea Dictionary (Internal Format)

```python
{
    'source_id': 'clip123456',
    'title': 'Amazing Gaming Moment',
    'description': 'Category: Gaming | Streamer: xqc',
    'tags': 'Gaming,xqc',
    'metrics': {
        'views': 50000,
        'likes': 500,
        'reactions': 500,
        'comments': 0,
        'shares': 0,
        'duration': 45,
        'created_at': '2025-01-15T10:30:00Z',
        'streamer_followers': 100000,
        'streamer_verified': True
    },
    'category': {
        'name': 'Gaming',
        'id': 'gaming'
    },
    'streamer': {
        'username': 'xqc',
        'followers': 100000,
        'verified': True
    },
    'clip': {
        'duration': 45,
        'language': 'en',
        'created_at': '2025-01-15T10:30:00Z'
    },
    'universal_metrics': {
        'view_count': 50000,
        'like_count': 500,
        'reaction_count': 500,
        'engagement_rate': 1.0,  # (likes + reactions) / views * 100
        'views_per_day': 5000,
        'views_per_hour': 208.33,
        'viral_velocity': 20.83,  # views_per_hour / days_since * growth_factor
        'platform': 'kick',
        'content_type': 'clip'
    }
}
```

### IdeaInspiration Format (Export)

```python
{
    'title': 'Amazing Gaming Moment',
    'description': 'Category: Gaming | Streamer: xqc',
    'content': '',  # Empty for clips (no transcription)
    'keywords': ['Gaming', 'xqc'],
    'source_type': 'video',
    'metadata': {
        'duration': '45',
        'language': 'en',
        'views': '50000',
        'reactions': '500'
    },
    'source_id': 'clip123456',
    'source_url': 'https://kick.com/video/clip123456',
    'source_created_by': 'xqc',
    'source_created_at': '2025-01-15T10:30:00Z',
    'score': 1,  # Engagement rate as integer
    'category': 'Gaming',
    'subcategory_relevance': {},
    'contextual_category_scores': {}
}
```

## Universal Metrics

### Calculated Metrics

1. **Engagement Rate**
   ```python
   engagement_rate = ((likes + reactions) / views) * 100
   ```

2. **Views Per Day**
   ```python
   views_per_day = views / days_since_upload
   ```

3. **Views Per Hour**
   ```python
   views_per_hour = views_per_day / 24
   ```

4. **Viral Velocity** (Kick-specific)
   ```python
   platform_growth_factor = 2.0  # Kick is a growing platform
   viral_velocity = (views_per_hour / days_since_upload) * platform_growth_factor
   ```

### Metric Ratios

- **Like to View Ratio**: `(likes / views) * 100`
- **Reaction to View Ratio**: `(reactions / views) * 100`
- **Comment to View Ratio**: `(comments / views) * 100`

## Data Flow

### 1. Scraping Flow

```
Kick API → Plugin.scrape() → Idea Dictionary → Database
```

### 2. Processing Flow

```
Database → IdeaProcessor → IdeaInspiration Format → JSON Export
```

### 3. Integration Flow

```
JSON Export → Classification Module → Scoring Module → Content Pipeline
```

## Field Descriptions

### Core Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| source_id | String | Unique clip ID from Kick | "clip123456" |
| title | String | Clip title | "Amazing Gaming Moment" |
| description | String | Generated description | "Category: Gaming" |
| tags | String | Comma-separated tags | "Gaming,xqc" |

### Metrics Fields

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| views | Integer | Total view count | 0 - ∞ |
| likes | Integer | Like count | 0 - ∞ |
| reactions | Integer | Reaction count | 0 - ∞ |
| engagement_rate | Float | Percentage engagement | 0 - 100% |
| viral_velocity | Float | Growth rate metric | 0 - ∞ |

### Metadata Fields

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| duration | Integer | Clip length in seconds | 0 - 300 |
| language | String | Clip language | ISO 639-1 |
| created_at | String | Upload timestamp | ISO 8601 |

## Best Practices

### 1. Deduplication

The database enforces uniqueness on `(source, source_id)`:
- First insert: Returns `True` (new record)
- Duplicate insert: Returns `False` (updates existing)

### 2. Scoring

Use engagement rate as the primary score:
```python
score = universal_metrics.engagement_rate or 0.0
```

### 3. Tagging

Combine category and streamer for comprehensive tagging:
```python
tags = [category_name, streamer_username]
```

### 4. Metadata

Store platform-specific data in score_dictionary:
```python
score_dictionary = universal_metrics.to_dict()
```

## API Response Examples

### Kick API Clip Object

```json
{
    "id": "clip123456",
    "title": "Amazing Gaming Moment",
    "views": 50000,
    "likes": 500,
    "duration": 45,
    "created_at": "2025-01-15T10:30:00Z",
    "language": "en",
    "category": {
        "name": "Gaming",
        "id": "gaming"
    },
    "channel": {
        "username": "xqc",
        "followers_count": 100000,
        "verified": true
    }
}
```

## Migration & Compatibility

The data model is compatible with:
- PrismQ.IdeaInspiration.Model (via IdeaProcessor)
- YouTubeShortsSource (similar structure)
- Classification module (via exported JSON)
- Scoring module (via universal metrics)

## Version History

- **v1.0.0** (2025-10-30): Initial implementation
  - Basic clip metadata
  - Universal metrics
  - Three scraping plugins
  - IdeaInspiration transformation
