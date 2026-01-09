"""
Main Data Pipeline
==================
Orchestrates the complete Phase 1 data collection workflow.
"""

import os
import pandas as pd
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from .tmdb_collector import TMDBCollector
from .review_scraper import IMDBReviewScraper
from .config import setup_directories, get_project_root

# Load environment
load_dotenv()


class DataPipeline:
    """
    Orchestrate the complete data collection pipeline.
    
    Steps:
    1. Collect movie metadata from TMDB
    2. Scrape reviews from IMDB
    3. Process and clean data
    4. Load into database
    """
    
    def __init__(self):
        self.project_root = get_project_root()
        self.data_dir = self.project_root / "data"
        
        # Ensure directories exist
        setup_directories()
        
        logger.info("DataPipeline initialized")
    
    def collect_movies(self, target: int = 5000) -> pd.DataFrame:
        """Collect movie metadata from TMDB."""
        logger.info(f"📥 Collecting {target} movies from TMDB...")
        
        collector = TMDBCollector()
        movies_df = collector.collect_comprehensive_dataset(target_movies=target)
        
        return movies_df
    
    def collect_reviews(self, movies_df: pd.DataFrame, max_per_movie: int = 200) -> pd.DataFrame:
        """Collect reviews from IMDB."""
        imdb_ids = movies_df['imdb_id'].dropna().tolist()
        
        if not imdb_ids:
            logger.warning("No IMDB IDs found!")
            return pd.DataFrame()
        
        logger.info(f"📥 Collecting reviews for {len(imdb_ids)} movies...")
        
        scraper = IMDBReviewScraper(delay=1.0)
        reviews_df = scraper.collect_reviews_for_movies(
            imdb_ids=imdb_ids,
            max_reviews_per_movie=max_per_movie
        )
        
        return reviews_df
    
    def process_data(self):
        """Process and clean collected data."""
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        return processor.run_full_processing()
    
    def load_to_database(self, movies_df: pd.DataFrame, reviews_df: pd.DataFrame):
        """Load data into database."""
        from src.database import init_db, get_session, bulk_insert_movies, bulk_insert_reviews
        
        logger.info("Loading data to database...")
        init_db()
        
        session = get_session()
        
        # Insert movies
        movies_count = bulk_insert_movies(session, movies_df.to_dict('records'))
        logger.info(f"Inserted {movies_count} movies")
        
        # Insert reviews
        if len(reviews_df) > 0:
            reviews_count = bulk_insert_reviews(session, reviews_df.to_dict('records'))
            logger.info(f"Inserted {reviews_count} reviews")
        
        session.close()
    
    def run(self, target_movies: int = 1000, skip_reviews: bool = False):
        """
        Run the complete pipeline.
        
        Args:
            target_movies: Number of movies to collect
            skip_reviews: Skip review collection (faster for testing)
        """
        logger.info("=" * 60)
        logger.info("🚀 STARTING DATA COLLECTION PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Collect movies
        movies_df = self.collect_movies(target=target_movies)
        
        # Step 2: Collect reviews (optional)
        reviews_df = pd.DataFrame()
        if not skip_reviews:
            reviews_df = self.collect_reviews(movies_df)
        
        # Step 3: Process data
        movies_clean, reviews_clean = self.process_data()
        
        # Step 4: Load to database
        self.load_to_database(movies_clean, reviews_clean)
        
        logger.success("=" * 60)
        logger.success("✅ PIPELINE COMPLETE!")
        logger.success("=" * 60)
        
        return movies_clean, reviews_clean


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Movie Mood Data Pipeline")
    parser.add_argument("--target", type=int, default=1000, help="Target movies")
    parser.add_argument("--skip-reviews", action="store_true", help="Skip reviews")
    
    args = parser.parse_args()
    
    pipeline = DataPipeline()
    pipeline.run(target_movies=args.target, skip_reviews=args.skip_reviews)


if __name__ == "__main__":
    main()
