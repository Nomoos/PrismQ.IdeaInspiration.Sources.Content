"""Configuration management for PrismQ.IdeaInspiration.Sources.Content.Shorts.InstagramReelsSource."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key


class Config:
    """Manages application configuration from environment variables."""

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: .env in topmost PrismQ directory)
            interactive: Whether to prompt for missing values (default: True)
        """
        # Determine working directory and .env file path
        if env_file is None:
            # Find topmost parent directory with exact name "PrismQ"
            prismq_dir = self._find_prismq_directory()
            # Only add _WD suffix if we found a PrismQ directory
            if prismq_dir.name == "PrismQ":
                working_dir = prismq_dir.parent / "PrismQ_WD"
            else:
                # If no PrismQ found, use current directory as-is
                working_dir = prismq_dir
            self.working_directory = str(working_dir)
            env_file = working_dir / ".env"
        else:
            # Use the directory of the provided env_file as working directory
            env_path = Path(env_file)
            self.working_directory = str(env_path.parent.absolute())
            env_file = env_path
        
        self.env_file = str(env_file)
        self._interactive = interactive
        
        # Create .env file if it doesn't exist
        if not Path(self.env_file).exists():
            self._create_env_file()
        
        # Load environment variables from .env file
        load_dotenv(self.env_file)
        
        # Store/update working directory in .env
        self._ensure_working_directory()
        
        # Load configuration with interactive prompting for missing values
        self._load_configuration()
    
    def _find_prismq_directory(self) -> Path:
        """Find the topmost/root parent directory with exact name 'PrismQ'.
        
        Returns:
            Path to the topmost PrismQ directory, or current directory if none found
        """
        current_path = Path.cwd().absolute()
        prismq_dir = None
        
        # Check current directory and all parents, continuing to find the topmost match
        for path in [current_path] + list(current_path.parents):
            if path.name == "PrismQ":
                prismq_dir = path
                # Continue searching - don't break early
        
        # Return the topmost PrismQ directory found, or current directory as fallback
        return prismq_dir if prismq_dir else current_path
    
    def _create_env_file(self):
        """Create a new .env file with default values."""
        Path(self.env_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.env_file).touch()
    
    def _ensure_working_directory(self):
        """Ensure WORKING_DIR is set in .env file."""
        if not os.getenv('WORKING_DIR'):
            set_key(self.env_file, 'WORKING_DIR', self.working_directory)
        else:
            # Use the value from .env if it exists
            self.working_directory = os.getenv('WORKING_DIR')
    
    def _load_configuration(self):
        """Load configuration from environment variables."""
        # Database path
        self.database_path = self._get_config_value(
            'DATABASE_PATH',
            default=os.path.join(self.working_directory, 'instagram_reels.db'),
            description='Path to SQLite database file'
        )
        
        # Instagram scraping settings
        self.instagram_max_reels = int(self._get_config_value(
            'INSTAGRAM_MAX_REELS',
            default='50',
            description='Maximum number of reels to scrape per session'
        ))
        
        self.instagram_explore_max_reels = int(self._get_config_value(
            'INSTAGRAM_EXPLORE_MAX_REELS',
            default='50',
            description='Maximum number of reels from explore/trending'
        ))
        
        self.instagram_hashtag_max_reels = int(self._get_config_value(
            'INSTAGRAM_HASHTAG_MAX_REELS',
            default='50',
            description='Maximum number of reels per hashtag'
        ))
        
        self.instagram_creator_max_reels = int(self._get_config_value(
            'INSTAGRAM_CREATOR_MAX_REELS',
            default='50',
            description='Maximum number of reels per creator'
        ))
        
        # Instagram authentication (optional)
        self.instagram_username = self._get_config_value(
            'INSTAGRAM_USERNAME',
            default='',
            description='Instagram username (optional, for authenticated scraping)',
            required=False
        )
        
        self.instagram_password = self._get_config_value(
            'INSTAGRAM_PASSWORD',
            default='',
            description='Instagram password (optional)',
            required=False
        )
        
        # Reel constraints
        self.max_reel_duration = int(self._get_config_value(
            'MAX_REEL_DURATION',
            default='90',
            description='Maximum duration for reels in seconds (Instagram limit is 90s)'
        ))
    
    def _get_config_value(self, key: str, default: str = '', 
                         description: str = '', required: bool = False) -> str:
        """Get configuration value from environment or prompt user.
        
        Args:
            key: Environment variable name
            default: Default value if not set
            description: Description for user prompt
            required: Whether this value is required
            
        Returns:
            Configuration value
        """
        value = os.getenv(key)
        
        if value:
            return value
        
        # If not interactive or not required, use default
        if not self._interactive or not required:
            if default:
                set_key(self.env_file, key, default)
            return default
        
        # Prompt user for value
        prompt = f"{description} [{default}]: " if default else f"{description}: "
        
        try:
            user_input = input(prompt).strip()
            value = user_input if user_input else default
            
            # Save to .env file
            if value:
                set_key(self.env_file, key, value)
            
            return value
        except (EOFError, KeyboardInterrupt):
            # In non-interactive environments, return default
            return default
