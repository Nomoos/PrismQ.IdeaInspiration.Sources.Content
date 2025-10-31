# Signals Source Module

**Early indicators of emerging trends and cultural shifts**

## Overview

This module aggregates signal data from multiple platforms - early indicators of emerging trends including search trends, hashtags, memes, challenges, sounds, location-based trends, and breaking news. Based on the PrismQ Source Taxonomy category **Signals**.

## Source Category

**Category**: Signals  
**Purpose**: Early indicators of emerging trends  
**Value**: Detect trends before they peak, inform content strategy

## Subcategories

This source collects the following types of signals:

### Trends
- **GoogleTrendsSource** - Search trend data from Google Trends
- **TrendsFileSource** - Import trend data from files

### Hashtags
- **TikTokHashtagSource** - Trending hashtags on TikTok
- **InstagramHashtagSource** - Trending hashtags on Instagram

### Memes
- **MemeTrackerSource** - Track viral meme formats
- **KnowYourMemeSource** - Documented meme origins and spread

### Challenges
- **SocialChallengeSource** - Viral social media challenges

### Sounds
- **TikTokSoundsSource** - Trending audio on TikTok
- **InstagramAudioTrendsSource** - Trending audio on Instagram

### Locations
- **GeoLocalTrendsSource** - Location-based trending topics

### News
- **GoogleNewsSource** - Breaking news from Google News
- **NewsApiSource** - News aggregation via NewsAPI

## Module Structure

```
Signals/
├── _meta/                          # Module metadata
│   ├── _scripts/                   # Quick start and setup scripts
│   ├── docs/                       # Module-level documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   ├── research/                   # Research materials
│   └── tests/                      # Module-specific tests
└── README.md                       # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the Signals module
cd Sources/Content/Signals

# Install dependencies (when available)
pip install -r requirements.txt

# Copy environment template (when available)
cp .env.example .env

# Edit .env with your configuration
```

## Usage

*To be implemented - This module will aggregate signal data from various platforms*

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../../Scoring/)** - Content scoring

## Documentation

See [_meta/docs/](_meta/docs/) for additional documentation about specific signal sources.

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
