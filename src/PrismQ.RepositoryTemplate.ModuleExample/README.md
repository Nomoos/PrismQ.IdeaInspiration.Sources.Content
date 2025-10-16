# PrismQ.RepositoryTemplate.ModuleExample

An example module demonstrating the structure and configuration of PrismQ modules.

## Purpose

This module serves as a reference implementation for creating new PrismQ modules. It demonstrates:

- Proper directory structure
- Module configuration with `module.json`
- Python code organization
- Testing structure
- Documentation standards

## Structure

```
PrismQ.RepositoryTemplate.ModuleExample/
├── module.json          # Module configuration
├── src/                 # Source code
│   ├── __init__.py
│   ├── config.py       # Configuration management
│   └── main.py         # Main entry point
├── tests/              # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   └── test_main.py
└── README.md           # This file
```

## Configuration

The module uses `module.json` for git subtree synchronization:

```json
{
  "remote": {
    "url": "https://github.com/Nomoos/PrismQ.RepositoryTemplate.ModuleExample.git"
  }
}
```

This configuration allows the module to be synchronized with its remote repository using the sync scripts.

## Usage

### Running the Module

```bash
cd src/PrismQ.RepositoryTemplate.ModuleExample
python -m src.main
```

### Running Tests

```bash
cd src/PrismQ.RepositoryTemplate.ModuleExample/tests
pytest
```

## Features

- **Configuration Management**: Environment-based configuration with sensible defaults
- **Example Processing**: Demonstrates simple data processing
- **Comprehensive Tests**: Unit tests for all functionality
- **Type Hints**: Full type annotations for better IDE support and type checking

## Integration

This module can be synchronized using the repository's sync scripts:

**Windows:**
```batch
scripts\sync-modules.bat src\PrismQ.RepositoryTemplate.ModuleExample
```

## Development

When developing this module:

1. Follow PEP 8 coding standards
2. Add type hints to all functions
3. Write tests for new functionality
4. Update this README as needed

## Target Platform

- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

Proprietary - All Rights Reserved

Copyright (c) 2025 PrismQ
