# Podcasts Source Module

**Platform-optimized podcast scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping podcast content from various platforms with comprehensive metadata extraction. It supports multiple podcast sources including Apple Podcasts, Spotify, and other podcast platforms.

## Module Structure

```
Podcasts/
├── _meta/                          # Module metadata
│   ├── _scripts/                   # Quick start and setup scripts
│   ├── docs/                       # Module-level documentation
│   │   ├── ApplePodcastsSource.md # Apple Podcasts scraper documentation
│   │   └── SpotifyPodcastsSource.md # Spotify Podcasts scraper documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   ├── research/                   # Research materials
│   └── tests/                      # Module-specific tests
└── README.md                       # This file
```

## Features

### Supported Sources

1. **Apple Podcasts** (`_meta/docs/ApplePodcastsSource.md`)
   - Popular podcasts and episodes
   - Episode metadata and descriptions
   - Ratings and reviews
   - Category trends

2. **Spotify Podcasts** (`_meta/docs/SpotifyPodcastsSource.md`)
   - Trending podcasts
   - Episode information
   - Listener engagement
   - Playlist integration

### Key Capabilities

- **Comprehensive Metadata**: Title, host, episode info, descriptions
- **Engagement Analytics**: Ratings, reviews, listener counts
- **Content Extraction**: Show notes, transcripts (when available)
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
# Navigate to the Podcasts module
cd Sources/Content/Podcasts

# Install dependencies (when available)
pip install -r requirements.txt

# Copy environment template (when available)
cp .env.example .env

# Edit .env with your configuration
```

## Usage

*To be implemented*

## Documentation

- **[Apple Podcasts Source](_meta/docs/ApplePodcastsSource.md)** - Apple Podcasts scraping
- **[Spotify Podcasts Source](_meta/docs/SpotifyPodcastsSource.md)** - Spotify Podcasts scraping

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
