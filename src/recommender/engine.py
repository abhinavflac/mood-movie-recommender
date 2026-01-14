"""
Mood-Based Movie Recommender
=============================
Recommend movies based on user's current mood and desired emotional experience.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from loguru import logger


# Our 12 emotion categories
EMOTION_CATEGORIES = [
    'cathartic_sadness',
    'thrilling_tension',
    'mind_blown',
    'pure_joy',
    'bittersweet_hope',
    'righteous_anger',
    'cozy_comfort',
    'controlled_fear',
    'intellectual_stimulation',
    'romantic_warmth',
    'triumphant_inspired',
    'awe_wonder',
]

# User-friendly mood options mapped to emotions
MOOD_PRESETS = {
    # Current mood options
    "stressed": {"intensity": "low", "comfort": "high"},
    "sad": {"primary": "cathartic_sadness", "comfort": "medium"},
    "bored": {"intensity": "high", "primary": "thrilling_tension"},
    "anxious": {"comfort": "high", "intensity": "low"},
    "happy": {"primary": "pure_joy", "comfort": "high"},
    "lonely": {"primary": "romantic_warmth", "comfort": "high"},
    "angry": {"primary": "righteous_anger", "intensity": "high"},
    "tired": {"comfort": "high", "intensity": "low"},
    "curious": {"primary": "intellectual_stimulation"},
    "romantic": {"primary": "romantic_warmth"},
    "adventurous": {"primary": "awe_wonder", "intensity": "high"},
    "reflective": {"primary": "bittersweet_hope", "intensity": "low"},
}

# What users want to feel
DESIRED_FEELINGS = {
    "feel-good": ["pure_joy", "cozy_comfort", "romantic_warmth"],
    "thrilled": ["thrilling_tension", "controlled_fear", "mind_blown"],
    "inspired": ["triumphant_inspired", "awe_wonder", "bittersweet_hope"],
    "cry": ["cathartic_sadness", "bittersweet_hope"],
    "laugh": ["pure_joy", "cozy_comfort"],
    "think": ["intellectual_stimulation", "mind_blown"],
    "scared": ["controlled_fear", "thrilling_tension"],
    "romantic": ["romantic_warmth", "bittersweet_hope"],
    "empowered": ["triumphant_inspired", "righteous_anger"],
    "relaxed": ["cozy_comfort", "pure_joy"],
    "amazed": ["awe_wonder", "mind_blown"],
}


@dataclass
class MovieRecommendation:
    """A movie recommendation with explanation."""
    title: str
    overview: str
    genres: List[str]
    poster_url: str
    dominant_emotions: List[str]
    intensity_score: float
    comfort_score: float
    match_score: float
    explanation: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "overview": self.overview,
            "genres": self.genres,
            "poster_url": self.poster_url,
            "dominant_emotions": self.dominant_emotions,
            "intensity_score": self.intensity_score,
            "comfort_score": self.comfort_score,
            "match_score": round(self.match_score, 2),
            "explanation": self.explanation,
        }


class MoodRecommender:
    """
    Recommend movies based on mood matching.
    """
    
    def __init__(self, movies_path: str = "data/processed/movies_with_emotions.csv"):
        """
        Initialize recommender with movie data.
        
        Args:
            movies_path: Path to movies with emotion profiles
        """
        self.movies_df = self._load_movies(movies_path)
        logger.info(f"Loaded {len(self.movies_df)} movies for recommendations")
    
    def _load_movies(self, path: str) -> pd.DataFrame:
        """Load and prepare movie data."""
        df = pd.read_csv(path)
        
        # Parse string representations of lists
        for col in ['dominant_emotions', 'genres']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
        
        # Parse emotion_profile if it exists
        if 'emotion_profile' in df.columns:
            df['emotion_profile'] = df['emotion_profile'].apply(
                lambda x: eval(x) if isinstance(x, str) else x
            )
        
        return df
    
    def recommend_by_mood(
        self,
        current_mood: str,
        desired_feeling: str,
        n_recommendations: int = 5
    ) -> List[MovieRecommendation]:
        """
        Get recommendations based on current mood and desired feeling.
        
        Args:
            current_mood: User's current mood (e.g., "stressed", "bored")
            desired_feeling: What they want to feel (e.g., "feel-good", "thrilled")
            n_recommendations: Number of recommendations
            
        Returns:
            List of MovieRecommendation objects
        """
        # Get mood parameters
        mood_params = MOOD_PRESETS.get(current_mood.lower(), {})
        desired_emotions = DESIRED_FEELINGS.get(desired_feeling.lower(), [])
        
        if not desired_emotions:
            # Default to feel-good if unknown
            desired_emotions = ["pure_joy", "cozy_comfort"]
        
        # Score each movie
        scores = []
        
        for idx, row in self.movies_df.iterrows():
            score = self._calculate_match_score(row, mood_params, desired_emotions)
            scores.append((idx, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top recommendations
        recommendations = []
        
        for idx, score in scores[:n_recommendations]:
            row = self.movies_df.iloc[idx]
            
            rec = MovieRecommendation(
                title=row.get(' ', row.get('title', 'Unknown')),  # Handle different column names
                overview=row.get('overview', '')[:200] + '...',
                genres=row.get('genres', []),
                poster_url=row.get('poster_url', ''),
                dominant_emotions=row.get('dominant_emotions', []),
                intensity_score=row.get('intensity_score', 5),
                comfort_score=row.get('comfort_score', 5),
                match_score=score,
                explanation=self._generate_explanation(row, current_mood, desired_feeling)
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_match_score(
        self,
        movie_row: pd.Series,
        mood_params: dict,
        desired_emotions: List[str]
    ) -> float:
        """
        Calculate how well a movie matches the user's needs.
        
        Score components:
        1. Emotion match (40%) - Does movie have desired emotions?
        2. Intensity match (30%) - Does intensity fit current mood?
        3. Comfort match (30%) - Does comfort fit current mood?
        """
        score = 0.0
        
        # 1. Emotion match
        movie_emotions = movie_row.get('dominant_emotions', [])
        if isinstance(movie_emotions, str):
            movie_emotions = eval(movie_emotions)
        
        emotion_match = 0
        for emotion in desired_emotions:
            if emotion in movie_emotions:
                emotion_match += 1
        
        emotion_score = emotion_match / len(desired_emotions) if desired_emotions else 0
        score += emotion_score * 0.4
        
        # 2. Intensity match
        movie_intensity = movie_row.get('intensity_score', 5)
        desired_intensity = mood_params.get('intensity', 'medium')
        
        if desired_intensity == 'low':
            # Prefer low intensity (< 4)
            intensity_score = max(0, 1 - (movie_intensity / 10))
        elif desired_intensity == 'high':
            # Prefer high intensity (> 6)
            intensity_score = movie_intensity / 10
        else:
            # Prefer medium (4-6)
            intensity_score = 1 - abs(movie_intensity - 5) / 5
        
        score += intensity_score * 0.3
        
        # 3. Comfort match
        movie_comfort = movie_row.get('comfort_score', 5)
        desired_comfort = mood_params.get('comfort', 'medium')
        
        if desired_comfort == 'high':
            comfort_score = movie_comfort / 10
        elif desired_comfort == 'low':
            comfort_score = max(0, 1 - (movie_comfort / 10))
        else:
            comfort_score = 1 - abs(movie_comfort - 5) / 5
        
        score += comfort_score * 0.3
        
        # Bonus for primary emotion match
        if mood_params.get('primary') in movie_emotions:
            score += 0.1
        
        return min(1.0, score)  # Cap at 1.0
    
    def _generate_explanation(
        self,
        movie_row: pd.Series,
        current_mood: str,
        desired_feeling: str
    ) -> str:
        """Generate a human-readable explanation for the recommendation."""
        dominant = movie_row.get('dominant_emotions', [])
        if isinstance(dominant, str):
            dominant = eval(dominant)
        
        intensity = movie_row.get('intensity_score', 5)
        comfort = movie_row.get('comfort_score', 5)
        
        # Format emotions nicely
        emotions_text = ", ".join([e.replace('_', ' ') for e in dominant[:2]])
        
        if desired_feeling == "feel-good":
            return f"A comforting choice with {emotions_text} to lift your spirits."
        elif desired_feeling == "thrilled":
            return f"An intense experience with {emotions_text} to get your heart racing."
        elif desired_feeling == "cry":
            return f"An emotional journey with {emotions_text} for a good cathartic release."
        elif desired_feeling == "inspired":
            return f"An uplifting film with {emotions_text} to inspire you."
        elif desired_feeling == "think":
            return f"A thought-provoking movie with {emotions_text} to engage your mind."
        else:
            return f"Featuring {emotions_text} - a great match for your mood."
    
    def recommend_by_emotions(
        self,
        target_emotions: List[str],
        min_intensity: float = 0,
        max_intensity: float = 10,
        min_comfort: float = 0,
        n_recommendations: int = 5
    ) -> List[MovieRecommendation]:
        """
        Get recommendations by specifying exact emotions.
        
        Args:
            target_emotions: List of desired emotion categories
            min_intensity: Minimum intensity score
            max_intensity: Maximum intensity score
            min_comfort: Minimum comfort score
            n_recommendations: Number of recommendations
            
        Returns:
            List of MovieRecommendation objects
        """
        # Filter by intensity and comfort
        df = self.movies_df[
            (self.movies_df['intensity_score'] >= min_intensity) &
            (self.movies_df['intensity_score'] <= max_intensity) &
            (self.movies_df['comfort_score'] >= min_comfort)
        ]
        
        # Score by emotion match
        scores = []
        
        for idx, row in df.iterrows():
            movie_emotions = row.get('dominant_emotions', [])
            if isinstance(movie_emotions, str):
                movie_emotions = eval(movie_emotions)
            
            match_count = sum(1 for e in target_emotions if e in movie_emotions)
            score = match_count / len(target_emotions) if target_emotions else 0
            
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for idx, score in scores[:n_recommendations]:
            row = self.movies_df.loc[idx]
            
            rec = MovieRecommendation(
                title=row.get(' ', row.get('title', 'Unknown')),
                overview=row.get('overview', '')[:200] + '...',
                genres=row.get('genres', []),
                poster_url=row.get('poster_url', ''),
                dominant_emotions=row.get('dominant_emotions', []),
                intensity_score=row.get('intensity_score', 5),
                comfort_score=row.get('comfort_score', 5),
                match_score=score,
                explanation=f"Matches {int(score * 100)}% of your desired emotions."
            )
            recommendations.append(rec)
        
        return recommendations
    
    def get_mood_journey(
        self,
        start_mood: str,
        end_mood: str,
        n_movies: int = 3
    ) -> List[MovieRecommendation]:
        """
        Get a sequence of movies to transition from one mood to another.
        
        Args:
            start_mood: Starting emotional state
            end_mood: Desired ending emotional state
            n_movies: Number of movies in the journey
            
        Returns:
            Ordered list of movie recommendations
        """
        # This creates a gradual emotional journey
        journey = []
        
        # First movie: acknowledge current mood
        first_recs = self.recommend_by_mood(start_mood, start_mood, n_recommendations=1)
        if first_recs:
            journey.append(first_recs[0])
        
        # Middle movies: transition
        if n_movies >= 3:
            mid_recs = self.recommend_by_mood(start_mood, end_mood, n_recommendations=n_movies - 2)
            journey.extend(mid_recs)
        
        # Final movie: deliver desired feeling
        final_recs = self.recommend_by_mood("neutral", end_mood, n_recommendations=1)
        if final_recs:
            journey.append(final_recs[0])
        
        return journey[:n_movies]


def get_available_moods() -> Dict[str, List[str]]:
    """Get available mood options for UI."""
    return {
        "current_moods": list(MOOD_PRESETS.keys()),
        "desired_feelings": list(DESIRED_FEELINGS.keys()),
        "emotions": EMOTION_CATEGORIES,
    }


if __name__ == "__main__":
    # Test the recommender
    print("=" * 60)
    print("MOOD-BASED MOVIE RECOMMENDER")
    print("=" * 60)
    
    recommender = MoodRecommender()
    
    # Test case 1: Stressed user wanting to feel good
    print("\n--- Test 1: Stressed -> Feel Good ---")
    recs = recommender.recommend_by_mood("stressed", "feel-good", n_recommendations=3)
    
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Genres: {rec.genres}")
        print(f"   Emotions: {rec.dominant_emotions}")
        print(f"   Match: {rec.match_score:.0%}")
        print(f"   {rec.explanation}")
    
    # Test case 2: Bored user wanting to be thrilled
    print("\n--- Test 2: Bored -> Thrilled ---")
    recs = recommender.recommend_by_mood("bored", "thrilled", n_recommendations=3)
    
    for i, rec in enumerate(recs, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Genres: {rec.genres}")
        print(f"   Match: {rec.match_score:.0%}")
    
    # Test case 3: Mood journey
    print("\n--- Test 3: Mood Journey (Sad -> Inspired) ---")
    journey = recommender.get_mood_journey("sad", "inspired", n_movies=3)
    
    for i, rec in enumerate(journey, 1):
        print(f"\nStep {i}: {rec.title}")
        print(f"   {rec.explanation}")
