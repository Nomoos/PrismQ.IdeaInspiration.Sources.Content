# Quick Start Scripts

This directory contains quick start and setup scripts for the YouTube Shorts Source module.

## Scripts

### Setup Scripts

**Windows: `setup.bat`**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Optionally creates .env file from .env.example

**Linux: `setup.sh`**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Optionally creates .env file from .env.example
- Note: Linux support is for testing purposes only; Windows is the primary target platform

### Run Scripts

**Windows: `run.bat`**
- Activates virtual environment
- Creates .env from .env.example if .env doesn't exist
- Opens .env in notepad for configuration (first run only)
- Runs the YouTube Shorts scraper CLI with help and examples

**Linux: `run.sh`**
- Activates virtual environment
- Creates .env from .env.example if .env doesn't exist
- Prompts user to configure .env (first run only)
- Runs the YouTube Shorts scraper CLI with help and examples
- Note: Linux support is for testing purposes only; Windows is the primary target platform

## Usage

### First Time Setup

**Windows:**
```cmd
cd Sources\Content\Shorts\YouTube
_meta\_scripts\setup.bat
_meta\_scripts\run.bat
```

**Linux:**
```bash
cd Sources/Content/Shorts/YouTube
_meta/_scripts/setup.sh
_meta/_scripts/run.sh
```

### Subsequent Runs

After initial setup, you can just run:

**Windows:**
```cmd
_meta\_scripts\run.bat
```

**Linux:**
```bash
_meta/_scripts/run.sh
```

## Configuration

The run scripts will automatically:
1. Check for virtual environment (prompt to run setup if missing)
2. Check for .env file
3. Copy .env.example to .env if .env doesn't exist
4. On Windows: Open .env in notepad for editing (first run only)
5. On Linux: Prompt user to edit .env manually (first run only)

### Required .env Configuration

At minimum, configure these in your .env file:
- `DATABASE_URL`: Database connection string (default: `sqlite:///db.s3db`)
- `YOUTUBE_API_KEY`: Your YouTube API key (for API-based scraping)
- `YOUTUBE_CHANNEL_URL`: Channel URL for channel-based scraping (optional)

See `.env.example` for all available configuration options.

## Available Commands

After running the scripts, you can use these CLI commands:

- `scrape-channel` - Scrape from a specific channel (recommended)
- `scrape-trending` - Scrape from trending page
- `scrape-keyword` - Search by keywords
- `stats` - View database statistics
- `export` - Export data to JSON

For detailed help on any command:
```bash
python -m src.cli [command] --help
```

## Target Platform

- **Primary**: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
- **Secondary**: Linux (for testing and CI/CD only)
- **Not Supported**: macOS

## Troubleshooting

### Virtual Environment Not Found
Run the setup script first:
- Windows: `_meta\_scripts\setup.bat`
- Linux: `_meta/_scripts/setup.sh`

### Module Not Found Errors
The virtual environment may not have all dependencies. Run:
```bash
venv\Scripts\activate.bat  # Windows
source venv/bin/activate   # Linux
pip install -r requirements.txt
```

### .env File Issues
Ensure your .env file exists and contains valid configuration:
```bash
# Check if .env exists
ls -la .env

# If missing, copy from example
cp .env.example .env  # Linux
copy .env.example .env  # Windows
```

## Notes

- Scripts automatically navigate to the YouTube module root directory
- All paths are relative to the module root (Sources/Content/Shorts/YouTube)
- The setup script can be run multiple times safely
- The run script will pause after showing help and examples
