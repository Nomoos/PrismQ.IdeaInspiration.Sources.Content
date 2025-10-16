"""Tests for main module."""

import sys
from pathlib import Path

# Add the module src to path for imports
module_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(module_src))

from main import process_example_data  # noqa: E402


def test_process_example_data():
    """Test example data processing function."""
    input_data = "hello world"
    result = process_example_data(input_data)

    assert result["input"] == input_data
    assert result["output"] == "HELLO WORLD"
    assert result["length"] == "11"


def test_process_example_data_empty():
    """Test processing empty string."""
    result = process_example_data("")

    assert result["input"] == ""
    assert result["output"] == ""
    assert result["length"] == "0"


def test_process_example_data_special_chars():
    """Test processing string with special characters."""
    input_data = "Hello, PrismQ! 123"
    result = process_example_data(input_data)

    assert result["input"] == input_data
    assert result["output"] == "HELLO, PRISMQ! 123"
    assert result["length"] == "18"
