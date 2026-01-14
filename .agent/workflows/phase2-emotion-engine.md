---
description: Phase 2 - Emotion Engine Implementation Plan
---

# Phase 2: Emotion Engine

## Overview
Build an emotion detection system using available movie data (4,967 movies with overviews).

## Available Data
- 4,967 movies with text descriptions (overviews)
- Genres for each movie
- Movie metadata (runtime, release date, etc.)

---

## Implementation Steps

### Step 1: Emotion Classifier Setup
Create emotion detection using pre-trained NLP models.

**File:** `src/emotion_engine/classifier.py`

**Approach:**
- Use HuggingFace Transformers for emotion detection
- Model: `j-hartmann/emotion-english-distilroberta-base` (7 emotions)
- Alternative: `SamLowe/roberta-base-go_emotions` (28 emotions)

**Output:** Emotion scores for each movie overview

---

### Step 2: Genre-to-Emotion Mapping
Create baseline emotion profiles from genres.

**File:** `src/emotion_engine/genre_mapper.py`

**Logic:**
- Horror -> fear, tension
- Comedy -> joy, amusement
- Drama -> sadness, complex emotions
- Action -> excitement, thrill
- Romance -> warmth, love

This provides fallback when NLP is uncertain.

---

### Step 3: Movie Emotion Profiler
Combine NLP + genre mapping for each movie.

**File:** `src/emotion_engine/profiler.py`

**Process:**
1. Run emotion classifier on movie overview
2. Apply genre-based emotion boosts
3. Normalize to our 12 emotion categories
4. Calculate intensity, catharsis, comfort scores

---

### Step 4: Batch Processing Pipeline
Process all 4,967 movies.

**File:** `src/emotion_engine/pipeline.py`

**Features:**
- Batch processing (GPU if available)
- Progress tracking
- Save to database + parquet

---

### Step 5: Emotion Profile Storage
Store results in database.

**Updates to:** `src/database/models.py`

**Fields to populate:**
- emotion_profile (JSON)
- dominant_emotions (list)
- intensity_score
- catharsis_score
- comfort_score

---

## File Structure After Phase 2

```
src/emotion_engine/
├── __init__.py
├── classifier.py      # HuggingFace emotion detection
├── genre_mapper.py    # Genre to emotion mapping
├── profiler.py        # Combine sources, create profile
├── pipeline.py        # Batch processing
└── utils.py           # Helper functions
```

---

## Emotion Category Mapping

Map model outputs to our 12 categories:

| Model Emotion | Our Category |
|---------------|--------------|
| joy | pure_joy |
| sadness | cathartic_sadness |
| fear | controlled_fear |
| anger | righteous_anger |
| surprise | mind_blown |
| love | romantic_warmth |
| excitement | thrilling_tension |

---

## Commands to Run

```powershell
// turbo
# Step 1: Install transformers
pip install transformers torch

// turbo
# Step 2: Run emotion pipeline
python -m src.emotion_engine.pipeline

// turbo
# Step 3: Verify results
python -c "from src.database import get_session, Movie; s=get_session(); print(s.query(Movie).filter(Movie.emotion_processed==True).count())"
```

---

## Success Criteria

- [ ] All 4,967 movies have emotion profiles
- [ ] Each movie has dominant_emotions list
- [ ] Intensity/catharsis/comfort scores populated
- [ ] Processing time < 30 minutes

---

## Estimated Time

| Task | Time |
|------|------|
| Classifier setup | 30 min |
| Genre mapper | 20 min |
| Profiler | 30 min |
| Pipeline + testing | 1 hour |
| **Total** | ~2.5 hours |
