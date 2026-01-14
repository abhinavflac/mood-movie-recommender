# 🎬 MovieMood - AI-Powered Movie Recommendations by Mood

> **Find the perfect movie for exactly how you're feeling.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

1. [What is MovieMood?](#-what-is-moviemood)
2. [How It Works](#-how-it-works)
3. [Project Architecture](#-project-architecture)
4. [Tech Stack](#-tech-stack)
5. [Quick Start](#-quick-start)
6. [Detailed Code Walkthrough](#-detailed-code-walkthrough)
7. [API Reference](#-api-reference)
8. [Frontend Guide](#-frontend-guide)
9. [Database Schema](#-database-schema)
10. [Deployment](#-deployment)
11. [Author](#-author)

---

## 🎯 What is MovieMood?

MovieMood is an **emotion-based movie recommendation system** that suggests films based on:
- **Your current mood** (stressed, sad, bored, happy, etc.)
- **What you want to feel** (thrilled, inspired, comforted, etc.)

Unlike traditional recommenders that use genres or ratings, MovieMood uses **NLP (Natural Language Processing)** to analyze movie descriptions and assign **emotional profiles** to each film.

### Key Features

| Feature | Description |
|---------|-------------|
| 🎨 **Visual Mood Picker** | Click colorful mood cards to get recommendations |
| 💬 **AI Chat** | Type naturally: "I'm stressed and need something uplifting" |
| 🎭 **12 Emotion Categories** | From "cozy comfort" to "thrilling tension" |
| 📊 **Emotion Scores** | Intensity, catharsis, and comfort ratings |
| 🛤️ **Mood Journeys** | Movie sequences to transition between moods |

---

## 🧠 How It Works

### The Three-Phase Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: DATA COLLECTION                     │
├─────────────────────────────────────────────────────────────────┤
│  TMDB API  ──▶  Movie Metadata  ──▶  5,000 Movies Collected     │
│  (titles, overviews, genres, posters, trailers)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 2: EMOTION ENGINE                      │
├─────────────────────────────────────────────────────────────────┤
│  Movie Overview  ──▶  NLP Model  ──▶  Emotion Scores            │
│       +                                                          │
│  Movie Genres  ──▶  Genre Mapper  ──▶  Genre-Based Emotions     │
│                              │                                   │
│                              ▼                                   │
│                   Combined Emotion Profile                       │
│                   (intensity, catharsis, comfort)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 3: RECOMMENDATION                      │
├─────────────────────────────────────────────────────────────────┤
│  User Mood  ──▶  Emotion Matching  ──▶  Ranked Movies           │
│       +              Algorithm              +                    │
│  Desired Feeling                       Explanations              │
└─────────────────────────────────────────────────────────────────┘
```

### The 12 Emotion Categories

| Emotion | Description | Example Movies |
|---------|-------------|----------------|
| `pure_joy` | Happiness, delight | Comedies, feel-good films |
| `cathartic_sadness` | Emotional release | Dramas, tearjerkers |
| `thrilling_tension` | Edge-of-seat excitement | Thrillers, action |
| `controlled_fear` | Safe scares | Horror, suspense |
| `romantic_warmth` | Love, connection | Romance |
| `cozy_comfort` | Relaxation, safety | Family, light comedies |
| `mind_blown` | Surprise, twists | Mysteries, plot-twists |
| `intellectual_stimulation` | Deep thinking | Documentaries, sci-fi |
| `triumphant_inspired` | Motivation, triumph | Sports, biopics |
| `bittersweet_hope` | Mixed emotions | Coming-of-age, drama |
| `righteous_anger` | Justice, revenge | Crime, action |
| `awe_wonder` | Amazement | Fantasy, epic adventures |

---

## 📁 Project Architecture

```
moviemood/
│
├── 📂 src/                          # Backend source code
│   ├── 📂 data_collection/          # Phase 1: Collect movie data
│   │   ├── tmdb_collector.py        # Fetch movies from TMDB API
│   │   ├── review_scraper.py        # Scrape IMDB reviews (optional)
│   │   ├── config.py                # Configuration & settings
│   │   └── pipeline.py              # Orchestrate data collection
│   │
│   ├── 📂 data_processing/          # Clean & validate data
│   │   ├── cleaner.py               # Data cleaning functions
│   │   └── processor.py             # Processing pipeline
│   │
│   ├── 📂 emotion_engine/           # Phase 2: Emotion detection
│   │   ├── classifier.py            # HuggingFace NLP model
│   │   ├── genre_mapper.py          # Genre → emotion mapping
│   │   ├── profiler.py              # Combine NLP + genres
│   │   └── pipeline.py              # Process all movies
│   │
│   ├── 📂 recommender/              # Phase 3: Recommendations
│   │   └── engine.py                # Mood matching algorithm
│   │
│   ├── 📂 api/                      # FastAPI backend
│   │   └── main.py                  # REST endpoints
│   │
│   └── 📂 database/                 # Data models
│       └── models.py                # SQLAlchemy models
│
├── 📂 frontend/                     # Next.js frontend
│   ├── 📂 src/
│   │   ├── 📂 app/                  # Next.js App Router
│   │   │   ├── layout.tsx           # Root layout
│   │   │   ├── page.tsx             # Main page
│   │   │   └── globals.css          # Tailwind styles
│   │   ├── 📂 components/           # React components
│   │   │   ├── Header.tsx           # Navigation header
│   │   │   ├── MoodSelector.tsx     # Mood selection grid
│   │   │   ├── DesiredFeelingSelector.tsx
│   │   │   ├── MovieGrid.tsx        # Movie cards display
│   │   │   └── ChatInterface.tsx    # AI chat component
│   │   └── 📂 types/                # TypeScript types
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── 📂 data/                         # Data storage
│   ├── 📂 raw/                      # Raw collected data
│   └── 📂 processed/                # Processed with emotions
│
├── 📂 config/                       # Configuration files
│   └── settings.yaml                # Project settings
│
├── .env                             # API keys (DO NOT COMMIT)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Core language |
| **FastAPI** | REST API framework |
| **HuggingFace Transformers** | Emotion detection NLP |
| **Pandas** | Data manipulation |
| **SQLAlchemy** | Database ORM |
| **SQLite/PostgreSQL** | Data storage |
| **Loguru** | Logging |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Styling |
| **Framer Motion** | Animations |
| **Lucide Icons** | Icon library |

### APIs & Data
| Service | Purpose |
|---------|---------|
| **TMDB API** | Movie metadata |
| **HuggingFace** | Pre-trained emotion model |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- TMDB API Key (free at [themoviedb.org](https://www.themoviedb.org/settings/api))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/abhinavflac/mood-movie-recommender.git
cd mood-movie-recommender

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env and add your TMDB_API_KEY

# 5. Collect movie data (one-time)
python -m src.data_collection.pipeline --target 1000 --skip-reviews

# 6. Process emotions (one-time)
python -m src.emotion_engine.pipeline --source csv --csv-path movies.csv

# 7. Start the backend
python -m uvicorn src.api.main:app --port 8000

# 8. In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

---

## 📚 Detailed Code Walkthrough

### Phase 1: Data Collection (`src/data_collection/`)

#### `tmdb_collector.py` - Movie Data Fetcher

```python
class TMDBCollector:
    """
    Fetches movie data from The Movie Database (TMDB) API.
    
    Key Methods:
    - get_popular_movies(): Fetches trending/popular movies
    - get_top_rated_movies(): Fetches critically acclaimed films
    - get_movie_details(): Gets full info for a single movie
    - collect_comprehensive_dataset(): Main method to collect N movies
    
    Rate Limiting:
    - 4 requests per second (TMDB limit)
    - Automatic retry on failures
    """
```

**How it works:**
1. Fetches movie IDs from popular/top-rated lists
2. Gets detailed info for each movie (cast, crew, trailer, etc.)
3. Saves to parquet files for fast loading

#### `pipeline.py` - Data Collection Orchestrator

```python
class DataPipeline:
    """
    Orchestrates the entire data collection workflow.
    
    Steps:
    1. collect_movies() → Fetch from TMDB
    2. collect_reviews() → Scrape from IMDB (optional)
    3. process_data() → Clean and validate
    4. load_to_database() → Store in SQLite/PostgreSQL
    """
```

---

### Phase 2: Emotion Engine (`src/emotion_engine/`)

#### `classifier.py` - NLP Emotion Detection

```python
def classify_text(text: str) -> Dict[str, float]:
    """
    Analyzes text and returns emotion scores.
    
    Uses: j-hartmann/emotion-english-distilroberta-base
    
    Input: "A heartwarming story about love and family"
    Output: {'joy': 0.8, 'sadness': 0.1, 'fear': 0.05, ...}
    """
    
# The model outputs 7 emotions:
# joy, sadness, anger, fear, surprise, disgust, neutral

# We map these to our 12 emotion categories:
MODEL_TO_CATEGORY = {
    'joy': 'pure_joy',
    'sadness': 'cathartic_sadness',
    'anger': 'righteous_anger',
    'fear': 'controlled_fear',
    'surprise': 'mind_blown',
    # ... etc
}
```

#### `genre_mapper.py` - Genre-Based Emotions

```python
GENRE_EMOTION_MAP = {
    'horror': {
        'controlled_fear': 0.9,      # Horror = fear
        'thrilling_tension': 0.7,    # Also tension
    },
    'comedy': {
        'pure_joy': 0.9,             # Comedy = joy
        'cozy_comfort': 0.5,         # Also comfort
    },
    'romance': {
        'romantic_warmth': 0.9,      # Romance = love
        'bittersweet_hope': 0.5,     # Often bittersweet
    },
    # ... etc
}

def get_genre_emotions(genres: List[str]) -> Dict[str, float]:
    """
    Maps movie genres to expected emotions.
    
    Input: ['Horror', 'Thriller']
    Output: {'controlled_fear': 0.9, 'thrilling_tension': 0.8}
    """
```

#### `profiler.py` - Combine All Sources

```python
def create_emotion_profile(overview: str, genres: List[str]) -> EmotionProfile:
    """
    Creates a complete emotion profile for a movie.
    
    Combines:
    1. NLP analysis of movie overview (60% weight)
    2. Genre-based emotions (40% weight)
    
    Returns:
        EmotionProfile with:
        - emotion_scores: All emotion scores (0-1)
        - dominant_emotions: Top 3 emotions
        - intensity_score: How intense (0-10)
        - catharsis_score: Emotional release potential (0-10)
        - comfort_score: Feel-good level (0-10)
    """
```

**Example Output:**
```python
{
    "emotion_scores": {
        "thrilling_tension": 0.85,
        "controlled_fear": 0.72,
        "mind_blown": 0.45
    },
    "dominant_emotions": ["thrilling_tension", "controlled_fear", "mind_blown"],
    "intensity_score": 8.5,
    "catharsis_score": 4.2,
    "comfort_score": 2.1
}
```

---

### Phase 3: Recommendation Engine (`src/recommender/`)

#### `engine.py` - Mood Matching Algorithm

```python
class MoodRecommender:
    """
    Matches user mood to movies with similar emotional profiles.
    
    Key Methods:
    - recommend_by_mood(current_mood, desired_feeling)
    - recommend_by_emotions(target_emotions)
    - get_mood_journey(start_mood, end_mood)
    """
    
    def _calculate_match_score(self, movie, mood_params, desired_emotions):
        """
        Calculates how well a movie matches the user's needs.
        
        Score Components:
        1. Emotion Match (40%) - Does movie have desired emotions?
        2. Intensity Match (30%) - Does intensity fit current mood?
        3. Comfort Match (30%) - Does comfort level fit needs?
        
        Example:
        - User: stressed (wants low intensity, high comfort)
        - Movie: cozy comedy (low intensity, high comfort)
        - Match: 90%
        """
```

**Mood Presets:**
```python
MOOD_PRESETS = {
    "stressed": {"intensity": "low", "comfort": "high"},
    "bored": {"intensity": "high", "primary": "thrilling_tension"},
    "sad": {"primary": "cathartic_sadness", "comfort": "medium"},
    "happy": {"primary": "pure_joy", "comfort": "high"},
    # ... etc
}

DESIRED_FEELINGS = {
    "feel-good": ["pure_joy", "cozy_comfort", "romantic_warmth"],
    "thrilled": ["thrilling_tension", "controlled_fear", "mind_blown"],
    "cry": ["cathartic_sadness", "bittersweet_hope"],
    # ... etc
}
```

---

### API Layer (`src/api/`)

#### `main.py` - FastAPI Endpoints

```python
# Available Endpoints:

@app.post("/recommend/mood")
# Input: {"current_mood": "stressed", "desired_feeling": "feel-good"}
# Output: List of matching movies with explanations

@app.post("/recommend/emotions") 
# Input: {"target_emotions": ["pure_joy", "cozy_comfort"]}
# Output: Movies with those specific emotions

@app.post("/recommend/journey")
# Input: {"start_mood": "sad", "end_mood": "inspired"}
# Output: Sequence of movies to transition moods

@app.post("/chat")
# Input: {"message": "I'm stressed and need something uplifting"}
# Natural language processing → movie recommendations
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /moods`
Returns available mood options.

```json
{
  "current_moods": ["stressed", "sad", "bored", "happy", "tired", ...],
  "desired_feelings": ["feel-good", "thrilled", "inspired", "cry", ...],
  "emotions": ["pure_joy", "cathartic_sadness", ...]
}
```

#### `POST /recommend/mood`
Get recommendations based on mood.

**Request:**
```json
{
  "current_mood": "stressed",
  "desired_feeling": "feel-good",
  "n_recommendations": 5
}
```

**Response:**
```json
[
  {
    "title": "Paddington",
    "overview": "A young bear travels to London...",
    "genres": ["Family", "Comedy"],
    "poster_url": "https://image.tmdb.org/...",
    "dominant_emotions": ["pure_joy", "cozy_comfort"],
    "intensity_score": 3.2,
    "comfort_score": 8.5,
    "match_score": 0.92,
    "explanation": "A comforting choice to lift your spirits."
  }
]
```

#### `POST /chat`
Natural language movie recommendations.

**Request:**
```json
{
  "message": "I'm feeling stressed and need something uplifting"
}
```

**Response:**
```json
{
  "response": "I sense you could use some positivity! Here are some uplifting films...",
  "detected_mood": "stressed",
  "detected_feeling": "feel-good",
  "movies": [...]
}
```

---

## 🎨 Frontend Guide

### Component Breakdown

#### `page.tsx` - Main Application Flow

```tsx
// State machine with 5 steps:
type Step = 'choose' | 'mood' | 'feeling' | 'results' | 'chat'

// Flow:
// choose → (mood → feeling → results) OR (chat)
```

#### `MoodSelector.tsx` - Mood Selection Grid

```tsx
const moods = [
  { id: 'stressed', label: 'Stressed', icon: Flame, color: 'from-red-500' },
  { id: 'sad', label: 'Sad', icon: CloudRain, color: 'from-blue-500' },
  // ... 10 mood options with icons and colors
]

// Animated grid of clickable mood cards
// Uses Framer Motion for stagger animations
```

#### `ChatInterface.tsx` - AI Chat

```tsx
// ChatGPT-style interface with:
// - Message bubbles (user/assistant)
// - Inline movie cards in responses
// - Suggestion chips
// - Loading states

// Calls /api/chat endpoint with natural language
```

#### `MovieGrid.tsx` - Results Display

```tsx
// Displays movie cards with:
// - Poster image
// - Match percentage
// - Emotion tags
// - Intensity/comfort scores
// - Explanation text
```

### Styling (`globals.css`)

```css
/* Custom utility classes */
.glass-card    /* Glass morphism effect */
.mood-button   /* Gradient button */
.text-gradient /* Colorful text */
.card-hover    /* Hover animation */

/* Color palette */
--dark-950: #020617;  /* Background */
--purple-500: Primary accent
--pink-500: Secondary accent
```

---

## 💾 Database Schema

```sql
-- Movies table
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    tmdb_id INTEGER UNIQUE,
    title VARCHAR(255),
    overview TEXT,
    genres JSON,
    release_date DATE,
    runtime INTEGER,
    poster_url VARCHAR(500),
    
    -- Emotion data (added by Phase 2)
    emotion_profile JSON,
    dominant_emotions JSON,
    intensity_score FLOAT,
    catharsis_score FLOAT,
    comfort_score FLOAT,
    emotion_processed BOOLEAN
);

-- Emotion categories
CREATE TABLE emotion_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50),        -- e.g., "pure_joy"
    display_name VARCHAR(50), -- e.g., "Pure Joy"
    description TEXT
);
```

---

## 🚢 Deployment

### Backend (Railway/Render/Fly.io)

```bash
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel)

1. Push to GitHub
2. Import repo in Vercel
3. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```
4. Deploy!

---

## 📈 Performance Tips

1. **Reduce movie count** for faster processing
2. **Use GPU** for emotion classification (if available)
3. **Cache recommendations** for common mood combinations
4. **Pre-compute** emotion profiles during data collection

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| TMDB API errors | Check API key in `.env` |
| Slow emotion processing | Reduce batch size or use GPU |
| Frontend can't connect | Ensure backend is running on port 8000 |
| Unicode errors on Windows | Run PowerShell as UTF-8 |

---

## 👤 Author

**Abhinav Choudhry**
- GitHub: [@abhinavflac](https://github.com/abhinavflac)

---

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for movie data
- [HuggingFace](https://huggingface.co/) for the emotion model
- [Vercel](https://vercel.com/) for hosting

---

<p align="center">
  Made with ❤️ and lots of ☕
</p>
