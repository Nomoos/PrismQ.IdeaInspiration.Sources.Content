# Streams Source Module

**Platform-optimized stream clips scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping streaming content clips from various platforms with comprehensive metadata extraction. It supports multiple streaming sources including Twitch Clips, Kick Clips, and other live streaming platforms.

## Module Structure

```
Streams/
├── _meta/                          # Module metadata
│   ├── _scripts/                   # Quick start and setup scripts
│   ├── docs/                       # Module-level documentation
│   │   ├── TwitchClipsSource.md   # Twitch Clips scraper documentation
│   │   └── KickClipsSource.md     # Kick Clips scraper documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   ├── research/                   # Research materials
│   └── tests/                      # Module-specific tests
└── README.md                       # This file
```

## Features

### Supported Sources

1. **Twitch Clips** (`_meta/docs/TwitchClipsSource.md`)
   - Trending and viral clips
   - Clip metadata (title, creator, game)
   - View counts and engagement
   - Streamer information

2. **Kick Clips** (`_meta/docs/KickClipsSource.md`)
   - Popular clips from Kick platform
   - Engagement metrics
   - Creator insights

### Key Capabilities

- **Comprehensive Metadata**: Title, creator, game, timestamps
- **Engagement Analytics**: Views, likes, shares
- **Content Extraction**: Clip URLs and thumbnails
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
# Navigate to the Streams module
cd Sources/Content/Streams

# Install dependencies (when available)
pip install -r requirements.txt

# Copy environment template (when available)
cp .env.example .env

# Edit .env with your configuration
```

## Usage

*To be implemented*

## Documentation

- **[Twitch Clips Source](_meta/docs/TwitchClipsSource.md)** - Twitch Clips scraping
- **[Kick Clips Source](_meta/docs/KickClipsSource.md)** - Kick Clips scraping

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
