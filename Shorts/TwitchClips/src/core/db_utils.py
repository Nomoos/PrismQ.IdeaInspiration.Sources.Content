"""Database utility functions using DATABASE_URL from environment.

This module provides direct database access using SQLAlchemy Core (not ORM)
with connection configured via DATABASE_URL environment variable.
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def get_engine(database_url: str):
    """Get SQLAlchemy engine from DATABASE_URL.
    
    Args:
        database_url: Database URL (e.g., sqlite:///db.s3db)
        
    Returns:
        SQLAlchemy engine
    """
    # For SQLite, ensure parent directory exists
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # Use StaticPool for SQLite to avoid threading issues
        return create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        return create_engine(database_url)


def init_database(database_url: str):
    """Initialize database schema.
    
    Args:
        database_url: Database URL
    """
    engine = get_engine(database_url)
    metadata = MetaData()
    
    # Define TwitchClipsSource table
    Table(
        'TwitchClipsSource',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('source', String(100), nullable=False, index=True),
        Column('source_id', String(255), nullable=False, index=True),
        Column('title', Text, nullable=False),
        Column('description', Text, nullable=True),
        Column('tags', Text, nullable=True),
        Column('score', Float, nullable=True),
        Column('score_dictionary', Text, nullable=True),
        Column('processed', Boolean, default=False, nullable=False, index=True),
        Column('created_at', DateTime, default=utc_now, nullable=False),
        Column('updated_at', DateTime, default=utc_now, onupdate=utc_now, nullable=False),
    )
    
    # Create all tables
    metadata.create_all(engine)


@contextmanager
def get_connection(database_url: str):
    """Get database connection as context manager.
    
    Args:
        database_url: Database URL
        
    Yields:
        SQLAlchemy connection
    """
    engine = get_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


def insert_idea(database_url: str, source: str, source_id: str, title: str,
                description: Optional[str] = None, tags: Optional[str] = None,
                score: Optional[float] = None, score_dictionary: Optional[str] = None) -> bool:
    """Insert or update an idea in the database.
    
    Args:
        database_url: Database URL
        source: Source platform
        source_id: Unique identifier from source
        title: Clip title
        description: Clip description
        tags: Comma-separated tags
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted, False if updated (duplicate)
    """
    with get_connection(database_url) as conn:
        # Check if record exists
        result = conn.execute(
            text("SELECT id FROM TwitchClipsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Update existing record
            conn.execute(
                text("""
                    UPDATE TwitchClipsSource
                    SET title = :title, description = :description, tags = :tags,
                        score = :score, score_dictionary = :score_dictionary, updated_at = :updated_at
                    WHERE source = :source AND source_id = :source_id
                """),
                {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                    "updated_at": utc_now(),
                    "source": source,
                    "source_id": source_id
                }
            )
            conn.commit()
            return False  # Not inserted, updated
        else:
            # Insert new record
            conn.execute(
                text("""
                    INSERT INTO TwitchClipsSource
                    (source, source_id, title, description, tags, score, score_dictionary, processed, created_at, updated_at)
                    VALUES (:source, :source_id, :title, :description, :tags, :score, :score_dictionary, :processed, :created_at, :updated_at)
                """),
                {
                    "source": source,
                    "source_id": source_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                    "processed": False,
                    "created_at": utc_now(),
                    "updated_at": utc_now()
                }
            )
            conn.commit()
            return True  # Inserted


def get_idea(database_url: str, source: str, source_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific idea by source and source_id.
    
    Args:
        database_url: Database URL
        source: Source platform
        source_id: Unique identifier from source
        
    Returns:
        Idea dictionary or None if not found
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("SELECT * FROM TwitchClipsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        row = result.fetchone()
        
        if row:
            return dict(row._mapping)
        return None


def get_all_ideas(database_url: str, source: Optional[str] = None, 
                  processed: Optional[bool] = None) -> List[Dict[str, Any]]:
    """Get all ideas, optionally filtered by source and processed status.
    
    Args:
        database_url: Database URL
        source: Optional source filter
        processed: Optional processed status filter
        
    Returns:
        List of idea dictionaries
    """
    with get_connection(database_url) as conn:
        query = "SELECT * FROM TwitchClipsSource WHERE 1=1"
        params = {}
        
        if source:
            query += " AND source = :source"
            params["source"] = source
        
        if processed is not None:
            query += " AND processed = :processed"
            params["processed"] = processed
        
        query += " ORDER BY created_at DESC"
        
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]


def mark_as_processed(database_url: str, source: str, source_id: str) -> bool:
    """Mark an idea as processed.
    
    Args:
        database_url: Database URL
        source: Source platform
        source_id: Unique identifier from source
        
    Returns:
        True if marked, False if not found
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("""
                UPDATE TwitchClipsSource
                SET processed = :processed, updated_at = :updated_at
                WHERE source = :source AND source_id = :source_id
            """),
            {
                "processed": True,
                "updated_at": utc_now(),
                "source": source,
                "source_id": source_id
            }
        )
        conn.commit()
        return result.rowcount > 0
