"""
Recommender Module
==================
Mood-based movie recommendation engine.
"""

from .engine import (
    MoodRecommender,
    MovieRecommendation,
    get_available_moods,
    MOOD_PRESETS,
    DESIRED_FEELINGS,
    EMOTION_CATEGORIES,
)

__all__ = [
    "MoodRecommender",
    "MovieRecommendation",
    "get_available_moods",
    "MOOD_PRESETS",
    "DESIRED_FEELINGS",
    "EMOTION_CATEGORIES",
]
