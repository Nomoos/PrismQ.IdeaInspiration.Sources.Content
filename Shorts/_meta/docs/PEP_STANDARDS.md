# PEP Standards for PrismQ

This document outlines the Python Enhancement Proposals (PEPs) that govern the design, structure, and development workflow of PrismQ modules.

## 📋 Adopted PEPs

### Packaging & Project Metadata

#### PEP 517 & 518 - Build System Interface
**Status**: ✅ Implemented

The project uses `pyproject.toml` as the single source of configuration, with `setuptools` as the build backend.

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"
```

**Benefits**:
- Modern, standardized build process
- Reproducible builds
- Better tooling support

---

#### PEP 621 - Project Metadata in pyproject.toml
**Status**: ✅ Implemented

All project metadata (name, version, dependencies, etc.) is declared in `pyproject.toml`:

```toml
[project]
name = "prismq-module-template"
version = "0.1.0"
description = "PrismQ module template for AI-powered content generation"
requires-python = ">=3.10"
dependencies = [...]
```

**Benefits**:
- Single source of truth for metadata
- Tool-agnostic configuration
- Better dependency management

---

#### PEP 660 - Editable Installs
**Status**: ✅ Supported

The project supports editable installs for development:

```bash
pip install -e .[dev]
```

**Benefits**:
- Live code changes without reinstallation
- Faster development iteration
- Easier debugging

---

#### PEP 440 - Version Identification
**Status**: ✅ Implemented

The project follows PEP 440 versioning scheme: `MAJOR.MINOR.PATCH`

```python
__version__ = "0.1.0"
```

**Benefits**:
- Clear versioning semantics
- Compatibility with packaging tools
- Predictable upgrade paths

---

#### PEP 508 - Dependency Specification
**Status**: ✅ Implemented

Dependencies are specified using PEP 508 syntax in `pyproject.toml`:

```toml
dependencies = [
    "python-dotenv>=1.0.0",
]
```

**Benefits**:
- Flexible dependency requirements
- Environment markers support
- Extra dependencies grouping

---

#### PEP 420 - Namespace Packages
**Status**: ✅ Configured

The project is configured to support namespace packages for modular design:

```toml
[tool.mypy]
namespace_packages = true
explicit_package_bases = true
```

**Benefits**:
- Split packages across multiple directories
- Better modularity for large projects
- Cleaner project structure

---

### Code Style & Documentation

#### PEP 8 - Style Guide for Python Code
**Status**: ✅ Enforced via Ruff

The project enforces PEP 8 compliance using Ruff:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "W", "F", ...]  # PEP 8 checks enabled
```

**Key Guidelines**:
- 100 characters line length (optimized for modern displays)
- 4 spaces for indentation
- Clear naming conventions
- Consistent formatting

**Usage**:
```bash
ruff check .          # Check for violations
ruff check --fix .    # Auto-fix violations
ruff format .         # Format code
```

---

#### PEP 257 - Docstring Conventions
**Status**: ✅ Enforced via Ruff

The project enforces Google-style docstrings:

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"
```

**Example**:
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Longer description if needed, explaining the function's
    purpose and behavior.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When invalid parameters are provided.
    """
    return True
```

**Usage**:
```bash
ruff check --select D .  # Check docstrings only
```

---

### Typing

#### PEP 484 - Type Hints
**Status**: ✅ Enforced via MyPy & Ruff

All functions must have type hints:

```python
def process_data(input_file: Path, verbose: bool = False) -> dict[str, Any]:
    """Process data from input file."""
    ...
```

**Configuration**:
```toml
[tool.mypy]
disallow_untyped_defs = true
disallow_untyped_calls = true

[tool.ruff.lint]
select = ["ANN"]  # Enforce annotations
```

---

#### PEP 526 - Variable Annotations
**Status**: ✅ Enforced

Class and instance variables must be annotated:

```python
class Config:
    """Configuration class."""
    
    app_name: str
    debug: bool
    cache_dir: Path
    
    def __init__(self) -> None:
        self.app_name: str = "PrismQ"
        self.debug: bool = False
        self.cache_dir: Path = Path("./cache")
```

---

#### PEP 544 - Protocols (Structural Subtyping)
**Status**: ✅ Supported

Use protocols for interface definitions:

```python
from typing import Protocol

class DataProcessor(Protocol):
    """Protocol for data processors."""
    
    def process(self, data: str) -> dict[str, Any]:
        """Process data."""
        ...

class JSONProcessor:
    """Concrete implementation."""
    
    def process(self, data: str) -> dict[str, Any]:
        """Process JSON data."""
        return json.loads(data)
```

**Benefits**:
- Duck typing with type safety
- Flexible interfaces
- Better code reuse

---

#### PEP 561 - Distributing Type Information
**Status**: ✅ Implemented

The package includes a `py.typed` marker for type hint distribution:

```
src/
├── __init__.py
├── py.typed      # Marker file
├── main.py
└── config.py
```

**Benefits**:
- Type checkers can use our type hints
- Better IDE support for users
- Type-safe package consumption

---

### Environments & Imports

#### PEP 405 - Virtual Environments
**Status**: ✅ Documented

Virtual environments are created using the built-in `venv` module:

```bash
python -m venv venv
venv\Scripts\activate
```

**Benefits**:
- Isolated dependencies
- Reproducible environments
- No conflicts with system packages

---

#### PEP 328 - Absolute/Relative Imports
**Status**: ✅ Configured

Prefer absolute imports for clarity:

```python
# Good - Absolute import
from src.config import Config
from src.utils.helpers import process_data

# Avoid - Relative imports in large codebases
from ..config import Config
from .helpers import process_data
```

**Configuration**:
```toml
[tool.ruff.lint]
select = ["I"]  # isort for import ordering
```

**Benefits**:
- Clear module references
- Easier refactoring
- Better IDE support

---

## 🚫 Not Adopted (Out of Scope)

The following PEP categories are **not** explicitly adopted as they are:
- Handled by Python interpreter version (Python 3.10+)
- Core CPython implementation details
- Rejected or superseded proposals

### Examples:
- **Syntax PEPs** (e.g., PEP 634 - Pattern Matching): Handled by Python 3.10+
- **Runtime PEPs** (e.g., PEP 554 - Multiple Interpreters): CPython implementation
- **Rejected PEPs**: Only of historical interest

---

## 🔧 Development Workflow

### Initial Setup
```bash
# Create virtual environment (PEP 405)
python -m venv venv
venv\Scripts\activate

# Install in editable mode (PEP 660)
pip install -e .[dev]
```

### Code Quality Checks
```bash
# Format code (PEP 8)
ruff format .

# Lint code (PEP 8, PEP 257)
ruff check .

# Type check (PEP 484, 526, 544, 561)
mypy src/

# Run tests
pytest
```

### Pre-commit Checklist
- [ ] Code formatted with Ruff
- [ ] No Ruff violations
- [ ] MyPy passes with no errors
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Type hints added to new code
- [ ] Docstrings added (Google style)

---

## 📚 References

- [PEP 0 - Index of Python Enhancement Proposals](https://peps.python.org/pep-0000/)
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)

---

## 🎯 Summary

PrismQ follows modern Python best practices by adopting relevant PEPs for:
- **Packaging**: PEP 517, 518, 621, 660
- **Versioning**: PEP 440, 508
- **Code Quality**: PEP 8, 257
- **Type Safety**: PEP 484, 526, 544, 561
- **Development**: PEP 405, 328, 420

This ensures code quality, maintainability, and compatibility across the PrismQ ecosystem.
