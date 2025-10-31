@echo off
REM YouTube Shorts Source Quick Start Script for Windows
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
REM This script provides a quick way to run the YouTube Shorts scraper

echo =====================================
echo YouTube Shorts Source Quick Start
echo =====================================
echo.

REM Navigate to the YouTube module directory (two levels up from _meta/_scripts)
cd /d "%~dp0..\.."

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please set up the environment first by running:
    echo   _meta\_scripts\setup.bat
    echo.
    echo Or manually:
    echo   1. Navigate to: Sources\Content\Shorts\YouTube
    echo   2. Create venv: python -m venv venv
    echo   3. Activate venv: venv\Scripts\activate.bat
    echo   4. Install deps: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Check if .env exists, if not copy from .env.example
if not exist ".env" (
    echo WARNING: .env file not found!
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo.
        echo =====================================
        echo IMPORTANT: Configure .env file
        echo =====================================
        echo The .env file has been created from .env.example
        echo Please edit .env with your configuration:
        echo   - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)
        echo   - DATABASE_URL: Database connection string
        echo   - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)
        echo   - Other settings as needed
        echo.
        echo Press any key to open .env in notepad...
        pause >nul
        notepad .env
        echo.
        echo After configuring .env, you can run this script again.
        echo.
        pause
        exit /b 0
    ) else (
        echo ERROR: .env.example file not found!
        echo Cannot create .env file.
        pause
        exit /b 1
    )
)

echo.
echo =====================================
echo Running YouTube Shorts Scraper
echo =====================================
echo Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
echo.
echo Available commands:
echo   scrape-channel  - Scrape from a specific channel (recommended)
echo   scrape-trending - Scrape from trending page
echo   scrape-keyword  - Search by keywords
echo   scrape          - Legacy YouTube API search (not recommended)
echo   stats           - View database statistics
echo   export          - Export data to JSON
echo.
echo For help on any command, run:
echo   python -m src.cli [command] --help
echo.
echo Starting interactive CLI...
echo.

REM Run the YouTube scraper CLI with help
python -m src.cli --help

echo.
echo =====================================
echo Example Usage:
echo =====================================
echo   python -m src.cli scrape-channel --channel-url "https://youtube.com/@channelname"
echo   python -m src.cli scrape-trending --max-results 50
echo   python -m src.cli scrape-keyword --query "startup ideas" --max-results 30
echo   python -m src.cli stats
echo   python -m src.cli export --output ideas.json
echo.
echo =====================================
echo Quick Start Complete!
echo =====================================
echo.

pause
