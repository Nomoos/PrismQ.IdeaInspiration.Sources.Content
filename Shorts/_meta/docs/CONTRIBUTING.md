# Contributing to PrismQ Module

Thank you for your interest in contributing to this PrismQ module!

## Development Environment

### System Requirements

- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB
- **Python**: 3.10 or higher

### Setup

1. Clone the repository
2. Create a virtual environment (PEP 405):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies in editable mode (PEP 660):
   ```bash
   pip install -e .[dev]
   ```
4. Copy `.env.example` to `.env` and configure

## Development Workflow

1. **Create a branch** for your changes
2. **Make your changes** following the coding standards
3. **Write tests** for new functionality
4. **Run code quality checks**:
   ```bash
   ruff format .      # Format code (PEP 8)
   ruff check .       # Lint code (PEP 8, PEP 257)
   mypy src/          # Type check (PEP 484, 526, 544)
   ```
5. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```
6. **Submit a pull request** with a clear description

## Coding Standards

PrismQ follows several Python Enhancement Proposals (PEPs) for code quality and consistency, along with SOLID design principles. See the following documents for full details:

- **[PEP Standards](PEP_STANDARDS.md)** - Python Enhancement Proposals we follow
- **[SOLID Principles](SOLID_PRINCIPLES.md)** - Design principles for maintainable code
- **[AI Coding Guidelines](AI_CODING_GUIDELINES.md)** - Best practices for AI-assisted development

### Key Requirements

#### Code Style (PEP Standards)
- **PEP 8**: Follow the style guide using Ruff for formatting and linting
- **PEP 257**: Write Google-style docstrings for all public functions and classes
- **PEP 484/526**: Use type hints for all function parameters, return values, and variables
- **PEP 544**: Use Protocols for interface definitions
- **PEP 328**: Prefer absolute imports over relative imports

#### Design Principles (SOLID)
- **Single Responsibility**: Each class should have one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Clients shouldn't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### Code Quality Tools

```bash
# Format code (replaces black)
ruff format .

# Check for style violations
ruff check .

# Auto-fix violations where possible
ruff check --fix .

# Type checking
mypy src/

# Run all checks before committing
ruff format . && ruff check . && mypy src/ && pytest
```

### Example Code

```python
from pathlib import Path
from typing import Any


def process_file(input_path: Path, verbose: bool = False) -> dict[str, Any]:
    """Process a file and return results.
    
    Args:
        input_path: Path to the input file.
        verbose: Enable verbose logging.
        
    Returns:
        Dictionary containing processing results.
        
    Raises:
        FileNotFoundError: If input file doesn't exist.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    result: dict[str, Any] = {"status": "success"}
    return result
```

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage (>80%)
- Test on the target platform (Windows with NVIDIA RTX 5090)

## Code Review Process

1. All code changes require review
2. Address reviewer feedback
3. Keep PRs focused and reasonably sized
4. Update documentation as needed

## Questions?

Open an issue for questions or discussions.
