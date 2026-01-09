"""
Data Processor - Main processing pipeline
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from loguru import logger

from .cleaner import clean_and_validate_movies, clean_and_validate_reviews


class DataProcessor:
    """Process raw data into clean, database-ready format."""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            from src.data_collection.config import get_project_root
            data_dir = get_project_root() / "data"
        
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def process_movies(self, input_path: Optional[str] = None) -> pd.DataFrame:
        """Process raw movie data."""
        if input_path is None:
            input_path = self.raw_dir / "tmdb" / "movies_metadata.parquet"
        
        logger.info(f"Loading movies from {input_path}")
        df = pd.read_parquet(input_path) if str(input_path).endswith('.parquet') else pd.read_csv(input_path)
        
        records = clean_and_validate_movies(df.to_dict('records'))
        df_clean = pd.DataFrame(records).drop_duplicates(subset=['tmdb_id'])
        
        if 'release_date' in df_clean.columns:
            df_clean['release_date'] = pd.to_datetime(df_clean['release_date'], errors='coerce')
        
        output_path = self.processed_dir / "movies.parquet"
        df_clean.to_parquet(output_path, index=False)
        logger.success(f"Processed {len(df_clean)} movies")
        return df_clean
    
    def process_reviews(self, input_path: Optional[str] = None) -> pd.DataFrame:
        """Process raw review data."""
        if input_path is None:
            input_path = self.raw_dir / "reviews" / "all_reviews.parquet"
        
        if not Path(input_path).exists():
            logger.warning("Reviews file not found")
            return pd.DataFrame()
        
        logger.info(f"Loading reviews from {input_path}")
        df = pd.read_parquet(input_path) if str(input_path).endswith('.parquet') else pd.read_csv(input_path)
        
        records = clean_and_validate_reviews(df.to_dict('records'))
        df_clean = pd.DataFrame(records)
        
        output_path = self.processed_dir / "reviews.parquet"
        df_clean.to_parquet(output_path, index=False)
        logger.success(f"Processed {len(df_clean)} reviews")
        return df_clean
    
    def run_full_processing(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Run complete processing pipeline."""
        logger.info("Starting data processing...")
        movies_df = self.process_movies()
        reviews_df = self.process_reviews()
        logger.success("Processing complete!")
        return movies_df, reviews_df


if __name__ == "__main__":
    processor = DataProcessor()
    processor.run_full_processing()
