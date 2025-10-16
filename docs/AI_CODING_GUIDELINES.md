# AI-Assisted Coding Guidelines for PrismQ

This document provides best practices for using AI-powered coding assistants like GitHub Copilot effectively in PrismQ module development. These guidelines help ensure high-quality, maintainable code while leveraging AI assistance.

## 🎯 Overview

AI coding assistants can significantly boost productivity, but they require proper guidance and oversight. This guide covers:
- Effective prompting strategies
- Code review for AI-generated code
- Testing AI-generated code
- Common pitfalls and how to avoid them
- Integration with SOLID principles and PEP standards

---

## 🤖 Understanding AI Coding Assistants

### What AI Assistants Are Good At

✅ **Strengths**:
- Generating boilerplate code quickly
- Implementing common patterns and algorithms
- Writing unit tests based on function signatures
- Creating docstrings and comments
- Refactoring repetitive code
- Suggesting variable and function names
- Implementing standard library usage
- Converting between similar code patterns

### What AI Assistants Struggle With

⚠️ **Limitations**:
- Understanding complex business logic
- Maintaining consistency across large codebases
- Knowing project-specific conventions
- Understanding system architecture
- Making architectural decisions
- Ensuring security best practices
- Optimizing for specific hardware (RTX 5090)
- Understanding domain-specific requirements

---

## 📝 Effective Prompting Strategies

### 1. Provide Context Through Comments

**❌ Poor Prompt**:
```python
# Create user class
```

**✅ Good Prompt**:
```python
# Create a User class that:
# - Follows SOLID principles (single responsibility)
# - Uses type hints for all attributes
# - Validates email format on initialization
# - Has a method to serialize to dict
# - Follows Google-style docstrings
# - Raises ValueError for invalid data
```

### 2. Specify Requirements Explicitly

**❌ Poor Prompt**:
```python
def process_data(data):
    # Process the data
```

**✅ Good Prompt**:
```python
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Process DataFrame by removing nulls and normalizing values.
    
    Requirements:
    - Remove rows with any null values
    - Normalize numeric columns to 0-1 range
    - Convert string columns to lowercase
    - Preserve original column order
    - Should work efficiently on RTX 5090 GPU if using cuDF
    
    Args:
        data: Input DataFrame with mixed types.
        
    Returns:
        Processed DataFrame.
        
    Raises:
        ValueError: If DataFrame is empty.
    """
```

### 3. Reference Existing Patterns

**✅ Good Prompt**:
```python
# Create a DataLoader class similar to the existing ConfigLoader class
# but for loading CSV files instead of JSON configuration.
# Follow the same error handling and logging patterns.
```

### 4. Specify Standards and Principles

**✅ Good Prompt**:
```python
# Implement a file caching system that:
# - Follows Dependency Inversion Principle (use Protocol for storage backend)
# - Adheres to PEP 8 style guide
# - Uses type hints (PEP 484)
# - Implements Google-style docstrings (PEP 257)
# - Has single responsibility (only caching logic)
```

### 5. Break Down Complex Tasks

**✅ Good Approach**:
```python
# Step 1: Create Protocol for data source
# Protocol should define: fetch(), validate(), transform()

# Step 2: Implement CSVDataSource following the Protocol
# Should handle file reading, null checking, type conversion

# Step 3: Implement APIDataSource following the Protocol
# Should handle HTTP requests, JSON parsing, error handling
```

---

## 🔍 Code Review Guidelines for AI-Generated Code

### Always Review for These Issues

#### 1. Type Safety

```python
# ❌ AI might generate untyped code
def process(data):
    return data.strip()

# ✅ Add proper type hints
def process(data: str) -> str:
    """Process string data.
    
    Args:
        data: Input string to process.
        
    Returns:
        Processed string.
    """
    return data.strip()
```

#### 2. Error Handling

```python
# ❌ AI might skip error handling
def divide(a: float, b: float) -> float:
    return a / b

# ✅ Add proper error handling
def divide(a: float, b: float) -> float:
    """Divide two numbers.
    
    Args:
        a: Numerator.
        b: Denominator.
        
    Returns:
        Result of division.
        
    Raises:
        ValueError: If denominator is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

#### 3. SOLID Principles Compliance

```python
# ❌ AI might create classes with multiple responsibilities
class DataHandler:
    def load_data(self): pass
    def process_data(self): pass
    def save_data(self): pass
    def validate_data(self): pass
    def generate_report(self): pass

# ✅ Refactor to follow Single Responsibility Principle
class DataLoader:
    def load(self): pass

class DataProcessor:
    def process(self): pass

class DataValidator:
    def validate(self): pass

class DataSaver:
    def save(self): pass

class ReportGenerator:
    def generate(self): pass
```

#### 4. Security Issues

```python
# ❌ AI might generate unsafe code
def execute_query(query: str) -> list:
    return database.execute(query)  # SQL injection risk!

# ✅ Use parameterized queries
def execute_query(table: str, user_id: int) -> list:
    """Execute safe parameterized query.
    
    Args:
        table: Table name (validated against whitelist).
        user_id: User identifier for filtering.
        
    Returns:
        Query results.
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table}")
    return database.execute(
        "SELECT * FROM ? WHERE user_id = ?",
        (table, user_id)
    )
```

#### 5. Resource Management

```python
# ❌ AI might not handle resources properly
def read_file(path: Path) -> str:
    f = open(path)
    return f.read()  # File not closed!

# ✅ Use context managers
def read_file(path: Path) -> str:
    """Read file contents safely.
    
    Args:
        path: Path to file.
        
    Returns:
        File contents.
    """
    with open(path, "r") as f:
        return f.read()
```

---

## 🧪 Testing AI-Generated Code

### Test Coverage Requirements

All AI-generated code must have tests:

```python
# AI-generated function
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price.
    
    Args:
        price: Original price.
        discount_percent: Discount percentage (0-100).
        
    Returns:
        Discounted price.
        
    Raises:
        ValueError: If inputs are invalid.
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)


# ✅ Comprehensive tests for AI-generated code
import pytest

def test_calculate_discount_valid() -> None:
    """Test valid discount calculation."""
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(100, 50) == 50
    assert calculate_discount(100, 0) == 100

def test_calculate_discount_edge_cases() -> None:
    """Test edge cases."""
    assert calculate_discount(0, 10) == 0
    assert calculate_discount(100, 100) == 0

def test_calculate_discount_invalid_price() -> None:
    """Test invalid price handling."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_discount(-100, 10)

def test_calculate_discount_invalid_percent() -> None:
    """Test invalid discount percentage."""
    with pytest.raises(ValueError, match="Discount must be between"):
        calculate_discount(100, 101)
    with pytest.raises(ValueError, match="Discount must be between"):
        calculate_discount(100, -1)
```

### Integration Tests

Test AI-generated code in context:

```python
# ✅ Test AI-generated code with real dependencies
def test_data_pipeline_integration() -> None:
    """Test full pipeline with AI-generated components."""
    # Setup
    loader = DataLoader()  # AI-generated
    processor = DataProcessor()  # AI-generated
    validator = DataValidator()  # AI-generated
    
    # Execute
    data = loader.load("test_data.csv")
    processed = processor.process(data)
    is_valid = validator.validate(processed)
    
    # Verify
    assert is_valid
    assert len(processed) > 0
```

---

## ⚠️ Common Pitfalls and Solutions

### Pitfall 1: Accepting Code Without Understanding

**Problem**: Blindly accepting AI suggestions without understanding what they do.

**Solution**:
```python
# ❌ Don't do this
# [Accept AI suggestion without reading]

# ✅ Do this:
# 1. Read the AI-generated code carefully
# 2. Understand each line and its purpose
# 3. Verify it follows project standards
# 4. Test edge cases
# 5. Add comments if logic is complex
```

### Pitfall 2: Over-Reliance on AI for Architecture

**Problem**: Using AI to design system architecture.

**Solution**:
- Use AI for implementing components, not designing them
- Create architecture diagrams and design docs yourself
- Use AI to implement well-defined interfaces
- Review AI code for architectural consistency

### Pitfall 3: Inconsistent Code Style

**Problem**: AI generates code in different styles across files.

**Solution**:
```python
# Use .github/copilot-instructions.md to enforce consistency
# Run linters after accepting AI code:
# ruff format .
# ruff check .
# mypy src/
```

### Pitfall 4: Missing Edge Cases

**Problem**: AI code handles happy path but misses edge cases.

**Solution**:
```python
# ✅ Always add edge case handling
def parse_age(age_str: str) -> int:
    """Parse age from string (AI-generated).
    
    Args:
        age_str: Age as string.
        
    Returns:
        Age as integer.
        
    Raises:
        ValueError: If age is invalid.
    """
    # AI-generated code
    age = int(age_str)
    
    # ✅ Add missing edge cases
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    
    return age
```

### Pitfall 5: Incomplete Documentation

**Problem**: AI generates code without proper docstrings.

**Solution**:
```python
# ❌ AI might generate
def process(data):
    return [x * 2 for x in data]

# ✅ Add comprehensive documentation
def process(data: list[int]) -> list[int]:
    """Double each value in the list.
    
    This function is used in the data preprocessing pipeline
    to scale values before normalization.
    
    Args:
        data: List of integer values to process.
        
    Returns:
        List with each value doubled.
        
    Examples:
        >>> process([1, 2, 3])
        [2, 4, 6]
    """
    return [x * 2 for x in data]
```

---

## 🎯 Best Practices for PrismQ Modules

### 1. GPU Optimization Context

When working with GPU code, provide context:

```python
# ✅ Good prompt for GPU code
"""
Create a batch processing function for image preprocessing that:
- Uses PyTorch/CUDA for GPU acceleration on RTX 5090
- Processes batches of 32 images (optimal for 32GB VRAM)
- Uses mixed precision (FP16) for performance
- Includes proper error handling for CUDA OOM
- Has fallback to CPU if GPU unavailable
- Follows SOLID principles (single responsibility)
"""
```

### 2. Integration with PrismQ Ecosystem

```python
# ✅ Specify ecosystem integration
"""
Create a data source adapter that:
- Implements the PrismQ DataSource protocol
- Compatible with PrismQ.IdeaInspiration.Sources format
- Returns data in the standard PrismQ format (see docs/FORMATS.md)
- Follows dependency injection pattern
- Uses type hints and Google-style docstrings
"""
```

### 3. Performance Considerations

```python
# ✅ Specify performance requirements
"""
Implement a caching layer that:
- Uses Redis for distributed caching
- Optimized for Windows environment
- Handles large objects (up to 1GB) efficiently
- Includes TTL and eviction policies
- Thread-safe for parallel processing
- Includes performance metrics logging
"""
```

---

## 📋 AI Code Review Checklist

Before committing AI-generated code, verify:

### Code Quality
- [ ] Follows PEP 8 (run `ruff check .`)
- [ ] Has type hints for all functions (PEP 484/526)
- [ ] Has Google-style docstrings (PEP 257)
- [ ] No security vulnerabilities
- [ ] Proper error handling
- [ ] Resource cleanup (context managers)

### SOLID Principles
- [ ] Single Responsibility Principle
- [ ] Open/Closed Principle
- [ ] Liskov Substitution Principle
- [ ] Interface Segregation Principle
- [ ] Dependency Inversion Principle

### Testing
- [ ] Unit tests written and passing
- [ ] Edge cases covered
- [ ] Integration tests if applicable
- [ ] Test coverage >80%

### Documentation
- [ ] Function/class docstrings complete
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] API documentation current

### Performance
- [ ] Efficient algorithms used
- [ ] No obvious performance issues
- [ ] GPU utilization optimized (if applicable)
- [ ] Memory usage reasonable

---

## 🛠️ Configuring GitHub Copilot

### Using .github/copilot-instructions.md

The repository includes Copilot instructions. Key sections:

```markdown
## Code Style
- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep functions focused and under 50 lines when possible

## SOLID Principles
- Single Responsibility: One class, one purpose
- Open/Closed: Extend, don't modify
- Liskov Substitution: Subtypes must be substitutable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions
```

### Inline Prompts

Use inline comments to guide Copilot:

```python
# Create a Protocol for data validators following ISP
# Should have only: validate() -> bool method
# Use type hints and proper docstring

# Create a concrete validator for email addresses
# Should implement the Protocol above
# Use regex for validation
# Raise ValueError with descriptive message on invalid input
```

---

## 🔄 Iterative Refinement

AI-generated code often needs refinement:

### Initial Generation
```python
# AI first attempt
def load_config(path):
    with open(path) as f:
        return json.load(f)
```

### Refinement 1: Add Types
```python
def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
```

### Refinement 2: Use Path, Add Docstring
```python
def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from JSON file."""
    with open(path) as f:
        return json.load(f)
```

### Final Version: Complete Implementation
```python
def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        path: Path to JSON configuration file.
        
    Returns:
        Configuration dictionary.
        
    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If file is not valid JSON.
        
    Examples:
        >>> config = load_config(Path("config.json"))
        >>> print(config["app_name"])
        'PrismQ'
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in config file: {path}",
            e.doc,
            e.pos
        )
```

---

## 📊 Measuring AI Assistance Effectiveness

### Metrics to Track

1. **Time Saved**: Compare development time with and without AI
2. **Code Quality**: Run static analysis on AI-generated code
3. **Bug Rate**: Track bugs in AI vs. manually written code
4. **Test Coverage**: Ensure AI code meets coverage targets
5. **Review Time**: Track time spent reviewing AI code

### Quality Gates

Set thresholds for AI-generated code:
- Minimum test coverage: 80%
- Maximum cyclomatic complexity: 10
- MyPy strict mode: 0 errors
- Ruff violations: 0
- Security scan: No critical issues

---

## 🎓 Training Tips

### Learn to Prompt Effectively

**Practice these prompting patterns**:

1. **Pattern-based prompting**:
   ```python
   # Create a class similar to DataLoader but for API endpoints
   # Follow the same structure and error handling
   ```

2. **Constraint-based prompting**:
   ```python
   # Function must:
   # - Be pure (no side effects)
   # - Handle None inputs gracefully
   # - Return empty list on error (don't raise)
   ```

3. **Example-driven prompting**:
   ```python
   # Create a function that works like this:
   # >>> process([1, 2, 3], factor=2)
   # [2, 4, 6]
   # >>> process([], factor=2)
   # []
   ```

### Continuous Learning

- Review AI suggestions before accepting
- Understand why AI suggests certain patterns
- Learn from good AI-generated code
- Identify and report AI hallucinations
- Stay updated on AI coding assistant features

---

## 🔗 Integration with Other Standards

AI-generated code must comply with:
- **[SOLID Principles](SOLID_PRINCIPLES.md)**: Design guidelines
- **[PEP Standards](PEP_STANDARDS.md)**: Python best practices
- **[Contributing Guide](CONTRIBUTING.md)**: Development workflow
- **[Copilot Instructions](.github/copilot-instructions.md)**: Project-specific rules

---

## 📚 Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [OpenAI Codex Research](https://openai.com/blog/openai-codex)
- [AI-Assisted Programming Best Practices](https://martinfowler.com/articles/ai-assisted-programming.html)
- [Testing AI-Generated Code](https://testing.googleblog.com/)

---

## 🎯 Summary

Effective use of AI coding assistants in PrismQ modules requires:

1. **Clear Context**: Provide detailed prompts with requirements
2. **Critical Review**: Always review and understand AI code
3. **Quality Standards**: Ensure compliance with SOLID and PEP standards
4. **Comprehensive Testing**: Test all AI-generated code thoroughly
5. **Iterative Refinement**: Improve AI suggestions incrementally
6. **Security Awareness**: Watch for security issues in AI code
7. **Documentation**: Complete all docstrings and comments

AI is a powerful tool for productivity, but human oversight ensures quality, security, and maintainability. Use AI to accelerate development, not replace critical thinking and architectural design.
