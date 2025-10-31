"""Database utility functions for HackerNews source using DATABASE_URL.

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
    """Initialize database schema for HackerNews posts.
    
    Args:
        database_url: Database URL
    """
    engine = get_engine(database_url)
    metadata = MetaData()
    
    # Define HackerNewsSource table
    Table(
        'HackerNewsSource',
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
    """Insert or update a HackerNews post in the database.
    
    Args:
        database_url: Database URL
        source: Source platform (e.g., 'hackernews_frontpage', 'hackernews_new')
        source_id: HackerNews item ID
        title: Post title
        description: Post text content
        tags: Comma-separated tags (type, domain, keywords)
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted, False if updated (duplicate)
    """
    with get_connection(database_url) as conn:
        # Check if record exists
        result = conn.execute(
            text("SELECT id FROM HackerNewsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Update existing record
            conn.execute(
                text("""
                    UPDATE HackerNewsSource
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
                    INSERT INTO HackerNewsSource
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


def get_all_ideas(database_url: str, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
    """Get all HackerNews posts from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of records to return
        order_by: Column to order by (validated against whitelist)
        
    Returns:
        List of post dictionaries
    """
    # Whitelist of allowed columns to prevent SQL injection
    allowed_columns = ['id', 'source', 'source_id', 'title', 'score', 'created_at', 'updated_at']
    if order_by not in allowed_columns:
        order_by = 'score'  # Default to safe value
    
    with get_connection(database_url) as conn:
        # Safe to use f-string here since order_by is validated against whitelist
        result = conn.execute(
            text(f"SELECT * FROM HackerNewsSource ORDER BY {order_by} DESC LIMIT :limit"),
            {"limit": limit}
        )
        return [dict(zip(result.keys(), row)) for row in result.fetchall()]


def count_ideas(database_url: str) -> int:
    """Count total HackerNews posts in database.
    
    Args:
        database_url: Database URL
        
    Returns:
        Total count
    """
    with get_connection(database_url) as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM HackerNewsSource"))
        return result.scalar()


def count_by_source(database_url: str, source: str) -> int:
    """Count HackerNews posts by source.
    
    Args:
        database_url: Database URL
        source: Source platform
        
    Returns:
        Count for source
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM HackerNewsSource WHERE source = :source"),
            {"source": source}
        )
        return result.scalar()


def clear_all_ideas(database_url: str) -> int:
    """Delete all HackerNews posts from database.
    
    Args:
        database_url: Database URL
        
    Returns:
        Number of records deleted
    """
    with get_connection(database_url) as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM HackerNewsSource"))
        count = result.scalar()
        conn.execute(text("DELETE FROM HackerNewsSource"))
        conn.commit()
        return count


def get_unprocessed_ideas(database_url: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get unprocessed HackerNews posts from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of records to return
        
    Returns:
        List of unprocessed post dictionaries
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("SELECT * FROM HackerNewsSource WHERE processed = 0 LIMIT :limit"),
            {"limit": limit}
        )
        return [dict(zip(result.keys(), row)) for row in result.fetchall()]


def mark_as_processed(database_url: str, record_id: int):
    """Mark a HackerNews post as processed.
    
    Args:
        database_url: Database URL
        record_id: Record ID to mark as processed
    """
    with get_connection(database_url) as conn:
        conn.execute(
            text("UPDATE HackerNewsSource SET processed = 1, updated_at = :updated_at WHERE id = :id"),
            {"id": record_id, "updated_at": utc_now()}
        )
        conn.commit()
