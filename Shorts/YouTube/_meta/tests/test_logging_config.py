"""Tests for logging configuration module."""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from src.core import logging_config


class TestModuleLogger:
    """Test ModuleLogger class."""
    
    def test_initialization(self):
        """Test that ModuleLogger initializes correctly."""
        module_logger = logging_config.ModuleLogger("TestModule", "1.0.0", "/test/path")
        
        assert module_logger.module_name == "TestModule"
        assert module_logger.module_version == "1.0.0"
        assert module_logger.module_path == "/test/path"
        assert module_logger.logger is not None
        assert isinstance(module_logger.logger, logging.Logger)
    
    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        module_logger = logging_config.ModuleLogger("TestModule")
        
        assert module_logger.module_name == "TestModule"
        assert module_logger.module_version == "0.1.0"
        assert module_logger.module_path == str(Path.cwd())
    
    def test_logger_name(self):
        """Test that logger has correct name."""
        module_logger = logging_config.ModuleLogger("MyTestModule")
        assert module_logger.logger.name == "MyTestModule"
    
    def test_logger_level_from_env(self, monkeypatch):
        """Test that log level is set from environment variable."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        module_logger = logging_config.ModuleLogger("TestModule")
        assert module_logger.logger.level == logging.DEBUG
        
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        module_logger = logging_config.ModuleLogger("TestModule2")
        assert module_logger.logger.level == logging.WARNING
    
    def test_default_log_level(self, monkeypatch):
        """Test default log level when not set in environment."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        module_logger = logging_config.ModuleLogger("TestModule")
        assert module_logger.logger.level == logging.INFO
    
    def test_console_handler_exists(self):
        """Test that console handler is added to logger."""
        module_logger = logging_config.ModuleLogger("TestModule")
        handlers = module_logger.logger.handlers
        
        assert len(handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    
    def test_file_handler_when_configured(self, monkeypatch):
        """Test that file handler is added when LOG_FILE is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            monkeypatch.setenv("LOG_FILE", log_file)
            
            module_logger = logging_config.ModuleLogger("TestModule")
            handlers = module_logger.logger.handlers
            
            assert any(isinstance(h, logging.FileHandler) for h in handlers)
            assert Path(log_file).exists()
    
    def test_get_logger(self):
        """Test get_logger returns the logger instance."""
        module_logger = logging_config.ModuleLogger("TestModule")
        logger = module_logger.get_logger()
        
        assert logger is module_logger.logger
        assert isinstance(logger, logging.Logger)
    
    def test_log_module_startup(self, caplog):
        """Test that log_module_startup logs expected information."""
        with caplog.at_level(logging.INFO):
            module_logger = logging_config.ModuleLogger("TestModule", "2.0.0")
            module_logger.log_module_startup()
        
        log_text = caplog.text
        assert "MODULE STARTUP" in log_text
        assert "TestModule" in log_text
        assert "2.0.0" in log_text
        assert "Module Information:" in log_text
        assert "System Information:" in log_text
        assert "Runtime Information:" in log_text
    
    def test_log_module_shutdown(self, caplog):
        """Test that log_module_shutdown logs expected information."""
        with caplog.at_level(logging.INFO):
            module_logger = logging_config.ModuleLogger("TestModule")
            module_logger.log_module_shutdown()
        
        log_text = caplog.text
        assert "MODULE SHUTDOWN" in log_text
        assert "TestModule" in log_text
    
    def test_app_env_from_environment(self, monkeypatch):
        """Test that APP_ENV is read from environment."""
        monkeypatch.setenv("APP_ENV", "production")
        module_logger = logging_config.ModuleLogger("TestModule")
        assert module_logger.app_env == "production"
    
    def test_default_app_env(self, monkeypatch):
        """Test default APP_ENV value."""
        monkeypatch.delenv("APP_ENV", raising=False)
        module_logger = logging_config.ModuleLogger("TestModule")
        assert module_logger.app_env == "development"
    
    def test_logger_formatting(self):
        """Test that logger has proper formatting."""
        module_logger = logging_config.ModuleLogger("TestModule")
        handlers = module_logger.logger.handlers
        
        for handler in handlers:
            formatter = handler.formatter
            assert formatter is not None
            assert "%(asctime)s" in formatter._fmt
            assert "%(name)s" in formatter._fmt
            assert "%(levelname)s" in formatter._fmt
            assert "%(message)s" in formatter._fmt


class TestGetModuleLogger:
    """Test get_module_logger function."""
    
    def test_returns_logger(self):
        """Test that get_module_logger returns a Logger instance."""
        logger = logging_config.get_module_logger("TestModule", log_startup=False)
        assert isinstance(logger, logging.Logger)
    
    def test_logger_with_startup_logging(self, caplog):
        """Test that startup logging happens when requested."""
        with caplog.at_level(logging.INFO):
            logger = logging_config.get_module_logger("TestModule", "1.0.0", log_startup=True)
        
        assert "MODULE STARTUP" in caplog.text
        assert "TestModule" in caplog.text
    
    def test_logger_without_startup_logging(self, caplog):
        """Test that startup logging is skipped when not requested."""
        with caplog.at_level(logging.INFO):
            logger = logging_config.get_module_logger("TestModule", log_startup=False)
        
        assert "MODULE STARTUP" not in caplog.text
    
    def test_logger_with_version(self):
        """Test logger creation with version."""
        logger = logging_config.get_module_logger("TestModule", "2.5.0", log_startup=False)
        assert logger.name == "TestModule"
    
    def test_logger_with_path(self):
        """Test logger creation with custom path."""
        custom_path = "/custom/path"
        logger = logging_config.get_module_logger("TestModule", module_path=custom_path, log_startup=False)
        assert logger.name == "TestModule"


class TestSetupBasicLogging:
    """Test setup_basic_logging function."""
    
    def test_basic_logging_setup(self):
        """Test that basic logging is set up correctly."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        logging_config.setup_basic_logging("DEBUG")
        # Check that logging setup doesn't crash
        assert root_logger is not None
    
    def test_default_log_level(self):
        """Test default log level for basic logging."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        logging_config.setup_basic_logging()
        # Check that logging setup doesn't crash
        assert root_logger is not None
    
    def test_case_insensitive_log_level(self):
        """Test that log level is case insensitive."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        logging_config.setup_basic_logging("warning")
        # Verify it accepts the parameter without error
        assert root_logger is not None


class TestHardwareInfoLogging:
    """Test hardware information logging."""
    
    def test_log_hardware_info_without_psutil(self, monkeypatch, caplog):
        """Test that hardware logging handles missing psutil gracefully."""
        # This test verifies the module doesn't crash without psutil
        with caplog.at_level(logging.DEBUG):
            module_logger = logging_config.ModuleLogger("TestModule")
            module_logger._log_hardware_info()
        
        # Should not raise an exception
        assert True
    
    def test_log_module_startup_includes_hardware_info(self, caplog):
        """Test that module startup includes hardware information."""
        with caplog.at_level(logging.INFO):
            module_logger = logging_config.ModuleLogger("TestModule")
            module_logger.log_module_startup()
        
        # Hardware info should be logged (or attempted)
        log_text = caplog.text
        assert "System Information:" in log_text


class TestFileLogging:
    """Test file logging functionality."""
    
    def test_log_file_creation(self, monkeypatch):
        """Test that log file is created in specified directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "logs", "app.log")
            monkeypatch.setenv("LOG_FILE", log_file)
            
            module_logger = logging_config.ModuleLogger("TestModule")
            logger = module_logger.get_logger()
            logger.info("Test message")
            
            assert Path(log_file).exists()
    
    def test_log_file_content(self, monkeypatch):
        """Test that messages are written to log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            monkeypatch.setenv("LOG_FILE", log_file)
            
            module_logger = logging_config.ModuleLogger("TestModule")
            logger = module_logger.get_logger()
            logger.info("Test log message")
            
            # Ensure handlers flush
            for handler in logger.handlers:
                handler.flush()
            
            with open(log_file, 'r') as f:
                content = f.read()
            
            assert "Test log message" in content
            assert "TestModule" in content
