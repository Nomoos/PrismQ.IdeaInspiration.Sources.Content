#!/bin/bash
# YouTube Shorts Source Quick Start Script for Linux
# Note: Windows is the primary target platform. This script provides limited Linux support for testing only.
# macOS is not supported.

set -e

echo "====================================="
echo "YouTube Shorts Source Quick Start"
echo "====================================="
echo

# Navigate to the YouTube module directory (two levels up from _meta/_scripts)
cd "$(dirname "$0")/../.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo
    echo "Please set up the environment first by running:"
    echo "  _meta/_scripts/setup.sh"
    echo
    echo "Or manually:"
    echo "  1. Navigate to: Sources/Content/Shorts/YouTube"
    echo "  2. Create venv: python3 -m venv venv"
    echo "  3. Activate venv: source venv/bin/activate"
    echo "  4. Install deps: pip install -r requirements.txt"
    echo
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo

# Check if .env exists, if not copy from .env.example
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
        echo
        echo "====================================="
        echo "IMPORTANT: Configure .env file"
        echo "====================================="
        echo "The .env file has been created from .env.example"
        echo "Please edit .env with your configuration:"
        echo "  - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)"
        echo "  - DATABASE_URL: Database connection string"
        echo "  - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)"
        echo "  - Other settings as needed"
        echo
        echo "Edit the .env file and run this script again."
        echo
        exit 0
    else
        echo "ERROR: .env.example file not found!"
        echo "Cannot create .env file."
        exit 1
    fi
fi

echo
echo "====================================="
echo "Running YouTube Shorts Scraper"
echo "====================================="
echo "Note: Windows is the primary target platform (NVIDIA RTX 5090, AMD Ryzen, 64GB RAM)"
echo "      This Linux script is for testing purposes only. macOS is not supported."
echo
echo "Available commands:"
echo "  scrape-channel  - Scrape from a specific channel (recommended)"
echo "  scrape-trending - Scrape from trending page"
echo "  scrape-keyword  - Search by keywords"
echo "  scrape          - Legacy YouTube API search (not recommended)"
echo "  stats           - View database statistics"
echo "  export          - Export data to JSON"
echo
echo "For help on any command, run:"
echo "  python -m src.cli [command] --help"
echo
echo "Starting interactive CLI..."
echo

# Run the YouTube scraper CLI with help
python -m src.cli --help

echo
echo "====================================="
echo "Example Usage:"
echo "====================================="
echo "  python -m src.cli scrape-channel --channel-url \"https://youtube.com/@channelname\""
echo "  python -m src.cli scrape-trending --max-results 50"
echo "  python -m src.cli scrape-keyword --query \"startup ideas\" --max-results 30"
echo "  python -m src.cli stats"
echo "  python -m src.cli export --output ideas.json"
echo
echo "====================================="
echo "Quick Start Complete!"
echo "====================================="
echo
