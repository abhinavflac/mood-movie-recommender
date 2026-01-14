"""
Movie Emotion Profiler
=======================
Combine NLP classification and genre mapping to create
comprehensive emotion profiles for movies.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from .classifier import classify_text, map_to_categories
from .genre_mapper import (
    get_genre_emotions,
    get_intensity_from_genres,
    get_comfort_from_genres
)


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


@dataclass
class EmotionProfile:
    """Emotion profile for a movie."""
    
    emotion_scores: Dict[str, float]  # All emotion scores
    dominant_emotions: List[str]      # Top 3 emotions
    intensity_score: float            # 0-10
    catharsis_score: float            # 0-10
    comfort_score: float              # 0-10
    confidence: float                 # 0-1, how confident we are
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'emotion_profile': self.emotion_scores,
            'dominant_emotions': self.dominant_emotions,
            'intensity_score': self.intensity_score,
            'catharsis_score': self.catharsis_score,
            'comfort_score': self.comfort_score,
        }


def create_emotion_profile(
    overview: str,
    genres: List[str],
    nlp_weight: float = 0.6,
    genre_weight: float = 0.4
) -> EmotionProfile:
    """
    Create an emotion profile for a movie.
    
    Args:
        overview: Movie plot description
        genres: List of movie genres
        nlp_weight: Weight for NLP-based emotions (0-1)
        genre_weight: Weight for genre-based emotions (0-1)
        
    Returns:
        EmotionProfile object
    """
    # Ensure weights sum to 1
    total_weight = nlp_weight + genre_weight
    nlp_weight = nlp_weight / total_weight
    genre_weight = genre_weight / total_weight
    
    # Get NLP-based emotions from overview
    nlp_emotions = {}
    confidence = 0.5  # Default confidence
    
    if overview and len(overview) > 20:
        raw_emotions = classify_text(overview)
        nlp_emotions = map_to_categories(raw_emotions)
        
        # Higher confidence with more text
        confidence = min(0.9, 0.5 + len(overview) / 1000)
    
    # Get genre-based emotions
    genre_emotions = get_genre_emotions(genres)
    
    # Combine emotion scores
    combined_emotions = {}
    
    # Add all categories with default 0
    for category in EMOTION_CATEGORIES:
        nlp_score = nlp_emotions.get(category, 0)
        genre_score = genre_emotions.get(category, 0)
        
        # Weighted combination
        combined_score = (nlp_score * nlp_weight) + (genre_score * genre_weight)
        
        if combined_score > 0.01:  # Only include non-trivial scores
            combined_emotions[category] = round(combined_score, 3)
    
    # Get top 3 dominant emotions
    sorted_emotions = sorted(
        combined_emotions.items(),
        key=lambda x: x[1],
        reverse=True
    )
    dominant_emotions = [e[0] for e in sorted_emotions[:3]]
    
    # Calculate intensity score
    intensity = calculate_intensity(combined_emotions, genres)
    
    # Calculate catharsis score (emotional release potential)
    catharsis = calculate_catharsis(combined_emotions)
    
    # Calculate comfort score
    comfort = calculate_comfort(combined_emotions, genres)
    
    return EmotionProfile(
        emotion_scores=combined_emotions,
        dominant_emotions=dominant_emotions,
        intensity_score=round(intensity, 1),
        catharsis_score=round(catharsis, 1),
        comfort_score=round(comfort, 1),
        confidence=round(confidence, 2)
    )


def calculate_intensity(emotions: Dict[str, float], genres: List[str]) -> float:
    """
    Calculate emotional intensity score (0-10).
    
    High intensity emotions: fear, tension, anger
    """
    HIGH_INTENSITY_EMOTIONS = [
        'thrilling_tension',
        'controlled_fear',
        'righteous_anger',
        'mind_blown',
    ]
    
    # Get max score from high intensity emotions
    intensity_scores = [emotions.get(e, 0) for e in HIGH_INTENSITY_EMOTIONS]
    emotion_intensity = max(intensity_scores) if intensity_scores else 0
    
    # Also factor in genre-based intensity
    genre_intensity = get_intensity_from_genres(genres) / 10
    
    # Combine (emotions weighted more)
    combined = (emotion_intensity * 0.7) + (genre_intensity * 0.3)
    
    return combined * 10  # Scale to 0-10


def calculate_catharsis(emotions: Dict[str, float]) -> float:
    """
    Calculate catharsis/emotional release score (0-10).
    
    High catharsis: sadness, hope, triumph
    """
    CATHARTIC_EMOTIONS = [
        'cathartic_sadness',
        'bittersweet_hope',
        'triumphant_inspired',
        'awe_wonder',
    ]
    
    catharsis_scores = [emotions.get(e, 0) for e in CATHARTIC_EMOTIONS]
    max_catharsis = max(catharsis_scores) if catharsis_scores else 0
    avg_catharsis = sum(catharsis_scores) / len(catharsis_scores) if catharsis_scores else 0
    
    return ((max_catharsis * 0.7) + (avg_catharsis * 0.3)) * 10


def calculate_comfort(emotions: Dict[str, float], genres: List[str]) -> float:
    """
    Calculate comfort/safety score (0-10).
    
    High comfort: joy, cozy, romance
    """
    COMFORT_EMOTIONS = [
        'pure_joy',
        'cozy_comfort',
        'romantic_warmth',
    ]
    
    DISCOMFORT_EMOTIONS = [
        'controlled_fear',
        'thrilling_tension',
        'cathartic_sadness',
    ]
    
    comfort_scores = [emotions.get(e, 0) for e in COMFORT_EMOTIONS]
    discomfort_scores = [emotions.get(e, 0) for e in DISCOMFORT_EMOTIONS]
    
    comfort = sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0
    discomfort = sum(discomfort_scores) / len(discomfort_scores) if discomfort_scores else 0
    
    # Genre-based comfort
    genre_comfort = get_comfort_from_genres(genres) / 10
    
    # Calculate net comfort
    net_comfort = comfort - (discomfort * 0.5)
    
    # Combine with genre
    combined = (net_comfort * 0.6) + (genre_comfort * 0.4)
    
    # Clamp to 0-10
    return max(0, min(10, combined * 10))


if __name__ == "__main__":
    # Test the profiler
    test_movies = [
        {
            "title": "The Notebook",
            "overview": "An epic love story centered around an older man who reads aloud to a woman with Alzheimer's. From a faded notebook, the old man reads the story of a couple who is separated by World War II, and the love letters that kept them together.",
            "genres": ["Romance", "Drama"]
        },
        {
            "title": "The Dark Knight",
            "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.",
            "genres": ["Action", "Crime", "Drama", "Thriller"]
        },
        {
            "title": "Paddington",
            "overview": "A young Peruvian bear travels to London in search of a home. Finding himself lost and alone at Paddington Station, he meets the kindly Brown family, who offer him a temporary haven.",
            "genres": ["Family", "Comedy", "Adventure"]
        },
    ]
    
    print("Testing Movie Emotion Profiler")
    print("=" * 60)
    
    for movie in test_movies:
        print(f"\n{'='*60}")
        print(f"Title: {movie['title']}")
        print(f"Genres: {movie['genres']}")
        print(f"Overview: {movie['overview'][:100]}...")
        
        profile = create_emotion_profile(movie['overview'], movie['genres'])
        
        print(f"\nEmotion Profile:")
        for emotion, score in sorted(profile.emotion_scores.items(), key=lambda x: -x[1]):
            bar = "#" * int(score * 20)
            print(f"  {emotion:25} {score:.2f} {bar}")
        
        print(f"\nDominant Emotions: {profile.dominant_emotions}")
        print(f"Intensity Score: {profile.intensity_score}/10")
        print(f"Catharsis Score: {profile.catharsis_score}/10")
        print(f"Comfort Score: {profile.comfort_score}/10")
        print(f"Confidence: {profile.confidence}")
