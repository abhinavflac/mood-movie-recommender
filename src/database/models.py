"""
Database Models
===============
SQLAlchemy ORM models for the movie mood recommender.
"""

import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    ForeignKey, Boolean, JSON, create_engine, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from loguru import logger

# For SQLite, we need to handle arrays differently
# PostgreSQL has native ARRAY support

Base = declarative_base()


class Movie(Base):
    """
    Movie metadata and emotion profile.
    
    This is the core table storing all movie information
    and the computed emotion profiles (added in Phase 2).
    """
    __tablename__ = "movies"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # External IDs
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)
    imdb_id = Column(String(20), unique=True, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    original_title = Column(String(500))
    release_date = Column(DateTime)
    runtime = Column(Integer)  # minutes
    status = Column(String(50))  # Released, Post Production, etc.
    
    # Financials
    budget = Column(Integer)
    revenue = Column(Integer)
    
    # Ratings & Popularity
    popularity = Column(Float)
    tmdb_rating = Column(Float)  # vote_average
    tmdb_vote_count = Column(Integer)
    imdb_rating = Column(Float)  # To be filled from reviews
    
    # Content
    overview = Column(Text)
    tagline = Column(String(1000))
    genres = Column(JSON)  # List of genre names
    keywords = Column(JSON)  # List of keywords
    
    # Media URLs
    poster_url = Column(String(500))
    backdrop_url = Column(String(500))
    trailer_url = Column(String(500))
    
    # Language & Region
    original_language = Column(String(10))
    spoken_languages = Column(JSON)  # List of languages
    production_countries = Column(JSON)  # List of countries
    production_companies = Column(JSON)  # List of company names
    
    # Credits
    director = Column(String(200))
    top_cast = Column(JSON)  # List of actor names
    
    # =========================================
    # EMOTION DATA (Populated in Phase 2)
    # =========================================
    
    # Emotion profile vector
    # {"joy": 0.8, "sadness": 0.2, "fear": 0.1, ...}
    emotion_profile = Column(JSON)
    
    # Dominant emotions (top 3)
    dominant_emotions = Column(JSON)  # ["joy", "excitement", "wonder"]
    
    # Emotional arc through the movie
    # [{"phase": "opening", "emotion": "intrigue", "intensity": 0.6}, ...]
    emotional_arc = Column(JSON)
    
    # Aggregate scores
    intensity_score = Column(Float)  # 0-10, how intense is the experience
    catharsis_score = Column(Float)  # 0-10, emotional release potential
    comfort_score = Column(Float)    # 0-10, how "safe" and cozy
    
    # Processing status
    emotion_processed = Column(Boolean, default=False)
    review_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}', tmdb_id={self.tmdb_id})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "tmdb_id": self.tmdb_id,
            "imdb_id": self.imdb_id,
            "title": self.title,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "runtime": self.runtime,
            "genres": self.genres,
            "overview": self.overview,
            "poster_url": self.poster_url,
            "director": self.director,
            "tmdb_rating": self.tmdb_rating,
            "emotion_profile": self.emotion_profile,
            "dominant_emotions": self.dominant_emotions,
            "intensity_score": self.intensity_score,
            "catharsis_score": self.catharsis_score,
        }


class Review(Base):
    """
    Movie reviews from various sources.
    
    Reviews are analyzed to extract emotions (Phase 2)
    and aggregated to create movie emotion profiles.
    """
    __tablename__ = "reviews"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to movie
    movie_id = Column(Integer, ForeignKey("movies.id"), index=True, nullable=False)
    
    # Source information
    source = Column(String(50), nullable=False)  # 'imdb', 'tmdb', 'letterboxd'
    source_review_id = Column(String(100))  # Original ID from source
    
    # Review content
    title = Column(String(500))
    content = Column(Text, nullable=False)
    
    # Ratings
    rating = Column(Float)  # Normalized to 0-10
    original_rating = Column(String(50))  # Original format ("8/10", "4 stars")
    
    # Author info
    author = Column(String(200))
    author_id = Column(String(100))
    
    # Metadata
    review_date = Column(DateTime)
    helpful_votes = Column(Integer, default=0)
    is_spoiler = Column(Boolean, default=False)
    
    # =========================================
    # EMOTION ANALYSIS (Populated in Phase 2)
    # =========================================
    
    # Detected emotions from this review
    # {"joy": 0.7, "admiration": 0.5, "surprise": 0.3, ...}
    emotions = Column(JSON)
    
    # Primary emotion detected
    dominant_emotion = Column(String(50))
    
    # Sentiment score (-1 to 1)
    sentiment_score = Column(Float)
    
    # Intensity of emotional expression (0-1)
    emotional_intensity = Column(Float)
    
    # Processing status
    processed = Column(Boolean, default=False)
    
    # Timestamps
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    movie = relationship("Movie", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, movie_id={self.movie_id}, source='{self.source}')>"


class EmotionCategory(Base):
    """
    Reference table for emotion categories.
    
    Defines the emotion taxonomy used by the recommender.
    """
    __tablename__ = "emotion_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identifiers
    name = Column(String(100), unique=True, nullable=False)  # internal name
    display_name = Column(String(100), nullable=False)  # UI display name
    emoji = Column(String(10))
    
    # Description
    description = Column(Text)
    example_movies = Column(JSON)  # List of example movie titles
    
    # Dimensional properties (for mapping and clustering)
    valence = Column(Float)     # -1 (negative) to 1 (positive)
    arousal = Column(Float)     # 0 (calm) to 1 (excited)
    dominance = Column(Float)   # 0 (powerless) to 1 (empowered)
    
    # Grouping
    category_group = Column(String(50))  # 'positive', 'negative', 'complex', etc.
    
    # UI styling
    color_hex = Column(String(7))  # e.g., '#FF6B6B'
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<EmotionCategory(name='{self.name}', emoji='{self.emoji}')>"


class MoodMapping(Base):
    """
    Mapping between user moods and recommendation strategies.
    
    Defines how to transition from one mood state to another.
    """
    __tablename__ = "mood_mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Mood transition
    current_mood = Column(String(100), nullable=False)
    desired_mood = Column(String(100), nullable=False)
    
    # Recommendation strategy
    recommended_emotions = Column(JSON)  # List of emotions to prioritize
    avoid_emotions = Column(JSON)  # List of emotions to avoid
    intensity_preference = Column(String(20))  # 'low', 'medium', 'high'
    
    # Journey details
    journey_name = Column(String(200))  # "Stress Relief Journey"
    journey_description = Column(Text)  # Explanation for the user
    
    # Weights for scoring
    scoring_weights = Column(JSON)  # Custom weights for this journey
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<MoodMapping('{self.current_mood}' -> '{self.desired_mood}')>"


# =========================================
# Database Connection Functions
# =========================================

_engine = None
_SessionLocal = None


def get_engine(database_url: Optional[str] = None, force_sqlite: bool = True):
    """
    Get or create database engine.
    
    Args:
        database_url: Optional database URL, uses env var if not provided
        force_sqlite: If True, use SQLite regardless of DATABASE_URL (easier dev)
        
    Returns:
        SQLAlchemy engine
    """
    global _engine
    
    if _engine is not None:
        return _engine
    
    # For simpler development, default to SQLite
    # Set force_sqlite=False to use PostgreSQL from DATABASE_URL
    if force_sqlite or database_url is None:
        from src.data_collection.config import get_project_root
        data_dir = get_project_root() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        database_url = f"sqlite:///{data_dir}/movie_mood.db"
        logger.info(f"Using SQLite database: {database_url}")
    
    # Create engine with appropriate settings
    if database_url.startswith("sqlite"):
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        # Enable foreign keys for SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        _engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            echo=False
        )
    
    return _engine


def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal()


def init_db(database_url: Optional[str] = None) -> None:
    """
    Initialize database and create all tables.
    
    Args:
        database_url: Optional database URL
    """
    engine = get_engine(database_url)
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.success("Database initialized successfully!")
    
    # Seed emotion categories if empty
    session = get_session()
    if session.query(EmotionCategory).count() == 0:
        seed_emotion_categories(session)
    session.close()


def seed_emotion_categories(session: Session) -> None:
    """
    Seed the emotion categories table with initial data.
    
    Args:
        session: Database session
    """
    logger.info("Seeding emotion categories...")
    
    categories = [
        {
            "name": "cathartic_sadness",
            "display_name": "Cathartic Sadness",
            "emoji": "😢",
            "description": "Deep emotional release through tears",
            "valence": -0.3,
            "arousal": 0.4,
            "dominance": 0.3,
            "category_group": "release",
            "color_hex": "#6B7FD7",
            "example_movies": ["The Notebook", "Schindler's List", "CODA"]
        },
        {
            "name": "thrilling_tension",
            "display_name": "Thrilling Tension",
            "emoji": "😰",
            "description": "Edge-of-seat excitement and suspense",
            "valence": 0.2,
            "arousal": 0.9,
            "dominance": 0.4,
            "category_group": "excitement",
            "color_hex": "#FF6B6B",
            "example_movies": ["Sicario", "No Country for Old Men", "Se7en"]
        },
        {
            "name": "mind_blown",
            "display_name": "Mind-Blown",
            "emoji": "🤯",
            "description": "Intellectual surprise and revelation",
            "valence": 0.7,
            "arousal": 0.8,
            "dominance": 0.6,
            "category_group": "stimulation",
            "color_hex": "#9B59B6",
            "example_movies": ["Inception", "The Prestige", "Memento"]
        },
        {
            "name": "pure_joy",
            "display_name": "Pure Joy",
            "emoji": "😂",
            "description": "Laughter and feel-good happiness",
            "valence": 0.9,
            "arousal": 0.7,
            "dominance": 0.7,
            "category_group": "positive",
            "color_hex": "#F1C40F",
            "example_movies": ["The Hangover", "Superbad", "Bridesmaids"]
        },
        {
            "name": "bittersweet_hope",
            "display_name": "Bittersweet Hope",
            "emoji": "🥹",
            "description": "Melancholy mixed with optimism",
            "valence": 0.3,
            "arousal": 0.5,
            "dominance": 0.5,
            "category_group": "complex",
            "color_hex": "#1ABC9C",
            "example_movies": ["CODA", "The Pursuit of Happyness", "Life is Beautiful"]
        },
        {
            "name": "righteous_anger",
            "display_name": "Righteous Anger",
            "emoji": "😤",
            "description": "Satisfying justice and vindication",
            "valence": 0.4,
            "arousal": 0.8,
            "dominance": 0.9,
            "category_group": "empowerment",
            "color_hex": "#E74C3C",
            "example_movies": ["John Wick", "Kill Bill", "Django Unchained"]
        },
        {
            "name": "cozy_comfort",
            "display_name": "Cozy Comfort",
            "emoji": "🫠",
            "description": "Warm, safe, and relaxing",
            "valence": 0.8,
            "arousal": 0.2,
            "dominance": 0.6,
            "category_group": "calm",
            "color_hex": "#FFB347",
            "example_movies": ["Paddington", "The Holiday", "Julie & Julia"]
        },
        {
            "name": "controlled_fear",
            "display_name": "Controlled Fear",
            "emoji": "😱",
            "description": "Safe thrills and scary fun",
            "valence": 0.1,
            "arousal": 0.85,
            "dominance": 0.3,
            "category_group": "excitement",
            "color_hex": "#2C3E50",
            "example_movies": ["A Quiet Place", "Get Out", "The Conjuring"]
        },
        {
            "name": "intellectual_stimulation",
            "display_name": "Intellectual Stimulation",
            "emoji": "🤔",
            "description": "Deep thinking and contemplation",
            "valence": 0.5,
            "arousal": 0.5,
            "dominance": 0.6,
            "category_group": "stimulation",
            "color_hex": "#3498DB",
            "example_movies": ["Arrival", "Ex Machina", "Blade Runner 2049"]
        },
        {
            "name": "romantic_warmth",
            "display_name": "Romantic Warmth",
            "emoji": "❤️‍🔥",
            "description": "Love, passion, and connection",
            "valence": 0.85,
            "arousal": 0.6,
            "dominance": 0.5,
            "category_group": "positive",
            "color_hex": "#FF69B4",
            "example_movies": ["Before Sunrise", "The Notebook", "Pride and Prejudice"]
        },
        {
            "name": "triumphant_inspired",
            "display_name": "Triumphant & Inspired",
            "emoji": "🏆",
            "description": "Motivation and empowerment",
            "valence": 0.9,
            "arousal": 0.75,
            "dominance": 0.9,
            "category_group": "empowerment",
            "color_hex": "#27AE60",
            "example_movies": ["Rocky", "The Shawshank Redemption", "Whiplash"]
        },
        {
            "name": "awe_wonder",
            "display_name": "Awe & Wonder",
            "emoji": "🌌",
            "description": "Beautiful vastness and amazement",
            "valence": 0.8,
            "arousal": 0.6,
            "dominance": 0.4,
            "category_group": "transcendent",
            "color_hex": "#8E44AD",
            "example_movies": ["Interstellar", "Avatar", "Planet Earth"]
        }
    ]
    
    for cat_data in categories:
        category = EmotionCategory(**cat_data)
        session.add(category)
    
    session.commit()
    logger.success(f"Seeded {len(categories)} emotion categories!")


# =========================================
# Utility Functions
# =========================================

def get_or_create_movie(session: Session, tmdb_id: int, **kwargs) -> Movie:
    """
    Get existing movie or create new one.
    
    Args:
        session: Database session
        tmdb_id: TMDB movie ID
        **kwargs: Movie attributes
        
    Returns:
        Movie instance
    """
    movie = session.query(Movie).filter_by(tmdb_id=tmdb_id).first()
    
    if movie is None:
        movie = Movie(tmdb_id=tmdb_id, **kwargs)
        session.add(movie)
        session.flush()
    else:
        # Update existing movie
        for key, value in kwargs.items():
            if value is not None:
                setattr(movie, key, value)
    
    return movie


def bulk_insert_movies(session: Session, movies_data: List[dict]) -> int:
    """
    Bulk insert movies, handling duplicates.
    
    Args:
        session: Database session
        movies_data: List of movie dictionaries
        
    Returns:
        Number of movies inserted/updated
    """
    count = 0
    
    for data in movies_data:
        tmdb_id = data.pop("tmdb_id", None)
        if tmdb_id is None:
            continue
            
        try:
            movie = get_or_create_movie(session, tmdb_id, **data)
            count += 1
        except Exception as e:
            logger.warning(f"Error inserting movie {tmdb_id}: {e}")
            session.rollback()
            continue
    
    session.commit()
    return count


def bulk_insert_reviews(session: Session, reviews_data: List[dict]) -> int:
    """
    Bulk insert reviews.
    
    Args:
        session: Database session
        reviews_data: List of review dictionaries
        
    Returns:
        Number of reviews inserted
    """
    # Get IMDB ID to movie ID mapping
    movies = session.query(Movie.id, Movie.imdb_id).all()
    imdb_to_id = {m.imdb_id: m.id for m in movies if m.imdb_id}
    
    count = 0
    
    for data in reviews_data:
        imdb_id = data.pop("imdb_id", None)
        movie_id = imdb_to_id.get(imdb_id)
        
        if movie_id is None:
            continue
        
        try:
            review = Review(movie_id=movie_id, **data)
            session.add(review)
            count += 1
        except Exception as e:
            logger.warning(f"Error inserting review: {e}")
            continue
    
    session.commit()
    return count


if __name__ == "__main__":
    # Test database initialization
    init_db()
    
    session = get_session()
    
    # Check emotion categories
    categories = session.query(EmotionCategory).all()
    print(f"\n🎭 Emotion Categories ({len(categories)}):")
    for cat in categories:
        print(f"  {cat.emoji} {cat.display_name}")
    
    session.close()
