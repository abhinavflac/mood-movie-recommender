"""
Database Module
===============
SQLAlchemy models and database operations.
"""

from .models import (
    Base,
    Movie,
    Review,
    EmotionCategory,
    MoodMapping,
    init_db,
    get_session,
    get_engine,
    bulk_insert_movies,
    bulk_insert_reviews,
    get_or_create_movie
)

__all__ = [
    "Base",
    "Movie", 
    "Review",
    "EmotionCategory",
    "MoodMapping",
    "init_db",
    "get_session",
    "get_engine",
    "bulk_insert_movies",
    "bulk_insert_reviews",
    "get_or_create_movie"
]
