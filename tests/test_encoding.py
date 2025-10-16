"""Tests for UTF-8 encoding configuration."""

from pathlib import Path


def test_gitattributes_exists() -> None:
    """Test that .gitattributes file exists."""
    gitattributes_path = Path(".gitattributes")
    assert gitattributes_path.exists(), ".gitattributes file should exist"
    assert gitattributes_path.is_file(), ".gitattributes should be a file"


def test_gitattributes_contains_utf8() -> None:
    """Test that .gitattributes contains UTF-8 encoding settings."""
    gitattributes_path = Path(".gitattributes")
    content = gitattributes_path.read_text(encoding="utf-8")

    # Check for UTF-8 encoding declarations
    assert "encoding=UTF-8" in content, ".gitattributes should specify UTF-8 encoding"
    assert "*.py text eol=lf encoding=UTF-8" in content, "Python files should use UTF-8"
    assert "*.md text eol=lf encoding=UTF-8" in content, "Markdown files should use UTF-8"
    assert "*.json text eol=lf encoding=UTF-8" in content, "JSON files should use UTF-8"


def test_editorconfig_exists() -> None:
    """Test that .editorconfig file exists."""
    editorconfig_path = Path(".editorconfig")
    assert editorconfig_path.exists(), ".editorconfig file should exist"
    assert editorconfig_path.is_file(), ".editorconfig should be a file"


def test_editorconfig_contains_utf8() -> None:
    """Test that .editorconfig contains UTF-8 charset settings."""
    editorconfig_path = Path(".editorconfig")
    content = editorconfig_path.read_text(encoding="utf-8")

    # Check for UTF-8 charset declarations
    assert "charset = utf-8" in content, ".editorconfig should specify utf-8 charset"
    assert "root = true" in content, ".editorconfig should be marked as root"


def test_python_files_can_use_utf8() -> None:
    """Test that Python files can be read/written with UTF-8 encoding."""
    test_file = Path("temp_utf8_test.py")

    try:
        # Test writing UTF-8 content with Unicode characters and emoji
        # Note: No need for '# -*- coding: utf-8 -*-' in Python 3+ (UTF-8 is default)
        utf8_content = (
            "# Test UTF-8 encoding with Unicode and emoji\n"
            "text = 'Hello 世界 🌍'\n"
            "print(f'UTF-8 works! {text}')\n"
        )
        test_file.write_text(utf8_content, encoding="utf-8")

        # Test reading UTF-8 content
        read_content = test_file.read_text(encoding="utf-8")
        assert read_content == utf8_content, "UTF-8 content should be preserved"
        assert "世界" in read_content, "Unicode characters should be preserved"
        assert "🌍" in read_content, "Emoji should be preserved"
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()


def test_gitattributes_line_endings() -> None:
    """Test that .gitattributes properly configures line endings."""
    gitattributes_path = Path(".gitattributes")
    content = gitattributes_path.read_text(encoding="utf-8")

    # Check for line ending configurations
    assert "text=auto eol=lf" in content, "Auto text detection with LF should be configured"
    assert "*.bat text eol=crlf" in content, "Windows batch files should use CRLF"
    assert "*.sh text eol=lf" in content, "Shell scripts should use LF"


def test_editorconfig_line_endings() -> None:
    """Test that .editorconfig properly configures line endings."""
    editorconfig_path = Path(".editorconfig")
    content = editorconfig_path.read_text(encoding="utf-8")

    # Check for line ending configurations
    assert "end_of_line = lf" in content, "Default line ending should be LF"
    # Windows batch files should use CRLF
    # Note: Simple string check is sufficient for this validation test.
    # A full parser would be overkill for just verifying the config is present.
    lines = content.split("\n")
    in_bat_section = False
    for line in lines:
        if "[*.{bat,cmd}]" in line:
            in_bat_section = True
        elif in_bat_section and "end_of_line" in line:
            assert "crlf" in line, "Batch files should use CRLF line endings"
            break
