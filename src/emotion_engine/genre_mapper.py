"""
Genre to Emotion Mapper
========================
Map movie genres to expected emotional experiences.
"""

from typing import Dict, List, Set


# Genre to emotion category mappings
# Each genre maps to a set of likely emotions with weights
GENRE_EMOTION_MAP = {
    # High-energy genres
    'action': {
        'thrilling_tension': 0.8,
        'triumphant_inspired': 0.6,
        'righteous_anger': 0.4,
        'awe_wonder': 0.3,
    },
    'adventure': {
        'awe_wonder': 0.8,
        'thrilling_tension': 0.6,
        'triumphant_inspired': 0.5,
        'pure_joy': 0.4,
    },
    'thriller': {
        'thrilling_tension': 0.9,
        'controlled_fear': 0.6,
        'mind_blown': 0.5,
        'intellectual_stimulation': 0.4,
    },
    
    # Emotional genres
    'drama': {
        'cathartic_sadness': 0.7,
        'bittersweet_hope': 0.6,
        'intellectual_stimulation': 0.4,
        'triumphant_inspired': 0.3,
    },
    'romance': {
        'romantic_warmth': 0.9,
        'bittersweet_hope': 0.5,
        'cathartic_sadness': 0.3,
        'pure_joy': 0.4,
    },
    
    # Feel-good genres
    'comedy': {
        'pure_joy': 0.9,
        'cozy_comfort': 0.5,
        'romantic_warmth': 0.3,
    },
    'family': {
        'cozy_comfort': 0.8,
        'pure_joy': 0.7,
        'bittersweet_hope': 0.4,
        'romantic_warmth': 0.3,
    },
    'animation': {
        'awe_wonder': 0.7,
        'pure_joy': 0.6,
        'cozy_comfort': 0.5,
    },
    
    # Dark/intense genres
    'horror': {
        'controlled_fear': 0.9,
        'thrilling_tension': 0.7,
        'cathartic_sadness': 0.2,
    },
    'crime': {
        'thrilling_tension': 0.7,
        'righteous_anger': 0.6,
        'intellectual_stimulation': 0.5,
        'mind_blown': 0.4,
    },
    'mystery': {
        'intellectual_stimulation': 0.8,
        'thrilling_tension': 0.6,
        'mind_blown': 0.7,
    },
    'war': {
        'cathartic_sadness': 0.7,
        'righteous_anger': 0.6,
        'triumphant_inspired': 0.5,
        'thrilling_tension': 0.5,
    },
    
    # Mind-expanding genres
    'science fiction': {
        'awe_wonder': 0.8,
        'intellectual_stimulation': 0.7,
        'mind_blown': 0.6,
        'thrilling_tension': 0.4,
    },
    'fantasy': {
        'awe_wonder': 0.8,
        'pure_joy': 0.5,
        'triumphant_inspired': 0.5,
        'romantic_warmth': 0.3,
    },
    'documentary': {
        'intellectual_stimulation': 0.9,
        'mind_blown': 0.5,
        'awe_wonder': 0.4,
    },
    
    # Other genres
    'music': {
        'pure_joy': 0.7,
        'triumphant_inspired': 0.6,
        'romantic_warmth': 0.5,
    },
    'history': {
        'intellectual_stimulation': 0.7,
        'bittersweet_hope': 0.5,
        'cathartic_sadness': 0.4,
    },
    'western': {
        'righteous_anger': 0.6,
        'thrilling_tension': 0.5,
        'triumphant_inspired': 0.4,
    },
}


def get_genre_emotions(genres: List[str]) -> Dict[str, float]:
    """
    Get emotion scores based on movie genres.
    
    Args:
        genres: List of genre names
        
    Returns:
        Dictionary of emotion category -> score (0-1)
    """
    if not genres:
        return {}
    
    emotion_scores = {}
    genre_count = 0
    
    for genre in genres:
        genre_lower = genre.lower().strip()
        
        if genre_lower in GENRE_EMOTION_MAP:
            genre_count += 1
            genre_emotions = GENRE_EMOTION_MAP[genre_lower]
            
            for emotion, score in genre_emotions.items():
                if emotion in emotion_scores:
                    # Take average if multiple genres suggest same emotion
                    emotion_scores[emotion] = (emotion_scores[emotion] + score) / 2
                else:
                    emotion_scores[emotion] = score
    
    return emotion_scores


def get_intensity_from_genres(genres: List[str]) -> float:
    """
    Estimate intensity level from genres.
    
    Args:
        genres: List of genre names
        
    Returns:
        Intensity score (0-10)
    """
    HIGH_INTENSITY = {'action', 'thriller', 'horror', 'war', 'crime'}
    MEDIUM_INTENSITY = {'adventure', 'mystery', 'science fiction', 'drama', 'western'}
    LOW_INTENSITY = {'comedy', 'family', 'romance', 'animation', 'music'}
    
    scores = []
    
    for genre in genres:
        genre_lower = genre.lower().strip()
        
        if genre_lower in HIGH_INTENSITY:
            scores.append(8)
        elif genre_lower in MEDIUM_INTENSITY:
            scores.append(5)
        elif genre_lower in LOW_INTENSITY:
            scores.append(3)
        else:
            scores.append(5)  # Default medium
    
    return sum(scores) / len(scores) if scores else 5


def get_comfort_from_genres(genres: List[str]) -> float:
    """
    Estimate comfort level from genres.
    
    Args:
        genres: List of genre names
        
    Returns:
        Comfort score (0-10)
    """
    HIGH_COMFORT = {'comedy', 'family', 'animation', 'romance', 'music'}
    MEDIUM_COMFORT = {'adventure', 'fantasy', 'drama', 'documentary'}
    LOW_COMFORT = {'horror', 'thriller', 'war', 'crime'}
    
    scores = []
    
    for genre in genres:
        genre_lower = genre.lower().strip()
        
        if genre_lower in HIGH_COMFORT:
            scores.append(8)
        elif genre_lower in MEDIUM_COMFORT:
            scores.append(5)
        elif genre_lower in LOW_COMFORT:
            scores.append(2)
        else:
            scores.append(5)
    
    return sum(scores) / len(scores) if scores else 5


if __name__ == "__main__":
    # Test the mapper
    test_cases = [
        ['Action', 'Adventure'],
        ['Comedy', 'Romance'],
        ['Horror', 'Thriller'],
        ['Drama'],
        ['Science Fiction', 'Mystery'],
    ]
    
    print("Testing Genre Mapper")
    print("=" * 50)
    
    for genres in test_cases:
        print(f"\nGenres: {genres}")
        emotions = get_genre_emotions(genres)
        intensity = get_intensity_from_genres(genres)
        comfort = get_comfort_from_genres(genres)
        
        print(f"Emotions: {emotions}")
        print(f"Intensity: {intensity:.1f}")
        print(f"Comfort: {comfort:.1f}")
