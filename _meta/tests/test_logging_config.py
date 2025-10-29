"""Tests for logging configuration module."""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.logging_config import ModuleLogger, get_module_logger, setup_basic_logging


def test_module_logger_initialization():
    """Test ModuleLogger initialization with defaults."""
    logger_obj = ModuleLogger("TestModule")
    assert logger_obj.module_name == "TestModule"
    assert logger_obj.module_version == "0.1.0"
    assert logger_obj.logger is not None
    assert isinstance(logger_obj.logger, logging.Logger)


def test_module_logger_custom_version():
    """Test ModuleLogger with custom version."""
    logger_obj = ModuleLogger("TestModule", module_version="2.0.0")
    assert logger_obj.module_version == "2.0.0"


def test_module_logger_custom_path():
    """Test ModuleLogger with custom path."""
    custom_path = "/custom/path"
    logger_obj = ModuleLogger("TestModule", module_path=custom_path)
    assert logger_obj.module_path == custom_path


def test_module_logger_log_level_from_env():
    """Test ModuleLogger respects LOG_LEVEL environment variable."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        logger_obj = ModuleLogger("TestModule")
        assert logger_obj.log_level == "DEBUG"
        assert logger_obj.logger.level == logging.DEBUG


def test_module_logger_log_level_default():
    """Test ModuleLogger uses INFO as default log level."""
    with patch.dict(os.environ, {}, clear=True):
        logger_obj = ModuleLogger("TestModule")
        assert logger_obj.log_level == "INFO"
        assert logger_obj.logger.level == logging.INFO


def test_module_logger_file_logging():
    """Test ModuleLogger creates file handler when LOG_FILE is set."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = str(Path(tmpdir) / "test.log")
        with patch.dict(os.environ, {"LOG_FILE": log_file}):
            logger_obj = ModuleLogger("TestModule")
            assert logger_obj.log_file == log_file

            # Write a log message
            logger_obj.logger.info("Test message")

            # Verify file was created and contains message
            log_file_path = Path(log_file)
            assert log_file_path.exists()
            content = log_file_path.read_text()
            assert "Test message" in content
            assert "TestModule" in content


def test_module_logger_startup_logging(caplog):
    """Test that module startup logs comprehensive information."""
    with caplog.at_level(logging.INFO):
        logger_obj = ModuleLogger("TestModule", module_version="1.0.0")
        logger_obj.log_module_startup()

        # Verify startup information is logged
        log_text = caplog.text
        assert "MODULE STARTUP" in log_text
        assert "TestModule" in log_text
        assert "1.0.0" in log_text
        assert "Operating System" in log_text
        assert "Python Version" in log_text
        assert "Working Directory" in log_text


def test_module_logger_shutdown_logging(caplog):
    """Test module shutdown logging."""
    with caplog.at_level(logging.INFO):
        logger_obj = ModuleLogger("TestModule")
        logger_obj.log_module_shutdown()

        log_text = caplog.text
        assert "MODULE SHUTDOWN" in log_text
        assert "TestModule" in log_text


def test_get_module_logger_with_startup():
    """Test get_module_logger convenience function."""
    logger = get_module_logger("TestModule", "1.0.0", log_startup=False)
    assert isinstance(logger, logging.Logger)
    assert logger.name == "TestModule"


def test_get_module_logger_startup_default(caplog):
    """Test get_module_logger logs startup by default."""
    with caplog.at_level(logging.INFO):
        _ = get_module_logger("TestModule", "1.0.0")
        assert "MODULE STARTUP" in caplog.text


def test_get_module_logger_no_startup(caplog):
    """Test get_module_logger can skip startup logging."""
    with caplog.at_level(logging.INFO):
        caplog.clear()
        _ = get_module_logger("TestModule", "1.0.0", log_startup=False)
        assert "MODULE STARTUP" not in caplog.text


def test_setup_basic_logging():
    """Test basic logging setup."""
    setup_basic_logging("WARNING")
    root_logger = logging.getLogger()
    assert root_logger.level == logging.WARNING


def test_logger_uses_module_name():
    """Test that logger uses the specified module name."""
    logger = get_module_logger("MySpecialModule", log_startup=False)
    assert logger.name == "MySpecialModule"


def test_multiple_loggers_independent():
    """Test that multiple loggers are independent."""
    logger1 = get_module_logger("Module1", log_startup=False)
    logger2 = get_module_logger("Module2", log_startup=False)

    assert logger1.name == "Module1"
    assert logger2.name == "Module2"
    assert logger1 is not logger2


def test_logger_format_includes_details(caplog):
    """Test that logger format includes filename and line number."""
    logger = get_module_logger("TestModule", log_startup=False)

    with caplog.at_level(logging.INFO):
        logger.info("Test message with details")

        # Check that the log record contains expected fields
        assert len(caplog.records) > 0
        record = caplog.records[-1]
        assert record.filename is not None
        assert record.lineno is not None
        assert "Test message with details" in caplog.text


def test_logger_handles_exceptions(caplog):
    """Test that logger properly handles exception logging."""
    logger = get_module_logger("TestModule", log_startup=False)

    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

        assert "An error occurred" in caplog.text
        assert "ValueError" in caplog.text
        assert "Test exception" in caplog.text
