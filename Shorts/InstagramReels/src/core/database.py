"""Database wrapper for Instagram Reels source.

This module provides database operations for Instagram Reels idea collection.
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from . import db_utils


class Database:
    """Manages database operations for Instagram Reels idea collection."""

    def __init__(self, db_path: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            interactive: Whether to prompt for confirmation before creating database
        """
        self.db_path = db_path
        self._interactive = interactive
        
        # Construct database_url from db_path
        if db_path.startswith("sqlite://"):
            self.database_url = db_path
        else:
            self.database_url = f"sqlite:///{db_path}"
        
        # Check if database already exists
        db_exists = Path(db_path).exists() if not db_path.startswith("sqlite://") else True
        
        # If database doesn't exist and we're in interactive mode, ask for confirmation
        if not db_exists and self._interactive:
            if not self._confirm_database_creation():
                print("Database creation cancelled.")
                sys.exit(0)
        
        # Initialize database schema
        self._init_db()
    
    def _confirm_database_creation(self) -> bool:
        """Prompt user for confirmation before creating database.
        
        Returns:
            True if user confirms, False otherwise
        """
        try:
            response = input(f"Database '{self.db_path}' does not exist. Create it? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            # In non-interactive environments, return True
            return True
    
    def _init_db(self):
        """Initialize database schema."""
        db_utils.init_database(self.database_url)
    
    def insert_idea(self, source: str, source_id: str, title: str,
                   description: Optional[str] = None, tags: Optional[str] = None,
                   score: Optional[float] = None, score_dictionary: Optional[str] = None) -> bool:
        """Insert or update an idea in the database.
        
        Args:
            source: Source platform (e.g., 'instagram_reels_explore')
            source_id: Unique reel identifier from Instagram
            title: Reel caption/title
            description: Full caption with hashtags
            tags: Comma-separated tags
            score: Calculated score
            score_dictionary: JSON string or dict of score components
            
        Returns:
            True if inserted, False if updated (duplicate)
        """
        # Convert dict to JSON string if needed
        if isinstance(score_dictionary, dict):
            import json
            score_dictionary = json.dumps(score_dictionary)
        
        return db_utils.insert_idea(
            self.database_url,
            source=source,
            source_id=source_id,
            title=title,
            description=description,
            tags=tags,
            score=score,
            score_dictionary=score_dictionary
        )
    
    def get_unprocessed_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get unprocessed records from database.
        
        Args:
            limit: Optional limit on number of records
            
        Returns:
            List of record dictionaries
        """
        return db_utils.get_unprocessed_records(self.database_url, limit=limit)
    
    def mark_as_processed(self, record_id: int):
        """Mark a record as processed.
        
        Args:
            record_id: Record ID to mark as processed
        """
        db_utils.mark_as_processed(self.database_url, record_id)
    
    def get_all_ideas(self, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
        """Get all ideas from database.
        
        Args:
            limit: Maximum number of records to return
            order_by: Column to order by (default: score)
            
        Returns:
            List of idea dictionaries
        """
        return db_utils.get_all_ideas(self.database_url, limit=limit, order_by=order_by)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        return db_utils.get_stats(self.database_url)
