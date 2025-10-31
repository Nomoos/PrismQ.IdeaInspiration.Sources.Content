# Kick API Documentation

## Overview

This document describes the unofficial Kick API endpoints used by KickClipsSource. These endpoints are reverse-engineered and may change without notice.

**⚠️ Warning**: These are unofficial endpoints. Use responsibly and respect Kick's Terms of Service.

## Base URL

```
https://kick.com/api/v2
```

## Authentication

Most clip endpoints are **public** and don't require authentication. However:

- Rate limiting is enforced by Kick
- Cloudflare protection is active
- We use `cloudscraper` library to bypass protection

## Endpoints

### 1. Trending Clips

**Endpoint**: `/clips/trending`

**Method**: GET

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | Integer | No | Page number (default: 1) |
| limit | Integer | No | Results per page (default: 20, max: 100) |

**Example Request**:
```
GET https://kick.com/api/v2/clips/trending?page=1&limit=20
```

**Example Response**:
```json
{
  "data": [
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
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10
  }
}
```

### 2. Category Clips

**Endpoint**: `/categories/{category_slug}/clips`

**Method**: GET

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category_slug | String | Yes | Category identifier (e.g., 'gaming') |
| page | Integer | No | Page number |
| limit | Integer | No | Results per page |

**Example Request**:
```
GET https://kick.com/api/v2/categories/gaming/clips?page=1&limit=20
```

**Response**: Same structure as trending clips

### 3. Streamer/Channel Clips

**Endpoint**: `/channels/{username}/clips`

**Method**: GET

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | String | Yes | Streamer username |
| page | Integer | No | Page number |
| limit | Integer | No | Results per page |

**Example Request**:
```
GET https://kick.com/api/v2/channels/xqc/clips?page=1&limit=20
```

**Response**: Same structure as trending clips, may include additional channel info

## Response Fields

### Clip Object

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique clip identifier |
| title | String | Clip title |
| views | Integer | Total view count |
| likes | Integer | Total likes |
| duration | Integer | Clip duration in seconds |
| created_at | String | ISO 8601 timestamp |
| language | String | Clip language (ISO 639-1) |
| category | Object | Category information |
| channel | Object | Channel/streamer information |

### Category Object

| Field | Type | Description |
|-------|------|-------------|
| id | String | Category identifier |
| name | String | Category display name |

### Channel Object

| Field | Type | Description |
|-------|------|-------------|
| username | String | Streamer username |
| followers_count | Integer | Total followers |
| verified | Boolean | Verification status |

## Error Handling

### HTTP Status Codes

| Code | Description | Action |
|------|-------------|--------|
| 200 | Success | Process response |
| 404 | Not found | Category/streamer doesn't exist |
| 429 | Rate limit | Wait and retry with backoff |
| 403 | Forbidden | Cloudflare block, increase delay |
| 500 | Server error | Retry with backoff |

### Error Response Example

```json
{
  "error": "Category not found",
  "status": 404
}
```

## Rate Limiting

### Recommended Practices

1. **Delay Between Requests**: 1-2 seconds
2. **Maximum Retries**: 3 attempts
3. **Backoff Strategy**: Exponential (2x each retry)
4. **Request Timeout**: 30 seconds

### Configuration

```python
REQUEST_DELAY=1.0        # Seconds between requests
MAX_RETRIES=3           # Maximum retry attempts
REQUEST_TIMEOUT=30      # Request timeout in seconds
```

## Cloudflare Protection

Kick uses Cloudflare to protect against scraping. Our approach:

### Solution: cloudscraper

```python
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get(url, params=params, timeout=30)
```

### If Blocked

1. **Increase Delay**: Set `REQUEST_DELAY=2.0` or higher
2. **Wait**: Take a break before retrying
3. **VPN**: Consider using a VPN
4. **User Agent**: cloudscraper handles this automatically

## Pagination

### Strategy

```python
page = 1
per_page = 20

while True:
    clips = fetch_clips(page, per_page)
    
    if not clips or len(clips) < per_page:
        break  # No more pages
    
    process_clips(clips)
    page += 1
    time.sleep(REQUEST_DELAY)
```

### Limits

- **Per Page**: Max 100 (recommended: 20)
- **Total Pages**: Varies by endpoint
- **Total Results**: Limited by Kick's API

## Data Freshness

- **Trending**: Updated frequently (minutes)
- **Category**: Updated regularly (hours)
- **Streamer**: Updated when new clips added

## Alternative Endpoints (Not Implemented)

These endpoints exist but are not currently implemented:

### Live Streams
```
GET /streams/live
```

### Clip Details
```
GET /clips/{clip_id}
```

### Search
```
GET /search/clips?query={query}
```

## API Changes

The Kick API is unofficial and may change. Monitor for:

1. **Endpoint Changes**: URLs may be updated
2. **Response Format**: Field names/structure may change
3. **Authentication**: May require auth in the future
4. **Rate Limits**: May become stricter

### Monitoring

Check these indicators:
- Increased 403/404 errors
- Empty responses
- Changed response structure
- New required parameters

## Best Practices

### 1. Error Handling

```python
for attempt in range(MAX_RETRIES):
    try:
        response = scraper.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return []  # Not found
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(REQUEST_DELAY * 2)
```

### 2. Respect Rate Limits

```python
import time

time.sleep(REQUEST_DELAY)  # Always delay between requests
```

### 3. Handle Empty Responses

```python
data = response.json()

# API may return different structures
if isinstance(data, list):
    return data
elif isinstance(data, dict) and 'data' in data:
    return data['data']
else:
    return []
```

### 4. Validate Data

```python
clip_id = clip.get('id') or clip.get('clip_id')
if not clip_id:
    return None  # Invalid clip
```

## Legal & Ethical Considerations

### Terms of Service

- Review Kick's ToS before scraping
- Respect rate limits
- Don't overload servers
- Use for research/personal purposes

### Data Usage

- Don't republish scraped data
- Respect streamer/creator rights
- Follow copyright laws
- Use responsibly

## Troubleshooting

### Common Issues

**Empty Results**:
- Category/streamer may not exist
- Try different parameters
- Check endpoint spelling

**403 Errors**:
- Cloudflare blocking
- Increase `REQUEST_DELAY`
- Wait before retrying

**Timeout Errors**:
- Increase `REQUEST_TIMEOUT`
- Check network connection
- Verify Kick.com is accessible

## Support

For API issues:
- Check Kick.com status
- Review error messages
- Test with curl/Postman
- Contact PrismQ support

---

**Last Updated**: 2025-10-30  
**API Version**: v2 (unofficial)  
**Status**: Active
