"""
TMDB Data Collector
====================
Collect movie metadata from The Movie Database (TMDB) API.

API Documentation: https://developers.themoviedb.org/3
"""

import time
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from typing import Optional, List, Dict, Any

from .config import get_tmdb_api_key, get_config, get_project_root


class TMDBCollector:
    """
    Collect comprehensive movie data from TMDB API.
    
    Attributes:
        api_key (str): TMDB API key
        base_url (str): TMDB API base URL
        session (requests.Session): HTTP session for requests
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDB collector.
        
        Args:
            api_key: Optional API key, will use env var if not provided
        """
        self.api_key = api_key or get_tmdb_api_key()
        self.session = requests.Session()
        self.config = get_config()
        
        # Rate limiting settings
        self.requests_made = 0
        self.last_request_time = 0
        
        logger.info("TMDBCollector initialized")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        retries: int = 3
    ) -> Optional[Dict]:
        """
        Make API request with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            JSON response as dictionary or None on failure
        """
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Rate limiting: max 4 requests per second
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.25:
            time.sleep(0.25 - elapsed)
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                self.last_request_time = time.time()
                self.requests_made += 1
                
                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 10))
                    logger.warning(f"Rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{retries}")
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    
        return None
    
    def get_popular_movies(self, pages: int = 100) -> List[Dict]:
        """
        Get popular movies.
        
        Args:
            pages: Number of pages to fetch (20 movies per page)
            
        Returns:
            List of movie dictionaries
        """
        movies = []
        
        for page in tqdm(range(1, pages + 1), desc="📥 Popular movies"):
            data = self._make_request("movie/popular", {"page": page})
            if data and "results" in data:
                movies.extend(data["results"])
            
            if data and page >= data.get("total_pages", 0):
                break
                
        logger.info(f"Fetched {len(movies)} popular movies")
        return movies
    
    def get_top_rated_movies(self, pages: int = 100) -> List[Dict]:
        """
        Get top rated movies.
        
        Args:
            pages: Number of pages to fetch
            
        Returns:
            List of movie dictionaries
        """
        movies = []
        
        for page in tqdm(range(1, pages + 1), desc="📥 Top rated movies"):
            data = self._make_request("movie/top_rated", {"page": page})
            if data and "results" in data:
                movies.extend(data["results"])
            
            if data and page >= data.get("total_pages", 0):
                break
                
        logger.info(f"Fetched {len(movies)} top rated movies")
        return movies
    
    def discover_movies_by_year(
        self, 
        start_year: int = 1990, 
        end_year: int = 2025,
        min_votes: int = 100
    ) -> List[Dict]:
        """
        Discover movies by release year for diversity.
        
        Args:
            start_year: Start year for discovery
            end_year: End year for discovery
            min_votes: Minimum vote count filter
            
        Returns:
            List of movie dictionaries
        """
        movies = []
        
        years = range(start_year, end_year + 1)
        for year in tqdm(years, desc="📥 Discovering by year"):
            # Get top movies from each year
            for page in range(1, 3):  # 2 pages per year
                data = self._make_request("discover/movie", {
                    "primary_release_year": year,
                    "sort_by": "vote_count.desc",
                    "vote_count.gte": min_votes,
                    "page": page
                })
                
                if data and "results" in data:
                    movies.extend(data["results"])
                    
        logger.info(f"Discovered {len(movies)} movies by year")
        return movies
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Get detailed information for a specific movie.
        
        Args:
            movie_id: TMDB movie ID
            
        Returns:
            Movie details dictionary or None
        """
        data = self._make_request(
            f"movie/{movie_id}",
            {"append_to_response": "credits,keywords,videos,reviews"}
        )
        return data
    
    def get_movie_reviews(self, movie_id: int, max_pages: int = 5) -> List[Dict]:
        """
        Get reviews for a specific movie from TMDB.
        
        Args:
            movie_id: TMDB movie ID
            max_pages: Maximum pages to fetch
            
        Returns:
            List of review dictionaries
        """
        reviews = []
        
        for page in range(1, max_pages + 1):
            data = self._make_request(
                f"movie/{movie_id}/reviews",
                {"page": page}
            )
            
            if data and "results" in data:
                reviews.extend(data["results"])
                
                if page >= data.get("total_pages", 1):
                    break
                    
        return reviews
    
    def _extract_director(self, credits: Dict) -> Optional[str]:
        """Extract director name from credits."""
        crew = credits.get("crew", [])
        directors = [p["name"] for p in crew if p.get("job") == "Director"]
        return directors[0] if directors else None
    
    def _extract_cast(self, credits: Dict, top_n: int = 5) -> List[str]:
        """Extract top cast member names."""
        cast = credits.get("cast", [])
        return [p["name"] for p in cast[:top_n]]
    
    def _extract_trailer_url(self, videos: Dict) -> Optional[str]:
        """Extract YouTube trailer URL."""
        results = videos.get("results", [])
        
        # Prefer official trailers
        for video in results:
            if (video.get("type") == "Trailer" and 
                video.get("site") == "YouTube" and 
                video.get("official", False)):
                return f"https://www.youtube.com/watch?v={video['key']}"
        
        # Fallback to any trailer
        for video in results:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
                
        return None
    
    def collect_comprehensive_dataset(
        self,
        target_movies: int = 5000,
        output_dir: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Collect comprehensive movie dataset from multiple sources.
        
        Args:
            target_movies: Target number of movies to collect
            output_dir: Output directory for saving data
            
        Returns:
            DataFrame with movie data
        """
        if output_dir is None:
            output_dir = get_project_root() / "data" / "raw" / "tmdb"
        else:
            output_dir = Path(output_dir)
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("=" * 60)
        logger.info(f"🎬 Starting collection of {target_movies} movies")
        logger.info("=" * 60)
        
        # Step 1: Gather movie IDs from multiple sources
        movie_ids = set()
        
        # Popular movies (wide appeal)
        popular = self.get_popular_movies(pages=150)
        movie_ids.update(m["id"] for m in popular)
        logger.info(f"📊 {len(movie_ids)} unique IDs after popular")
        
        # Top rated (quality films)
        top_rated = self.get_top_rated_movies(pages=150)
        movie_ids.update(m["id"] for m in top_rated)
        logger.info(f"📊 {len(movie_ids)} unique IDs after top rated")
        
        # Discover by year (diversity)
        discovered = self.discover_movies_by_year(1990, 2025)
        movie_ids.update(m["id"] for m in discovered)
        logger.info(f"📊 {len(movie_ids)} unique IDs after year discovery")
        
        # Limit to target
        movie_ids = list(movie_ids)[:target_movies]
        logger.info(f"🎯 Processing {len(movie_ids)} movies")
        
        # Step 2: Get detailed info for each movie
        movies_data = []
        failed_ids = []
        
        for movie_id in tqdm(movie_ids, desc="📥 Getting movie details"):
            try:
                details = self.get_movie_details(movie_id)
                
                if not details:
                    failed_ids.append(movie_id)
                    continue
                
                # Extract and structure data
                movie_record = {
                    # IDs
                    "tmdb_id": details.get("id"),
                    "imdb_id": details.get("imdb_id"),
                    
                    # Basic info
                    "title": details.get("title"),
                    "original_title": details.get("original_title"),
                    "release_date": details.get("release_date"),
                    "runtime": details.get("runtime"),
                    "status": details.get("status"),
                    
                    # Financials
                    "budget": details.get("budget"),
                    "revenue": details.get("revenue"),
                    
                    # Ratings
                    "popularity": details.get("popularity"),
                    "vote_average": details.get("vote_average"),
                    "vote_count": details.get("vote_count"),
                    
                    # Content
                    "overview": details.get("overview"),
                    "tagline": details.get("tagline"),
                    "genres": [g["name"] for g in details.get("genres", [])],
                    "keywords": [
                        k["name"] 
                        for k in details.get("keywords", {}).get("keywords", [])
                    ],
                    
                    # Media URLs
                    "poster_path": details.get("poster_path"),
                    "backdrop_path": details.get("backdrop_path"),
                    "poster_url": (
                        f"{self.IMAGE_BASE_URL}/w500{details['poster_path']}"
                        if details.get("poster_path") else None
                    ),
                    "backdrop_url": (
                        f"{self.IMAGE_BASE_URL}/original{details['backdrop_path']}"
                        if details.get("backdrop_path") else None
                    ),
                    "trailer_url": self._extract_trailer_url(
                        details.get("videos", {})
                    ),
                    
                    # Language & Region
                    "original_language": details.get("original_language"),
                    "spoken_languages": [
                        l.get("english_name", l.get("name"))
                        for l in details.get("spoken_languages", [])
                    ],
                    "production_countries": [
                        c["name"] for c in details.get("production_countries", [])
                    ],
                    "production_companies": [
                        c["name"] for c in details.get("production_companies", [])
                    ],
                    
                    # Credits
                    "director": self._extract_director(details.get("credits", {})),
                    "top_cast": self._extract_cast(details.get("credits", {})),
                    
                    # TMDB reviews (will supplement with IMDB later)
                    "tmdb_review_count": len(
                        details.get("reviews", {}).get("results", [])
                    ),
                }
                
                movies_data.append(movie_record)
                
            except Exception as e:
                logger.warning(f"Error processing movie {movie_id}: {e}")
                failed_ids.append(movie_id)
                continue
        
        # Create DataFrame
        df = pd.DataFrame(movies_data)
        
        # Save to parquet
        output_path = output_dir / "movies_metadata.parquet"
        df.to_parquet(output_path, index=False)
        logger.success(f"💾 Saved {len(df)} movies to {output_path}")
        
        # Also save as CSV for easy viewing
        csv_path = output_dir / "movies_metadata.csv"
        df.to_csv(csv_path, index=False)
        
        # Save failed IDs for retry
        if failed_ids:
            failed_path = output_dir / "failed_movie_ids.txt"
            with open(failed_path, 'w') as f:
                f.write('\n'.join(map(str, failed_ids)))
            logger.warning(f"⚠️ {len(failed_ids)} movies failed, saved to {failed_path}")
        
        # Print summary
        self._print_collection_summary(df)
        
        return df
    
    def _print_collection_summary(self, df: pd.DataFrame):
        """Print a summary of collected data."""
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              🎬 TMDB COLLECTION SUMMARY                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Total Movies Collected:     {len(df):>6,}                          ║
║  With IMDB ID:               {df['imdb_id'].notna().sum():>6,}                          ║
║  With Overview:              {df['overview'].notna().sum():>6,}                          ║
║  With Poster:                {df['poster_path'].notna().sum():>6,}                          ║
║  With Trailer:               {df['trailer_url'].notna().sum():>6,}                          ║
║                                                               ║
║  API Requests Made:          {self.requests_made:>6,}                          ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(summary)


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect movies from TMDB")
    parser.add_argument(
        "--target", 
        type=int, 
        default=5000,
        help="Target number of movies to collect"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for data"
    )
    
    args = parser.parse_args()
    
    collector = TMDBCollector()
    df = collector.collect_comprehensive_dataset(
        target_movies=args.target,
        output_dir=args.output
    )
    
    print(f"\n✅ Collection complete! {len(df)} movies collected.")
