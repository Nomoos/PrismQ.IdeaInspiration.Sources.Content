# Forums Source Module

**Platform-optimized forum scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping forum content from various platforms with comprehensive metadata extraction. It supports multiple forum sources including Reddit, Hacker News, and other community discussion platforms.

## Module Structure

```
Forums/
├── _meta/                          # Module metadata
│   ├── _scripts/                   # Quick start and setup scripts
│   ├── docs/                       # Module-level documentation
│   │   ├── HackerNewsSource.md    # Hacker News scraper documentation
│   │   └── RedditSource.md        # Reddit scraper documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   ├── research/                   # Research materials
│   └── tests/                      # Module-specific tests
└── README.md                       # This file
```

## Features

### Supported Sources

1. **Reddit** (`_meta/docs/RedditSource.md`)
   - Trending discussions and community sentiment
   - Post metadata (title, content, subreddit)
   - Upvotes and engagement metrics
   - Comment analysis
   - Trending subreddits and topics

2. **Hacker News** (`_meta/docs/HackerNewsSource.md`)
   - Tech discussions and trends
   - Story rankings and points
   - Comment threads
   - Community insights

### Key Capabilities

- **Comprehensive Metadata**: Title, author, content, timestamps
- **Engagement Analytics**: Upvotes, comments, sentiment
- **Thread Analysis**: Comment trees and discussions
- **Deduplication**: Prevents duplicate entries
- **SQLite Storage**: Persistent storage with complete metadata
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the Forums module
cd Sources/Content/Forums

# Install dependencies (when available)
pip install -r requirements.txt

# Copy environment template (when available)
cp .env.example .env

# Edit .env with your configuration
```

## Usage

*To be implemented*

## Documentation

- **[Reddit Source](_meta/docs/RedditSource.md)** - Reddit content scraping
- **[Hacker News Source](_meta/docs/HackerNewsSource.md)** - Hacker News scraping

For a complete list of documentation, see [_meta/docs/](_meta/docs/).

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../Scoring/)** - Content scoring

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [_meta/docs/](_meta/docs/) directory
- **Issues**: Report via GitHub Issues

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
