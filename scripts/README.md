# Scripts

This directory contains utility scripts for the PrismQ module.

## Available Scripts

### Setup Scripts

- **setup.bat** - Windows setup script

### Quick Start Scripts

- **quickstart.bat** - Quick start for Windows

### Development Scripts

- **lint.bat** - Run code quality checks (ruff check + mypy)
- **format.bat** - Format code with Ruff (PEP 8)
- **test.bat** - Run tests with pytest

### Module Management Scripts

- **add-module.bat** - Create a new module with proper structure
- **sync-modules.bat** - Sync modules using git subtree

## Usage

### Windows

Create a new module:
```batch
scripts\add-module.bat ModuleName
REM or with custom remote URL
scripts\add-module.bat ModuleName https://github.com/Nomoos/ModuleName.git
```

Run the setup script to install dependencies:
```batch
scripts\setup.bat
```

Run the quick start script to test the module:
```batch
scripts\quickstart.bat
```

Run development scripts for code quality:
```batch
REM Format code (PEP 8)
scripts\format.bat

REM Lint code (PEP 8, PEP 257) and type check (PEP 484, 526, 544)
scripts\lint.bat

REM Run tests
scripts\test.bat
```

Sync modules from their remote repositories:
```batch
REM List all modules
scripts\sync-modules.bat --list

REM Sync all modules
scripts\sync-modules.bat --all

REM Sync a specific module
scripts\sync-modules.bat src\YourModule
```

### Configuring Python Executable

The setup scripts support configurable Python executables. To use a specific Python version:

1. Copy `.env.example` to `.env` (if not already done)
2. Set the `PYTHON_EXECUTABLE` variable:
   ```
   PYTHON_EXECUTABLE=python
   # or
   PYTHON_EXECUTABLE=python3.10
   # or
   PYTHON_EXECUTABLE=C:\Python310\python.exe
   ```
3. Run the setup script - it will use your specified Python executable

This is useful when:
- You have multiple Python versions installed
- Different subprojects require different Python versions
- You need to use a specific Python installation

## Target Platform

These scripts are optimized for:
- **OS**: Windows (required)
- **GPU**: NVIDIA RTX 5090
- **CPU**: AMD Ryzen
- **RAM**: 64GB

## Creating New Scripts

When adding new scripts:
1. Create Windows batch files (.bat) as the primary implementation
2. Add clear comments explaining what the script does
3. Include error handling
4. Update this README
