"""
Review Scraper
==============
Scrape movie reviews from IMDB and other sources.

Note: Be respectful of rate limits and robots.txt!
"""

import re
import time
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from loguru import logger
from typing import Optional, List, Dict
from datetime import datetime

from .config import get_config, get_project_root


class IMDBReviewScraper:
    """
    Scrape user reviews from IMDB.
    
    IMDB reviews are valuable because they tend to be:
    - Longer and more detailed
    - More emotionally expressive
    - Include user ratings
    
    Be respectful: Use delays between requests!
    """
    
    BASE_URL = "https://www.imdb.com"
    
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize IMDB scraper.
        
        Args:
            delay: Delay between requests in seconds
        """
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.delay = delay
        self.config = get_config()
        
        logger.info(f"IMDBReviewScraper initialized (delay: {delay}s)")
    
    def get_reviews_for_movie(
        self,
        imdb_id: str,
        max_reviews: int = 200
    ) -> List[Dict]:
        """
        Scrape reviews for a single movie.
        
        Args:
            imdb_id: IMDB movie ID (e.g., 'tt1375666')
            max_reviews: Maximum number of reviews to collect
            
        Returns:
            List of review dictionaries
        """
        if not imdb_id or not imdb_id.startswith("tt"):
            logger.warning(f"Invalid IMDB ID: {imdb_id}")
            return []
        
        reviews = []
        url = f"{self.BASE_URL}/title/{imdb_id}/reviews"
        
        try:
            # Initial page request
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 404:
                logger.debug(f"No reviews page for {imdb_id}")
                return []
                
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch reviews for {imdb_id}: {e}")
            return []
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Find all review containers
        review_containers = soup.find_all("div", class_="review-container")
        
        for container in review_containers[:max_reviews]:
            try:
                review = self._parse_review_container(container, imdb_id)
                if review:
                    reviews.append(review)
            except Exception as e:
                logger.debug(f"Error parsing review: {e}")
                continue
        
        # TODO: Handle "Load More" button for additional reviews
        # This requires JavaScript execution or API endpoint discovery
        
        return reviews
    
    def _parse_review_container(
        self, 
        container, 
        imdb_id: str
    ) -> Optional[Dict]:
        """
        Parse a single review container element.
        
        Args:
            container: BeautifulSoup element
            imdb_id: IMDB movie ID
            
        Returns:
            Review dictionary or None
        """
        # Extract rating (1-10 scale)
        rating = None
        rating_elem = container.find("span", class_="rating-other-user-rating")
        if rating_elem:
            rating_span = rating_elem.find("span")
            if rating_span:
                try:
                    rating = int(rating_span.text.strip())
                except ValueError:
                    pass
        
        # Extract review title
        title = None
        title_elem = container.find("a", class_="title")
        if title_elem:
            title = title_elem.text.strip()
        
        # Extract review content
        content = None
        content_elem = container.find("div", class_="text")
        if content_elem:
            content = content_elem.text.strip()
        
        # Skip if content is too short
        min_length = self.config.get("data_collection", {}).get(
            "reviews", {}
        ).get("min_review_length", 50)
        
        if not content or len(content) < min_length:
            return None
        
        # Extract date
        date_str = None
        date_elem = container.find("span", class_="review-date")
        if date_elem:
            date_str = date_elem.text.strip()
        
        # Extract author
        author = None
        author_elem = container.find("span", class_="display-name-link")
        if author_elem:
            author_link = author_elem.find("a")
            if author_link:
                author = author_link.text.strip()
        
        # Extract helpful votes
        helpful_votes = 0
        helpful_elem = container.find("div", class_="actions")
        if helpful_elem:
            helpful_text = helpful_elem.text
            match = re.search(r"(\d+)\s+out of\s+(\d+)", helpful_text)
            if match:
                helpful_votes = int(match.group(1))
        
        # Check if marked as spoiler
        is_spoiler = container.find("span", class_="spoiler-warning") is not None
        
        return {
            "imdb_id": imdb_id,
            "rating": rating,
            "title": title,
            "content": content,
            "author": author,
            "date": date_str,
            "helpful_votes": helpful_votes,
            "is_spoiler": is_spoiler,
            "source": "imdb",
            "scraped_at": datetime.now().isoformat()
        }
    
    def collect_reviews_for_movies(
        self,
        imdb_ids: List[str],
        output_dir: Optional[str] = None,
        max_reviews_per_movie: int = 200,
        batch_size: int = 100
    ) -> pd.DataFrame:
        """
        Collect reviews for multiple movies.
        
        Args:
            imdb_ids: List of IMDB movie IDs
            output_dir: Directory to save reviews
            max_reviews_per_movie: Maximum reviews per movie
            batch_size: Save progress every N movies
            
        Returns:
            DataFrame with all reviews
        """
        if output_dir is None:
            output_dir = get_project_root() / "data" / "raw" / "reviews"
        else:
            output_dir = Path(output_dir)
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Filter valid IDs
        valid_ids = [
            id for id in imdb_ids 
            if id and isinstance(id, str) and id.startswith("tt")
        ]
        
        logger.info("=" * 60)
        logger.info(f"📝 Starting review collection for {len(valid_ids)} movies")
        logger.info("=" * 60)
        
        all_reviews = []
        movies_with_reviews = 0
        batch_num = 0
        
        for i, imdb_id in enumerate(tqdm(valid_ids, desc="📥 Scraping reviews")):
            # Get reviews for this movie
            reviews = self.get_reviews_for_movie(imdb_id, max_reviews_per_movie)
            
            if reviews:
                all_reviews.extend(reviews)
                movies_with_reviews += 1
            
            # Respectful delay
            time.sleep(self.delay)
            
            # Save batch periodically
            if (i + 1) % batch_size == 0:
                batch_num += 1
                batch_df = pd.DataFrame(all_reviews)
                batch_path = output_dir / f"reviews_batch_{batch_num}.parquet"
                batch_df.to_parquet(batch_path, index=False)
                logger.info(
                    f"💾 Saved batch {batch_num}: {len(batch_df)} reviews"
                )
        
        # Create final DataFrame
        df = pd.DataFrame(all_reviews)
        
        if len(df) > 0:
            # Save complete dataset
            final_path = output_dir / "all_reviews.parquet"
            df.to_parquet(final_path, index=False)
            
            # Also save as CSV for viewing
            csv_path = output_dir / "all_reviews.csv"
            df.to_csv(csv_path, index=False)
            
            logger.success(f"💾 Saved {len(df)} reviews to {final_path}")
        
        # Print summary
        self._print_collection_summary(
            df, 
            len(valid_ids), 
            movies_with_reviews
        )
        
        return df
    
    def _print_collection_summary(
        self, 
        df: pd.DataFrame, 
        total_movies: int,
        movies_with_reviews: int
    ):
        """Print collection summary."""
        
        if len(df) == 0:
            logger.warning("No reviews collected!")
            return
        
        avg_length = df['content'].str.len().mean()
        with_rating = df['rating'].notna().sum()
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              📝 IMDB REVIEW COLLECTION SUMMARY                ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Movies Processed:           {total_movies:>6,}                          ║
║  Movies with Reviews:        {movies_with_reviews:>6,}                          ║
║                                                               ║
║  Total Reviews Collected:    {len(df):>6,}                          ║
║  Reviews with Rating:        {with_rating:>6,}                          ║
║  Avg Review Length:          {avg_length:>6,.0f} chars                    ║
║  Avg Reviews/Movie:          {len(df)/max(movies_with_reviews,1):>6.1f}                          ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(summary)


class LetterboxdScraper:
    """
    Scrape reviews from Letterboxd.
    
    Letterboxd reviews are especially valuable for emotion analysis:
    - Often more personal and emotional
    - Film-focused community
    - Rich emotional vocabulary
    
    TODO: Implement in Phase 2 for enhanced emotion data
    """
    
    def __init__(self):
        logger.info("LetterboxdScraper - Coming in Phase 2!")
        raise NotImplementedError(
            "Letterboxd scraper will be implemented in Phase 2"
        )


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape IMDB reviews")
    parser.add_argument(
        "--movies-file",
        type=str,
        required=True,
        help="Path to movies parquet file with imdb_id column"
    )
    parser.add_argument(
        "--max-reviews",
        type=int,
        default=200,
        help="Maximum reviews per movie"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests (seconds)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    # Load movie IDs
    movies_df = pd.read_parquet(args.movies_file)
    imdb_ids = movies_df['imdb_id'].dropna().tolist()
    
    print(f"Found {len(imdb_ids)} movies with IMDB IDs")
    
    # Scrape reviews
    scraper = IMDBReviewScraper(delay=args.delay)
    reviews_df = scraper.collect_reviews_for_movies(
        imdb_ids=imdb_ids,
        output_dir=args.output,
        max_reviews_per_movie=args.max_reviews
    )
    
    print(f"\n✅ Scraping complete! {len(reviews_df)} reviews collected.")
