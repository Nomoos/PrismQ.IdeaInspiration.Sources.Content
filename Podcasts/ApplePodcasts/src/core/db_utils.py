"""Database utilities for ApplePodcastsSource."""

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime

Base = declarative_base()


class ApplePodcastsSource(Base):
    """Table for storing Apple Podcasts episode data."""
    
    __tablename__ = 'ApplePodcastsSource'
    
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(String)
    tags = Column(String)
    score = Column(Float)
    score_dictionary = Column(String)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_database(database_url: str):
    """Initialize database schema.
    
    Args:
        database_url: Database URL (e.g., sqlite:///db.s3db)
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


@contextmanager
def get_connection(database_url: str):
    """Get database connection context manager.
    
    Args:
        database_url: Database URL
        
    Yields:
        Database connection
    """
    engine = create_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


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
        database_url: Database URL
        source: Source platform
        source_id: Unique identifier from source
        title: Episode title
        description: Episode description
        tags: Comma-separated tags
        score: Calculated score
        score_dictionary: JSON string of score components
        
    Returns:
        True if inserted (new), False if updated (duplicate)
    """
    import json
    
    # Convert dict to JSON string if needed
    if isinstance(score_dictionary, dict):
        score_dictionary = json.dumps(score_dictionary)
    
    with get_connection(database_url) as conn:
        # Check if record exists
        result = conn.execute(
            text("SELECT id FROM ApplePodcastsSource WHERE source = :source AND source_id = :source_id"),
            {"source": source, "source_id": source_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Update existing record
            conn.execute(
                text("""
                    UPDATE ApplePodcastsSource 
                    SET title = :title,
                        description = :description,
                        tags = :tags,
                        score = :score,
                        score_dictionary = :score_dictionary,
                        updated_at = :updated_at
                    WHERE source = :source AND source_id = :source_id
                """),
                {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                    "updated_at": datetime.utcnow(),
                    "source": source,
                    "source_id": source_id
                }
            )
            conn.commit()
            return False
        else:
            # Insert new record
            conn.execute(
                text("""
                    INSERT INTO ApplePodcastsSource 
                    (source, source_id, title, description, tags, score, score_dictionary, created_at, updated_at)
                    VALUES (:source, :source_id, :title, :description, :tags, :score, :score_dictionary, :created_at, :updated_at)
                """),
                {
                    "source": source,
                    "source_id": source_id,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "score": score,
                    "score_dictionary": score_dictionary,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            conn.commit()
            return True


def get_all_ideas(database_url: str, limit: int = 20, order_by: str = "score") -> List[Dict[str, Any]]:
    """Get all ideas from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of records to return
        order_by: Column to order by
        
    Returns:
        List of idea dictionaries
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text(f"SELECT * FROM ApplePodcastsSource ORDER BY {order_by} DESC LIMIT :limit"),
            {"limit": limit}
        )
        rows = result.fetchall()
        return [dict(zip(result.keys(), row)) for row in rows]


def count_ideas(database_url: str) -> int:
    """Count total ideas in database.
    
    Args:
        database_url: Database URL
        
    Returns:
        Total count
    """
    with get_connection(database_url) as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM ApplePodcastsSource"))
        return result.scalar()


def count_by_source(database_url: str, source: str) -> int:
    """Count ideas by source.
    
    Args:
        database_url: Database URL
        source: Source platform
        
    Returns:
        Count for source
    """
    with get_connection(database_url) as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM ApplePodcastsSource WHERE source = :source"),
            {"source": source}
        )
        return result.scalar()


def get_unprocessed_records(database_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get unprocessed records from database.
    
    Args:
        database_url: Database URL
        limit: Maximum number of records to return (None for all)
        
    Returns:
        List of unprocessed record dictionaries
    """
    with get_connection(database_url) as conn:
        if limit:
            result = conn.execute(
                text("SELECT * FROM ApplePodcastsSource WHERE processed = 0 LIMIT :limit"),
                {"limit": limit}
            )
        else:
            result = conn.execute(
                text("SELECT * FROM ApplePodcastsSource WHERE processed = 0")
            )
        rows = result.fetchall()
        return [dict(zip(result.keys(), row)) for row in rows]


def mark_as_processed(database_url: str, record_id: int):
    """Mark a record as processed.
    
    Args:
        database_url: Database URL
        record_id: Record ID
    """
    with get_connection(database_url) as conn:
        conn.execute(
            text("UPDATE ApplePodcastsSource SET processed = 1 WHERE id = :id"),
            {"id": record_id}
        )
        conn.commit()
