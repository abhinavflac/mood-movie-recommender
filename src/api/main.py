"""
FastAPI Backend for Movie Mood Recommender
============================================
REST API for mood-based movie recommendations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys

# Add UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.recommender import MoodRecommender, get_available_moods


# Initialize FastAPI
app = FastAPI(
    title="Movie Mood Recommender API",
    description="Get movie recommendations based on your mood",
    version="1.0.0"
)

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender (load once)
recommender = None


def get_recommender():
    """Lazy load the recommender."""
    global recommender
    if recommender is None:
        recommender = MoodRecommender()
    return recommender


# Request/Response models
class MoodRequest(BaseModel):
    current_mood: str
    desired_feeling: str
    n_recommendations: int = 5


class EmotionRequest(BaseModel):
    target_emotions: List[str]
    min_intensity: float = 0
    max_intensity: float = 10
    min_comfort: float = 0
    n_recommendations: int = 5


class JourneyRequest(BaseModel):
    start_mood: str
    end_mood: str
    n_movies: int = 3


class MovieResponse(BaseModel):
    title: str
    overview: str
    genres: List
    poster_url: str
    dominant_emotions: List
    intensity_score: float
    comfort_score: float
    match_score: float
    explanation: str


# API Endpoints
@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "healthy",
        "message": "Movie Mood Recommender API",
        "version": "1.0.0"
    }


@app.get("/moods")
async def get_moods():
    """Get available mood options."""
    return get_available_moods()


@app.post("/recommend/mood", response_model=List[MovieResponse])
async def recommend_by_mood(request: MoodRequest):
    """
    Get recommendations based on current mood and desired feeling.
    
    Example:
    - current_mood: "stressed", "bored", "sad", "happy"
    - desired_feeling: "feel-good", "thrilled", "inspired", "cry"
    """
    rec = get_recommender()
    
    try:
        recommendations = rec.recommend_by_mood(
            current_mood=request.current_mood,
            desired_feeling=request.desired_feeling,
            n_recommendations=request.n_recommendations
        )
        
        return [r.to_dict() for r in recommendations]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/emotions", response_model=List[MovieResponse])
async def recommend_by_emotions(request: EmotionRequest):
    """
    Get recommendations by specifying exact emotions.
    
    Available emotions:
    - cathartic_sadness, thrilling_tension, mind_blown
    - pure_joy, bittersweet_hope, righteous_anger
    - cozy_comfort, controlled_fear, intellectual_stimulation
    - romantic_warmth, triumphant_inspired, awe_wonder
    """
    rec = get_recommender()
    
    try:
        recommendations = rec.recommend_by_emotions(
            target_emotions=request.target_emotions,
            min_intensity=request.min_intensity,
            max_intensity=request.max_intensity,
            min_comfort=request.min_comfort,
            n_recommendations=request.n_recommendations
        )
        
        return [r.to_dict() for r in recommendations]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/journey", response_model=List[MovieResponse])
async def recommend_journey(request: JourneyRequest):
    """
    Get a movie journey to transition from one mood to another.
    
    Example: start_mood="sad", end_mood="inspired"
    Returns a sequence of movies to gradually shift your mood.
    """
    rec = get_recommender()
    
    try:
        journey = rec.get_mood_journey(
            start_mood=request.start_mood,
            end_mood=request.end_mood,
            n_movies=request.n_movies
        )
        
        return [r.to_dict() for r in journey]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movie/{title}")
async def get_movie(title: str):
    """Get details for a specific movie."""
    rec = get_recommender()
    
    # Search for movie
    df = rec.movies_df
    matches = df[df[' '].str.lower().str.contains(title.lower(), na=False)]
    
    if len(matches) == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = matches.iloc[0]
    
    return {
        "title": movie.get(' ', 'Unknown'),
        "overview": movie.get('overview', ''),
        "genres": movie.get('genres', []),
        "poster_url": movie.get('poster_url', ''),
        "dominant_emotions": movie.get('dominant_emotions', []),
        "intensity_score": movie.get('intensity_score', 5),
        "comfort_score": movie.get('comfort_score', 5),
        "catharsis_score": movie.get('catharsis_score', 5),
    }


# Chat endpoint request model
class ChatRequest(BaseModel):
    message: str


# Keywords for natural language mood detection
MOOD_KEYWORDS = {
    "stressed": ["stressed", "stress", "overwhelmed", "anxious", "anxiety", "tense", "pressure"],
    "sad": ["sad", "depressed", "down", "unhappy", "lonely", "melancholy", "blue", "crying"],
    "bored": ["bored", "boring", "nothing to do", "uninterested", "dull"],
    "happy": ["happy", "good", "great", "excited", "joyful", "cheerful"],
    "tired": ["tired", "exhausted", "sleepy", "worn out", "fatigued"],
    "angry": ["angry", "frustrated", "annoyed", "mad", "furious"],
    "lonely": ["lonely", "alone", "isolated", "single"],
    "romantic": ["romantic", "love", "date night", "partner", "couple"],
    "curious": ["curious", "interesting", "learn", "documentary", "educational"],
    "adventurous": ["adventurous", "adventure", "explore", "exciting"],
}

FEELING_KEYWORDS = {
    "feel-good": ["feel good", "feel-good", "uplifting", "positive", "happy ending", "light", "cheerful"],
    "thrilled": ["thrilling", "thriller", "exciting", "action", "edge of seat", "adrenaline", "intense"],
    "inspired": ["inspired", "inspiring", "motivating", "motivation", "uplifting", "triumphant"],
    "cry": ["cry", "crying", "emotional", "tearjerker", "sad movie", "cathartic"],
    "laugh": ["laugh", "funny", "comedy", "hilarious", "humor"],
    "think": ["think", "thought-provoking", "mind-bending", "intellectual", "smart", "clever"],
    "scared": ["scared", "scary", "horror", "frightening", "terrifying", "creepy"],
    "romantic": ["romantic", "romance", "love story", "relationship"],
    "relaxed": ["relaxed", "relaxing", "calm", "peaceful", "cozy", "comfort"],
    "amazed": ["amazed", "amazing", "spectacular", "epic", "visually stunning"],
}


def detect_mood_from_text(text: str) -> tuple:
    """
    Detect mood and desired feeling from natural language text.
    
    Returns:
        (current_mood, desired_feeling)
    """
    text_lower = text.lower()
    
    # Detect current mood
    current_mood = "bored"  # default
    max_mood_matches = 0
    
    for mood, keywords in MOOD_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > max_mood_matches:
            max_mood_matches = matches
            current_mood = mood
    
    # Detect desired feeling
    desired_feeling = "feel-good"  # default
    max_feeling_matches = 0
    
    for feeling, keywords in FEELING_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > max_feeling_matches:
            max_feeling_matches = matches
            desired_feeling = feeling
    
    # Special patterns
    if "sunday" in text_lower and ("rainy" in text_lower or "lazy" in text_lower):
        desired_feeling = "relaxed"
    if "date" in text_lower:
        desired_feeling = "romantic"
    if "can't sleep" in text_lower or "insomnia" in text_lower:
        current_mood = "anxious"
        desired_feeling = "relaxed"
    
    return current_mood, desired_feeling


def generate_chat_response(current_mood: str, desired_feeling: str, num_movies: int) -> str:
    """Generate a natural language response."""
    responses = {
        "feel-good": f"I sense you could use some positivity! Here are some uplifting films that'll brighten your day:",
        "thrilled": f"Looking for excitement? These heart-pounding picks will get your adrenaline pumping:",
        "inspired": f"Ready to be motivated? These inspiring films will lift your spirits:",
        "cry": f"Sometimes we all need a good cry. These emotional gems will help you release those feelings:",
        "laugh": f"Laughter is the best medicine! Here are some comedies guaranteed to make you smile:",
        "think": f"Ready for a mental workout? These thought-provoking films will keep your mind engaged:",
        "scared": f"In the mood for some safe scares? These films will thrill without traumatizing:",
        "romantic": f"Love is in the air! These romantic picks are perfect for the mood:",
        "relaxed": f"Time to unwind! These cozy films are perfect for relaxation:",
        "amazed": f"Prepare to be amazed! These visually stunning films will blow your mind:",
    }
    
    return responses.get(desired_feeling, f"Based on what you're looking for, here are my top picks:")


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Natural language chat endpoint.
    
    Process user message and return movie recommendations with explanation.
    """
    rec = get_recommender()
    
    try:
        # Detect mood and feeling from text
        current_mood, desired_feeling = detect_mood_from_text(request.message)
        
        # Get recommendations
        recommendations = rec.recommend_by_mood(
            current_mood=current_mood,
            desired_feeling=desired_feeling,
            n_recommendations=5
        )
        
        # Generate response
        response_text = generate_chat_response(current_mood, desired_feeling, len(recommendations))
        
        return {
            "response": response_text,
            "detected_mood": current_mood,
            "detected_feeling": desired_feeling,
            "movies": [r.to_dict() for r in recommendations]
        }
        
    except Exception as e:
        return {
            "response": f"I had trouble understanding that. Could you tell me more about what kind of movie experience you're looking for?",
            "movies": []
        }


# Run with: uvicorn src.api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
