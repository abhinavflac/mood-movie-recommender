"""
Emotion Engine Pipeline
========================
Batch process all movies to generate emotion profiles.
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from typing import Optional

from .profiler import create_emotion_profile, EmotionProfile


def process_movies_from_csv(
    csv_path: str = "movies.csv",
    output_path: Optional[str] = None,
    batch_size: int = 100
) -> pd.DataFrame:
    """
    Process all movies from CSV and add emotion profiles.
    
    Args:
        csv_path: Path to movies CSV file
        output_path: Where to save results (default: data/processed/movies_with_emotions.parquet)
        batch_size: Number of movies to process before saving checkpoint
        
    Returns:
        DataFrame with emotion profiles added
    """
    logger.info(f"Loading movies from {csv_path}...")
    
    # Load movies
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} movies")
    
    # Prepare output columns
    df['emotion_profile'] = None
    df['dominant_emotions'] = None
    df['intensity_score'] = None
    df['catharsis_score'] = None
    df['comfort_score'] = None
    df['emotion_processed'] = False
    
    # Process each movie
    logger.info("Processing movies...")
    
    for idx in tqdm(range(len(df)), desc="Analyzing emotions"):
        row = df.iloc[idx]
        
        # Get overview and genres
        overview = row.get('overview', '')
        genres_str = row.get('genres', '[]')
        
        # Parse genres from string representation
        try:
            if isinstance(genres_str, str):
                genres = eval(genres_str)
            else:
                genres = genres_str if genres_str else []
        except:
            genres = []
        
        # Skip if no overview
        if not overview or pd.isna(overview):
            continue
        
        # Create emotion profile
        try:
            profile = create_emotion_profile(
                overview=str(overview),
                genres=genres if isinstance(genres, list) else []
            )
            
            # Store results
            df.at[idx, 'emotion_profile'] = str(profile.emotion_scores)
            df.at[idx, 'dominant_emotions'] = str(profile.dominant_emotions)
            df.at[idx, 'intensity_score'] = profile.intensity_score
            df.at[idx, 'catharsis_score'] = profile.catharsis_score
            df.at[idx, 'comfort_score'] = profile.comfort_score
            df.at[idx, 'emotion_processed'] = True
            
        except Exception as e:
            logger.warning(f"Error processing movie {idx}: {e}")
            continue
        
        # Checkpoint save
        if (idx + 1) % batch_size == 0:
            logger.debug(f"Checkpoint: {idx + 1} movies processed")
    
    # Count processed
    processed = df['emotion_processed'].sum()
    logger.success(f"Processed {processed} / {len(df)} movies")
    
    # Save results
    if output_path is None:
        output_path = Path("data/processed/movies_with_emotions.parquet")
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_parquet(output_path, index=False)
    logger.success(f"Saved to {output_path}")
    
    # Also save as CSV for easy viewing
    csv_output = output_path.with_suffix('.csv')
    df.to_csv(csv_output, index=False)
    logger.info(f"Also saved to {csv_output}")
    
    return df


def process_movies_from_database(batch_size: int = 100) -> int:
    """
    Process movies from database and update with emotion profiles.
    
    Args:
        batch_size: Number to process at a time
        
    Returns:
        Number of movies processed
    """
    from src.database import get_session, Movie
    
    session = get_session()
    
    # Get unprocessed movies
    movies = session.query(Movie).filter(
        Movie.emotion_processed == False,
        Movie.overview != None
    ).all()
    
    logger.info(f"Found {len(movies)} movies to process")
    
    count = 0
    
    for movie in tqdm(movies, desc="Analyzing emotions"):
        try:
            # Parse genres
            genres = movie.genres if movie.genres else []
            
            # Create profile
            profile = create_emotion_profile(
                overview=movie.overview,
                genres=genres
            )
            
            # Update movie
            movie.emotion_profile = profile.emotion_scores
            movie.dominant_emotions = profile.dominant_emotions
            movie.intensity_score = profile.intensity_score
            movie.catharsis_score = profile.catharsis_score
            movie.comfort_score = profile.comfort_score
            movie.emotion_processed = True
            
            count += 1
            
            # Commit in batches
            if count % batch_size == 0:
                session.commit()
                logger.debug(f"Committed batch: {count} movies")
                
        except Exception as e:
            logger.warning(f"Error processing {movie.title}: {e}")
            continue
    
    # Final commit
    session.commit()
    session.close()
    
    logger.success(f"Processed {count} movies")
    return count


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process movie emotions")
    parser.add_argument(
        "--source", 
        choices=["csv", "database"],
        default="csv",
        help="Source of movie data"
    )
    parser.add_argument(
        "--csv-path",
        default="movies.csv",
        help="Path to movies CSV (if source=csv)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for results"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("EMOTION ENGINE - Starting Processing")
    logger.info("=" * 60)
    
    if args.source == "csv":
        df = process_movies_from_csv(
            csv_path=args.csv_path,
            output_path=args.output,
            batch_size=args.batch_size
        )
        
        # Print summary
        print("\n" + "=" * 60)
        print("EMOTION ENGINE SUMMARY")
        print("=" * 60)
        print(f"Total movies processed: {df['emotion_processed'].sum()}")
        print(f"\nSample emotion profiles:")
        
        sample = df[df['emotion_processed'] == True].head(3)
        for _, row in sample.iterrows():
            title = row.get(' ', 'Unknown')  # First column might be title
            print(f"\n  {title}")
            print(f"    Dominant: {row['dominant_emotions']}")
            print(f"    Intensity: {row['intensity_score']}")
            print(f"    Comfort: {row['comfort_score']}")
            
    else:
        count = process_movies_from_database(batch_size=args.batch_size)
        print(f"\nProcessed {count} movies in database")
    
    logger.success("Emotion Engine complete!")


if __name__ == "__main__":
    main()
