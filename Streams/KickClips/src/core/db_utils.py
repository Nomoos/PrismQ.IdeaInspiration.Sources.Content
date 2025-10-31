"""Database utilities for KickClips storage using SQLAlchemy.

This module provides a database abstraction layer for storing Kick clips data
with support for multiple database backends via SQLAlchemy.
"""

import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Float, DateTime, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from datetime import datetime


# Global engine cache to avoid recreating engines
_engines = {}


def get_engine(database_url: str):
    """Get or create a SQLAlchemy engine for the given database URL.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        SQLAlchemy engine
    """
    if database_url not in _engines:
        _engines[database_url] = create_engine(database_url, echo=False)
    return _engines[database_url]


@contextmanager
def get_connection(database_url: str):
    """Context manager for database connections.
    
    Args:
        database_url: Database connection URL
        
    Yields:
        SQLAlchemy connection
    """
    engine = get_engine(database_url)
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(database_url: str):
    """Initialize database schema.
    
    Args:
        database_url: Database connection URL
    """
    engine = get_engine(database_url)
    metadata = MetaData()
    
    # Define KickClipsSource table
    Table(
        'KickClipsSource',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('source', String, nullable=False),
        Column('source_id', String, nullable=False),
        Column('title', String, nullable=False),
        Column('description', String),
        Column('tags', String),
        Column('score', Float),
        Column('score_dictionary', String),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        UniqueConstraint('source', 'source_id', name='uix_source_source_id'),
        extend_existing=True
    )
    
    # Create tables
    metadata.create_all(engine)


def insert_idea(
    database_url: str,
    source: str,
    source_id: str,
    title: str,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    score: Optional[float] = None,
    score_dictionary: Optional[str] = None
) -> bool:
    """Insert or update an idea in the database.
    
    Args:
        database_url: Database connection URL
        source: Source platform (e.g., 'kick_clips')
        source_id: Unique identifier from source
        title: Clip title
        description: Clip description
        tags: Comma-separated tags
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted (new), False if updated (duplicate)
    """
    # Convert dict to JSON string if needed
    if isinstance(score_dictionary, dict):
        score_dictionary = json.dumps(score_dictionary)
    
    with get_connection(database_url) as conn:
        # Try to insert first
        try:
            conn.execute(
                text("""
                    INSERT INTO KickClipsSource 
                    (source, source_id, title, description, tags, score, score_dictionary)
                    VALUES (:source, :source_id, :title, :description, :tags, :score, :score_dictionary)
                """),
                {
                    "source": source,
                    "source_id": source_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                }
            )
            return True  # New insert
        except IntegrityError:
            # Update existing record
            conn.rollback()
            conn.execute(
                text("""
                    UPDATE KickClipsSource
                    SET title = :title,
                        description = :description,
                        tags = :tags,
                        score = :score,
                        score_dictionary = :score_dictionary,
                        updated_at = :updated_at
                    WHERE source = :source AND source_id = :source_id
                """),
                {
                    "source": source,
                    "source_id": source_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                    "updated_at": datetime.utcnow(),
                }
            )
            return False  # Update


def get_all_ideas(database_url: str, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
    """Get all ideas from database.
    
    Args:
        database_url: Database connection URL
        limit: Maximum number of records to return
        order_by: Column to order by
        
    Returns:
        List of idea dictionaries
    """
    # Validate order_by to prevent SQL injection
    valid_columns = ["id", "source", "source_id", "title", "score", "created_at", "updated_at"]
    if order_by not in valid_columns:
        order_by = "score"
    
    with get_connection(database_url) as conn:
        result = conn.execute(
            text(f"SELECT * FROM KickClipsSource ORDER BY {order_by} DESC LIMIT :limit"),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [dict(zip(result.keys(), row)) for row in rows]


def count_ideas(database_url: str) -> int:
    """Count total ideas in database.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Total count
    """
    with get_connection(database_url) as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM KickClipsSource"))
        return result.scalar()


def count_by_source(database_url: str, source: str) -> int:
    """Count ideas by source.
    
    Args:
        database_url: Database connection URL
        source: Source platform
        
    Returns:
        Count for source
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM KickClipsSource WHERE source = :source"),
            {"source": source}
        )
        return result.scalar()
