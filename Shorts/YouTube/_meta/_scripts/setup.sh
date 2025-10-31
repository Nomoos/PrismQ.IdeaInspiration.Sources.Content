#!/bin/bash
# YouTube Shorts Source Setup Script for Linux
# Note: Windows is the primary target platform. This script provides limited Linux support for testing only.
# macOS is not supported.

set -e

echo "====================================="
echo "YouTube Shorts Source Setup"
echo "====================================="
echo

# Navigate to the YouTube module directory (two levels up from _meta/_scripts)
cd "$(dirname "$0")/../.."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Python found!"
python3 --version
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo

# Check if .env exists, if not copy from .env.example
if [ ! -f ".env" ]; then
    echo "Setting up .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env file created from .env.example"
        echo
        echo "====================================="
        echo "IMPORTANT: Configure .env file"
        echo "====================================="
        echo "Please edit .env with your configuration:"
        echo "  - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)"
        echo "  - DATABASE_URL: Database connection string"
        echo "  - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)"
        echo "  - Other settings as needed"
        echo
    else
        echo "WARNING: .env.example file not found"
        echo "Please create .env file manually"
        echo
    fi
else
    echo ".env file already exists."
    echo
fi

echo
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo
echo "To run the module:"
echo "  _meta/_scripts/run.sh"
echo
echo "Or directly:"
echo "  python -m src.cli --help"
echo
