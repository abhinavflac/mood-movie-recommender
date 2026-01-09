"""
Configuration loader for data collection.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_config() -> dict:
    """
    Load configuration from settings.yaml
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = get_project_root() / "config" / "settings.yaml"
    
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return get_default_config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_default_config() -> dict:
    """Return default configuration."""
    return {
        "project": {
            "name": "Movie Mood Recommender",
            "version": "0.1.0"
        },
        "data_collection": {
            "tmdb": {
                "base_url": "https://api.themoviedb.org/3",
                "rate_limit_per_second": 4
            },
            "reviews": {
                "min_reviews_per_movie": 20,
                "max_reviews_per_movie": 300,
                "min_review_length": 50
            }
        },
        "paths": {
            "data_dir": "data",
            "raw_data": "data/raw",
            "processed_data": "data/processed"
        }
    }


def get_tmdb_api_key() -> str:
    """
    Get TMDB API key from environment.
    
    Returns:
        str: TMDB API key
        
    Raises:
        ValueError: If API key is not set
    """
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key or api_key == "your_tmdb_api_key_here":
        raise ValueError(
            "TMDB_API_KEY not found in environment!\n"
            "Please set it in your .env file.\n"
            "Get your API key from: https://www.themoviedb.org/settings/api"
        )
    
    return api_key


def get_database_url() -> str:
    """
    Get database URL from environment.
    
    Returns:
        str: Database connection URL
    """
    url = os.getenv("DATABASE_URL")
    
    if not url:
        # Default to SQLite for development
        data_dir = get_project_root() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{data_dir}/movie_mood.db"
        logger.info(f"Using SQLite database: {url}")
    
    return url


def setup_directories():
    """Create necessary data directories."""
    root = get_project_root()
    
    directories = [
        root / "data" / "raw" / "tmdb",
        root / "data" / "raw" / "reviews",
        root / "data" / "processed",
        root / "data" / "embeddings",
        root / "logs",
        root / "models"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {directory}")
    
    logger.info("All directories created successfully")


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    print(f"Project: {config['project']['name']}")
    
    setup_directories()
