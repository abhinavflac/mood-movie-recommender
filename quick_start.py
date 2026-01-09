"""
Quick Start Script
==================
Test script to verify setup and collect a small sample dataset.
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.data_collection.config import setup_directories, get_tmdb_api_key
from src.data_collection.tmdb_collector import TMDBCollector
from src.database.models import init_db


def main():
    """Quick test of the data collection setup."""
    
    print("=" * 60)
    print("🎬 Movie Mood Recommender - Quick Start")
    print("=" * 60)
    
    # Step 1: Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    print("✅ Directories created")
    
    # Step 2: Check API key
    print("\n🔑 Checking TMDB API key...")
    try:
        api_key = get_tmdb_api_key()
        print(f"✅ API key found: {api_key[:8]}...")
    except ValueError as e:
        print(f"❌ {e}")
        print("\n👉 Please add your TMDB API key to .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your TMDB API key")
        print("   3. Get key from: https://www.themoviedb.org/settings/api")
        return
    
    # Step 3: Initialize database
    print("\n🗄️ Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    # Step 4: Test TMDB connection
    print("\n🎬 Testing TMDB API connection...")
    collector = TMDBCollector()
    
    # Get just a few movies as test
    popular = collector.get_popular_movies(pages=1)
    print(f"✅ Connected! Found {len(popular)} popular movies")
    
    # Show sample
    print("\n📋 Sample movies:")
    for movie in popular[:5]:
        print(f"   - {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete! You're ready to go.")
    print("=" * 60)
    print("\n📖 Next steps:")
    print("   1. Run full collection: python -m src.data_collection.pipeline --target 100")
    print("   2. Explore data: jupyter notebook notebooks/01_data_exploration.ipynb")


if __name__ == "__main__":
    main()
