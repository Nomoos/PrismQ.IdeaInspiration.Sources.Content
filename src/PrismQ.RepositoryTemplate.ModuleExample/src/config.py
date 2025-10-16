"""Configuration management for the ModuleExample."""

import os
from pathlib import Path


class ModuleConfig:
    """Configuration class for the ModuleExample.

    Loads configuration from environment variables.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.module_name: str = os.getenv("MODULE_NAME", "PrismQ.RepositoryTemplate.ModuleExample")
        self.module_env: str = os.getenv("MODULE_ENV", "development")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Paths
        self.input_dir: Path = Path(os.getenv("INPUT_DIR", "./input"))
        self.output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.cache_dir: Path = Path(os.getenv("CACHE_DIR", "./cache"))

        # Create directories if they don't exist
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.input_dir, self.output_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_api_key(self, service: str) -> str | None:
        """Get API key for a service.

        Args:
            service: Name of the service (e.g., 'openai', 'anthropic')

        Returns:
            API key or None if not found
        """
        env_var = f"{service.upper()}_API_KEY"
        return os.getenv(env_var)


# Global config instance
config = ModuleConfig()
