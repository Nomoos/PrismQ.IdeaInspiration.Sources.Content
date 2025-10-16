# SOLID Principles for PrismQ

This document outlines the SOLID principles and additional design principles that should guide code development in all PrismQ modules. These principles ensure maintainable, testable, and scalable code.

## 🎯 Overview

SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

## 📚 The SOLID Principles

### 1. Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change, meaning it should have only one job or responsibility.

**Why It Matters**:
- Easier to understand and maintain
- Reduces coupling between components
- Changes in one area don't affect others
- Easier to test in isolation

**Python Example**:

```python
# ❌ BAD: Multiple responsibilities
class DataHandler:
    """Handles data loading, processing, and saving."""
    
    def load_data(self, path: Path) -> pd.DataFrame:
        """Load data from file."""
        return pd.read_csv(path)
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process the data."""
        # Complex processing logic
        return data.dropna()
    
    def save_data(self, data: pd.DataFrame, path: Path) -> None:
        """Save data to file."""
        data.to_csv(path, index=False)
    
    def generate_report(self, data: pd.DataFrame) -> str:
        """Generate HTML report."""
        return f"<html>{data.to_html()}</html>"


# ✅ GOOD: Single responsibility per class
class DataLoader:
    """Responsible only for loading data."""
    
    def load(self, path: Path) -> pd.DataFrame:
        """Load data from CSV file.
        
        Args:
            path: Path to the CSV file.
            
        Returns:
            Loaded DataFrame.
        """
        return pd.read_csv(path)


class DataProcessor:
    """Responsible only for processing data."""
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data by removing null values.
        
        Args:
            data: Input DataFrame.
            
        Returns:
            Processed DataFrame.
        """
        return data.dropna()


class DataSaver:
    """Responsible only for saving data."""
    
    def save(self, data: pd.DataFrame, path: Path) -> None:
        """Save data to CSV file.
        
        Args:
            data: DataFrame to save.
            path: Destination path.
        """
        data.to_csv(path, index=False)


class ReportGenerator:
    """Responsible only for generating reports."""
    
    def generate_html(self, data: pd.DataFrame) -> str:
        """Generate HTML report from data.
        
        Args:
            data: DataFrame to convert to HTML.
            
        Returns:
            HTML string representation.
        """
        return f"<html>{data.to_html()}</html>"
```

---

### 2. Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

**Why It Matters**:
- Add new functionality without changing existing code
- Reduces risk of breaking existing functionality
- Promotes code reusability
- Easier to maintain and test

**Python Example**:

```python
from abc import ABC, abstractmethod
from typing import Any

# ❌ BAD: Requires modification to add new formats
class DataExporter:
    """Export data to various formats."""
    
    def export(self, data: pd.DataFrame, format: str, path: Path) -> None:
        """Export data in specified format."""
        if format == "csv":
            data.to_csv(path)
        elif format == "json":
            data.to_json(path)
        elif format == "excel":  # Adding this requires modifying the class
            data.to_excel(path)
        # Adding new formats requires modifying this method


# ✅ GOOD: Open for extension, closed for modification
class DataExporter(ABC):
    """Abstract base class for data exporters."""
    
    @abstractmethod
    def export(self, data: pd.DataFrame, path: Path) -> None:
        """Export data to file.
        
        Args:
            data: DataFrame to export.
            path: Destination path.
        """
        pass


class CSVExporter(DataExporter):
    """Export data to CSV format."""
    
    def export(self, data: pd.DataFrame, path: Path) -> None:
        """Export data to CSV file."""
        data.to_csv(path, index=False)


class JSONExporter(DataExporter):
    """Export data to JSON format."""
    
    def export(self, data: pd.DataFrame, path: Path) -> None:
        """Export data to JSON file."""
        data.to_json(path, orient="records")


class ExcelExporter(DataExporter):
    """Export data to Excel format."""
    
    def export(self, data: pd.DataFrame, path: Path) -> None:
        """Export data to Excel file."""
        data.to_excel(path, index=False)


# Usage
def save_data(data: pd.DataFrame, exporter: DataExporter, path: Path) -> None:
    """Save data using specified exporter.
    
    Args:
        data: DataFrame to save.
        exporter: Exporter instance.
        path: Destination path.
    """
    exporter.export(data, path)
```

---

### 3. Liskov Substitution Principle (LSP)

**Definition**: Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

**Why It Matters**:
- Ensures inheritance is used correctly
- Prevents unexpected behavior when using polymorphism
- Makes code more predictable and reliable
- Enables proper abstraction

**Python Example**:

```python
from typing import Protocol

# ❌ BAD: Violates LSP
class Bird:
    """Base bird class."""
    
    def fly(self) -> None:
        """Make the bird fly."""
        print("Flying...")


class Penguin(Bird):
    """Penguin can't fly, violates LSP."""
    
    def fly(self) -> None:
        """Penguins can't fly!"""
        raise NotImplementedError("Penguins can't fly!")


# ✅ GOOD: Respects LSP
class Bird(Protocol):
    """Protocol for all birds."""
    
    def move(self) -> None:
        """Move the bird."""
        ...


class FlyingBird:
    """Base class for birds that can fly."""
    
    def move(self) -> None:
        """Move by flying."""
        self.fly()
    
    def fly(self) -> None:
        """Make the bird fly."""
        print("Flying...")


class Sparrow(FlyingBird):
    """Sparrow can fly."""
    
    def fly(self) -> None:
        """Sparrow flies."""
        print("Sparrow flying...")


class Penguin:
    """Penguin moves differently."""
    
    def move(self) -> None:
        """Move by swimming."""
        self.swim()
    
    def swim(self) -> None:
        """Penguin swims."""
        print("Swimming...")


# Usage - any bird can move
def make_bird_move(bird: Bird) -> None:
    """Make any bird move.
    
    Args:
        bird: Any object implementing the Bird protocol.
    """
    bird.move()
```

---

### 4. Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they do not use.

**Why It Matters**:
- Prevents bloated interfaces
- Reduces coupling
- Makes code more modular
- Easier to implement and test

**Python Example**:

```python
from typing import Protocol

# ❌ BAD: Fat interface forces unnecessary dependencies
class Worker(Protocol):
    """Worker interface with too many responsibilities."""
    
    def work(self) -> None:
        """Do work."""
        ...
    
    def eat(self) -> None:
        """Eat food."""
        ...
    
    def sleep(self) -> None:
        """Sleep."""
        ...


class HumanWorker:
    """Human worker can do everything."""
    
    def work(self) -> None:
        print("Working...")
    
    def eat(self) -> None:
        print("Eating...")
    
    def sleep(self) -> None:
        print("Sleeping...")


class RobotWorker:
    """Robot doesn't eat or sleep, but forced to implement them."""
    
    def work(self) -> None:
        print("Working...")
    
    def eat(self) -> None:
        raise NotImplementedError("Robots don't eat!")
    
    def sleep(self) -> None:
        raise NotImplementedError("Robots don't sleep!")


# ✅ GOOD: Segregated interfaces
class Workable(Protocol):
    """Interface for working."""
    
    def work(self) -> None:
        """Do work."""
        ...


class Eatable(Protocol):
    """Interface for eating."""
    
    def eat(self) -> None:
        """Eat food."""
        ...


class Sleepable(Protocol):
    """Interface for sleeping."""
    
    def sleep(self) -> None:
        """Sleep."""
        ...


class HumanWorker:
    """Human implements all interfaces."""
    
    def work(self) -> None:
        print("Working...")
    
    def eat(self) -> None:
        print("Eating...")
    
    def sleep(self) -> None:
        print("Sleeping...")


class RobotWorker:
    """Robot only implements what it needs."""
    
    def work(self) -> None:
        print("Working...")


# Usage
def manage_work(worker: Workable) -> None:
    """Manage worker's work.
    
    Args:
        worker: Any object that can work.
    """
    worker.work()


def manage_break(worker: Eatable & Sleepable) -> None:
    """Manage worker's break.
    
    Args:
        worker: Any object that can eat and sleep.
    """
    worker.eat()
    worker.sleep()
```

---

### 5. Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

**Why It Matters**:
- Reduces coupling between components
- Makes code more testable (easier to mock)
- Enables flexibility in implementation
- Promotes code reusability

**Python Example**:

```python
from abc import ABC, abstractmethod
from typing import Protocol

# ❌ BAD: High-level module depends on low-level module
class MySQLDatabase:
    """MySQL database implementation."""
    
    def connect(self) -> None:
        """Connect to MySQL."""
        print("Connecting to MySQL...")
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL query."""
        print(f"Executing: {sql}")
        return []


class UserRepository:
    """User repository tightly coupled to MySQL."""
    
    def __init__(self) -> None:
        self.db = MySQLDatabase()  # Direct dependency on concrete class
    
    def get_user(self, user_id: int) -> dict[str, Any]:
        """Get user by ID."""
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")[0]


# ✅ GOOD: Both depend on abstraction
class Database(Protocol):
    """Database abstraction."""
    
    def connect(self) -> None:
        """Connect to database."""
        ...
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute query."""
        ...


class MySQLDatabase:
    """MySQL implementation."""
    
    def connect(self) -> None:
        """Connect to MySQL."""
        print("Connecting to MySQL...")
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute MySQL query."""
        print(f"Executing on MySQL: {sql}")
        return []


class PostgreSQLDatabase:
    """PostgreSQL implementation."""
    
    def connect(self) -> None:
        """Connect to PostgreSQL."""
        print("Connecting to PostgreSQL...")
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute PostgreSQL query."""
        print(f"Executing on PostgreSQL: {sql}")
        return []


class UserRepository:
    """User repository depends on abstraction."""
    
    def __init__(self, database: Database) -> None:
        """Initialize with database dependency.
        
        Args:
            database: Database implementation.
        """
        self.db = database  # Depends on abstraction
    
    def get_user(self, user_id: int) -> dict[str, Any]:
        """Get user by ID.
        
        Args:
            user_id: User identifier.
            
        Returns:
            User data dictionary.
        """
        self.db.connect()
        results = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return results[0] if results else {}


# Usage - can switch databases easily
mysql_repo = UserRepository(MySQLDatabase())
postgres_repo = UserRepository(PostgreSQLDatabase())
```

---

## 🔧 Additional Design Principles

### DRY (Don't Repeat Yourself)

**Definition**: Every piece of knowledge should have a single, unambiguous representation within a system.

**Example**:

```python
# ❌ BAD: Code duplication
def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email.split("@")[1]

def process_user_email(email: str) -> None:
    """Process user email."""
    if "@" in email and "." in email.split("@")[1]:
        print(f"Valid email: {email}")

def send_email(email: str, message: str) -> None:
    """Send email."""
    if "@" in email and "." in email.split("@")[1]:
        print(f"Sending to {email}: {message}")


# ✅ GOOD: Single source of truth
def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    return "@" in email and "." in email.split("@")[1]

def process_user_email(email: str) -> None:
    """Process user email.
    
    Args:
        email: Email address to process.
    """
    if validate_email(email):
        print(f"Valid email: {email}")

def send_email(email: str, message: str) -> None:
    """Send email.
    
    Args:
        email: Recipient email address.
        message: Message to send.
    """
    if validate_email(email):
        print(f"Sending to {email}: {message}")
```

---

### KISS (Keep It Simple, Stupid)

**Definition**: Simplicity should be a key goal in design. Avoid unnecessary complexity.

**Example**:

```python
# ❌ BAD: Over-engineered solution
class NumberProcessor:
    """Complex number processor."""
    
    def __init__(self) -> None:
        self.operations: dict[str, Callable] = {
            "even": self._is_even,
            "odd": self._is_odd,
        }
    
    def _is_even(self, n: int) -> bool:
        return n % 2 == 0
    
    def _is_odd(self, n: int) -> bool:
        return n % 2 != 0
    
    def process(self, numbers: list[int], operation: str) -> list[int]:
        """Process numbers with operation."""
        return [n for n in numbers if self.operations[operation](n)]


# ✅ GOOD: Simple and clear
def get_even_numbers(numbers: list[int]) -> list[int]:
    """Get even numbers from list.
    
    Args:
        numbers: List of integers.
        
    Returns:
        List of even integers.
    """
    return [n for n in numbers if n % 2 == 0]

def get_odd_numbers(numbers: list[int]) -> list[int]:
    """Get odd numbers from list.
    
    Args:
        numbers: List of integers.
        
    Returns:
        List of odd integers.
    """
    return [n for n in numbers if n % 2 != 0]
```

---

### YAGNI (You Aren't Gonna Need It)

**Definition**: Don't add functionality until it's necessary.

**Example**:

```python
# ❌ BAD: Adding features that might be needed later
class UserService:
    """User service with unnecessary features."""
    
    def create_user(self, username: str, email: str) -> dict[str, Any]:
        """Create user."""
        user = {"username": username, "email": email}
        
        # These might be needed later... or might not
        self._log_creation(user)
        self._send_welcome_email(user)
        self._create_default_preferences(user)
        self._setup_user_analytics(user)
        self._initialize_user_cache(user)
        
        return user


# ✅ GOOD: Only implement what's needed now
class UserService:
    """User service with only required features."""
    
    def create_user(self, username: str, email: str) -> dict[str, Any]:
        """Create user.
        
        Args:
            username: User's username.
            email: User's email address.
            
        Returns:
            Created user data.
        """
        user = {"username": username, "email": email}
        return user
    
    # Add other features when actually needed
```

---

### Composition Over Inheritance

**Definition**: Favor object composition over class inheritance to achieve code reuse.

**Example**:

```python
# ❌ BAD: Deep inheritance hierarchy
class Animal:
    """Base animal class."""
    
    def move(self) -> None:
        """Move the animal."""
        pass

class Swimmer(Animal):
    """Animal that can swim."""
    
    def swim(self) -> None:
        """Swim."""
        print("Swimming...")

class Walker(Animal):
    """Animal that can walk."""
    
    def walk(self) -> None:
        """Walk."""
        print("Walking...")

class Duck(Swimmer, Walker):
    """Duck can swim and walk - complex inheritance."""
    pass


# ✅ GOOD: Use composition
class SwimBehavior:
    """Swimming behavior."""
    
    def swim(self) -> None:
        """Swim."""
        print("Swimming...")

class WalkBehavior:
    """Walking behavior."""
    
    def walk(self) -> None:
        """Walk."""
        print("Walking...")

class Duck:
    """Duck uses composition for behaviors."""
    
    def __init__(self) -> None:
        """Initialize duck with behaviors."""
        self.swim_behavior = SwimBehavior()
        self.walk_behavior = WalkBehavior()
    
    def swim(self) -> None:
        """Delegate to swim behavior."""
        self.swim_behavior.swim()
    
    def walk(self) -> None:
        """Delegate to walk behavior."""
        self.walk_behavior.walk()
```

---

## 🎯 Python-Specific Best Practices

### Use Protocols for Duck Typing

Python's `typing.Protocol` enables structural subtyping (duck typing with type safety):

```python
from typing import Protocol

class Drawable(Protocol):
    """Protocol for drawable objects."""
    
    def draw(self) -> None:
        """Draw the object."""
        ...

class Circle:
    """Circle doesn't inherit from Drawable but implements it."""
    
    def draw(self) -> None:
        """Draw circle."""
        print("Drawing circle")

def render(obj: Drawable) -> None:
    """Render any drawable object.
    
    Args:
        obj: Object implementing Drawable protocol.
    """
    obj.draw()

# Works without inheritance!
render(Circle())
```

### Dependency Injection

Use dependency injection for better testability:

```python
from typing import Protocol

class EmailService(Protocol):
    """Email service protocol."""
    
    def send(self, to: str, message: str) -> None:
        """Send email."""
        ...

class SMTPEmailService:
    """SMTP email implementation."""
    
    def send(self, to: str, message: str) -> None:
        """Send email via SMTP."""
        print(f"Sending via SMTP to {to}: {message}")

class MockEmailService:
    """Mock for testing."""
    
    def __init__(self) -> None:
        self.sent_emails: list[tuple[str, str]] = []
    
    def send(self, to: str, message: str) -> None:
        """Record email for testing."""
        self.sent_emails.append((to, message))

class UserNotifier:
    """Notifier with injected dependency."""
    
    def __init__(self, email_service: EmailService) -> None:
        """Initialize with email service.
        
        Args:
            email_service: Email service implementation.
        """
        self.email_service = email_service
    
    def notify(self, user_email: str, message: str) -> None:
        """Notify user.
        
        Args:
            user_email: User's email address.
            message: Notification message.
        """
        self.email_service.send(user_email, message)

# Production
notifier = UserNotifier(SMTPEmailService())

# Testing
mock_service = MockEmailService()
test_notifier = UserNotifier(mock_service)
test_notifier.notify("user@example.com", "Hello")
assert mock_service.sent_emails == [("user@example.com", "Hello")]
```

---

## 🧪 Testing with SOLID Principles

SOLID principles make code more testable:

```python
import pytest
from typing import Protocol

# Interface for database (DIP)
class Database(Protocol):
    """Database protocol."""
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Execute query."""
        ...

# Single responsibility (SRP)
class UserService:
    """Service for user operations."""
    
    def __init__(self, database: Database) -> None:
        """Initialize with database dependency.
        
        Args:
            database: Database implementation.
        """
        self.db = database
    
    def get_user(self, user_id: int) -> dict[str, Any]:
        """Get user by ID.
        
        Args:
            user_id: User identifier.
            
        Returns:
            User data.
        """
        results = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return results[0] if results else {}

# Easy to test with mock
class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self, data: list[dict[str, Any]]) -> None:
        """Initialize with test data.
        
        Args:
            data: Test data to return.
        """
        self.data = data
    
    def query(self, sql: str) -> list[dict[str, Any]]:
        """Return test data.
        
        Args:
            sql: SQL query (ignored in mock).
            
        Returns:
            Test data.
        """
        return self.data

# Test
def test_get_user() -> None:
    """Test getting user."""
    test_data = [{"id": 1, "name": "John"}]
    mock_db = MockDatabase(test_data)
    service = UserService(mock_db)
    
    user = service.get_user(1)
    assert user == {"id": 1, "name": "John"}
```

---

## 📋 Checklist for Code Review

When reviewing code, check for SOLID compliance:

- [ ] **SRP**: Does each class have a single, well-defined responsibility?
- [ ] **OCP**: Can new functionality be added without modifying existing code?
- [ ] **LSP**: Can subclasses be used interchangeably with their base classes?
- [ ] **ISP**: Are interfaces focused and minimal?
- [ ] **DIP**: Do high-level modules depend on abstractions, not concrete implementations?
- [ ] **DRY**: Is there no duplicated logic?
- [ ] **KISS**: Is the solution as simple as possible?
- [ ] **YAGNI**: Is all code necessary for current requirements?
- [ ] Is composition preferred over inheritance?
- [ ] Are dependencies injected rather than hard-coded?

---

## 🔗 Integration with PrismQ Standards

SOLID principles complement other PrismQ standards:

- **PEP 8**: SOLID helps create well-organized code that naturally follows style guidelines
- **PEP 484/526**: Type hints make SOLID abstractions explicit and verifiable
- **PEP 544**: Protocols are ideal for implementing Interface Segregation and Dependency Inversion
- **Testing**: SOLID makes unit testing easier with isolated, mockable components

---

## 📚 References

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)

---

## 🎯 Summary

Following SOLID principles in PrismQ modules ensures:
- **Maintainability**: Code is easier to understand and modify
- **Testability**: Components can be tested in isolation
- **Flexibility**: New features can be added with minimal changes
- **Reliability**: Reduced coupling means fewer breaking changes
- **Scalability**: Well-designed code grows with your needs

Apply these principles from the start of every PrismQ module to build robust, professional-grade software.
