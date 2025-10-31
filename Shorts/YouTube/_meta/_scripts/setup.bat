@echo off
REM YouTube Shorts Source Setup Script for Windows
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

echo =====================================
echo YouTube Shorts Source Setup
echo =====================================
echo.

REM Navigate to the YouTube module directory (two levels up from _meta/_scripts)
cd /d "%~dp0..\.."

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.

REM Check if .env exists, if not copy from .env.example
if not exist ".env" (
    echo Setting up .env file...
    if exist ".env.example" (
        copy .env.example .env
        echo .env file created from .env.example
        echo.
        echo =====================================
        echo IMPORTANT: Configure .env file
        echo =====================================
        echo Please edit .env with your configuration:
        echo   - YOUTUBE_API_KEY: Your YouTube API key (for API scraping)
        echo   - DATABASE_URL: Database connection string
        echo   - YOUTUBE_CHANNEL_URL: Channel URL (for channel scraping)
        echo   - Other settings as needed
        echo.
    ) else (
        echo WARNING: .env.example file not found
        echo Please create .env file manually
        echo.
    )
) else (
    echo .env file already exists.
    echo.
)

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo To activate the virtual environment manually:
echo   venv\Scripts\activate.bat
echo.
echo To run the module:
echo   _meta\_scripts\run.bat
echo.
echo Or directly:
echo   python -m src.cli --help
echo.

pause
