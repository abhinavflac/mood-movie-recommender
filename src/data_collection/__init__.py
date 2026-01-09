"""
Data Collection Module
======================
Scripts for collecting movie data from various sources.
"""

from .tmdb_collector import TMDBCollector
from .review_scraper import IMDBReviewScraper
from .config import get_config

__all__ = ["TMDBCollector", "IMDBReviewScraper", "get_config"]
