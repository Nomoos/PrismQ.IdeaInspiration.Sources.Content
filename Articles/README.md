# Articles Source Module

**Platform-optimized article scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping article content from various platforms with comprehensive metadata extraction. It supports multiple article sources including Medium, web articles, and other long-form content platforms.

## Module Structure

```
Articles/
├── _meta/                          # Module metadata
│   ├── _scripts/                   # Quick start and setup scripts
│   ├── docs/                       # Module-level documentation
│   │   ├── MediumSource.md        # Medium scraper documentation
│   │   └── WebArticleSource.md    # Web article scraper documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   ├── research/                   # Research materials
│   └── tests/                      # Module-specific tests
└── README.md                       # This file
```

## Features

### Supported Sources

1. **Medium** (`_meta/docs/MediumSource.md`)
   - Trending articles and thought leadership content
   - Article metadata (title, author, tags)
   - Read time and claps
   - Topics and categories
   - Author insights

2. **Web Articles** (`_meta/docs/WebArticleSource.md`)
   - General web article scraping
   - Metadata extraction
   - Content analysis

### Key Capabilities

- **Comprehensive Metadata**: Title, author, tags, read time
- **Engagement Analytics**: Claps, reads, shares
- **Content Extraction**: Full article text and structure
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
# Navigate to the Articles module
cd Sources/Content/Articles

# Install dependencies (when available)
pip install -r requirements.txt

# Copy environment template (when available)
cp .env.example .env

# Edit .env with your configuration
```

## Usage

*To be implemented*

## Documentation

- **[Medium Source](_meta/docs/MediumSource.md)** - Medium article scraping
- **[Web Article Source](_meta/docs/WebArticleSource.md)** - General web article scraping

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
