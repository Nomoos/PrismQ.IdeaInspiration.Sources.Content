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
import json


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
    
    # Define SpotifyPodcastsSource table
    Table(
        'SpotifyPodcastsSource',
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
        title: Episode title
        description: Episode description
        tags: Comma-separated tags
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted, False if updated (duplicate)
    """
    with get_connection(database_url) as conn:
        # Check if record exists
        result = conn.execute(
            text("SELECT id FROM SpotifyPodcastsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Update existing record
            conn.execute(
                text("""
                    UPDATE SpotifyPodcastsSource
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
                    INSERT INTO SpotifyPodcastsSource
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
            text("SELECT * FROM SpotifyPodcastsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        row = result.fetchone()
        
        if row:
            return dict(row._mapping)
        return None


def get_all_ideas(database_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all ideas from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of ideas to return
        
    Returns:
        List of idea dictionaries
    """
    with get_connection(database_url) as conn:
        query = "SELECT * FROM SpotifyPodcastsSource ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        result = conn.execute(text(query))
        return [dict(row._mapping) for row in result]


def get_unprocessed_records(database_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get unprocessed records from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of records to return
        
    Returns:
        List of unprocessed record dictionaries
    """
    with get_connection(database_url) as conn:
        query = "SELECT * FROM SpotifyPodcastsSource WHERE processed = 0 ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        result = conn.execute(text(query))
        return [dict(row._mapping) for row in result]


def mark_as_processed(database_url: str, record_id: int):
    """Mark a record as processed.
    
    Args:
        database_url: Database URL
        record_id: Record ID
    """
    with get_connection(database_url) as conn:
        conn.execute(
            text("UPDATE SpotifyPodcastsSource SET processed = 1, updated_at = :updated_at WHERE id = :id"),
            {"updated_at": utc_now(), "id": record_id}
        )
        conn.commit()
