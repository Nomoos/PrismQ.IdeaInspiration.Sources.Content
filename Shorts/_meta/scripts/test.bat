@echo off
REM PrismQ Module Test Script for Windows
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

echo =====================================
echo PrismQ Module Test
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running tests with pytest...
echo Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
echo.

REM Run pytest with coverage
pytest

if errorlevel 1 (
    echo.
    echo =====================================
    echo Tests failed!
    echo =====================================
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Tests Complete!
echo =====================================
echo All tests passed.
echo.
echo Coverage report generated in htmlcov/index.html
echo.

pause
