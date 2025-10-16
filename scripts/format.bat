@echo off
REM PrismQ Module Format Script for Windows
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

echo =====================================
echo PrismQ Module Format
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
echo Formatting code with Ruff (PEP 8)...
echo Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
echo.

REM Run ruff format
ruff format .

if errorlevel 1 (
    echo.
    echo =====================================
    echo Formatting failed!
    echo =====================================
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Formatting Complete!
echo =====================================
echo Code has been formatted according to PEP 8.
echo.

pause
