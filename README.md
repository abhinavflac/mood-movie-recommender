# 🎬 Movie Mood Recommender

> **An emotion-based movie recommendation system that matches films to your mood journey.**

Instead of asking *"What genre do you like?"*, this system asks:
- 🎭 **"How are you feeling right now?"**
- 🎯 **"How do you want to feel after watching?"**

---

## ✨ Features

- **Mood-Based Recommendations**: Match movies to your emotional state
- **Emotional Arc Mapping**: Understand how a movie's emotions flow
- **Journey Planning**: Get from "stressed" to "relaxed" with the perfect film
- **Catharsis Scoring**: Quantify emotional release potential
- **Explainable Results**: Know *why* a movie is recommended

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/abhinavflac/mood-movie-recommender.git
cd mood-movie-recommender

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your API keys
# - Get TMDB API key from: https://www.themoviedb.org/settings/api
```

### 3. Collect Data

```bash
# Run the data collection pipeline
python -m src.data_collection.pipeline
```

---

## 📁 Project Structure

```
movie-mood-recommender/
├── 📂 config/              # Configuration files
├── 📂 data/                # Data storage
│   ├── raw/                # Raw collected data
│   ├── processed/          # Cleaned data
│   └── embeddings/         # Vector embeddings
├── 📂 src/                 # Source code
│   ├── data_collection/    # Data gathering scripts
│   ├── data_processing/    # Cleaning & validation
│   ├── database/           # Database models
│   ├── emotion_engine/     # Emotion extraction (Phase 2)
│   ├── recommender/        # Recommendation logic (Phase 3)
│   └── api/                # FastAPI backend (Phase 3)
├── 📂 notebooks/           # Jupyter exploration
├── 📂 tests/               # Unit tests
└── 📂 frontend/            # Web UI (Phase 4)
```

---

## 🎭 Emotion Categories

| Emotion | Emoji | Description |
|---------|-------|-------------|
| Cathartic Sadness | 😢 | Deep emotional release through tears |
| Thrilling Tension | 😰 | Edge-of-seat excitement |
| Mind-Blown | 🤯 | Intellectual surprise and revelation |
| Pure Joy | 😂 | Laughter and feel-good happiness |
| Bittersweet Hope | 🥹 | Melancholy mixed with optimism |
| Righteous Anger | 😤 | Satisfying justice and vindication |
| Cozy Comfort | 🫠 | Warm, safe, and relaxing |
| Controlled Fear | 😱 | Safe thrills and scary fun |
| Intellectual Stimulation | 🤔 | Deep thinking and contemplation |
| Romantic Warmth | ❤️‍🔥 | Love, passion, and connection |
| Triumphant & Inspired | 🏆 | Motivation and empowerment |
| Awe & Wonder | 🌌 | Beautiful vastness and amazement |

---

## 🛠️ Development Phases

- [x] **Phase 1**: Data Foundation - Collect movies & reviews
- [ ] **Phase 2**: Emotion Engine - Extract emotions from reviews
- [ ] **Phase 3**: Recommendation Logic - Build matching algorithm
- [ ] **Phase 4**: Frontend & UX - Beautiful web interface

---

## 📊 Data Sources

- **TMDB API**: Movie metadata, posters, trailers
- **IMDB**: User reviews, ratings
- **Letterboxd**: Expressive reviews (optional)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [TMDB](https://www.themoviedb.org/) for the amazing movie database API
- [Hugging Face](https://huggingface.co/) for emotion classification models
- [Plutchik](https://en.wikipedia.org/wiki/Robert_Plutchik) for the emotion wheel framework

---

## 👤 Author

**Abhinav Choudhry** ([@abhinavflac](https://github.com/abhinavflac))

- GitHub: [github.com/abhinavflac](https://github.com/abhinavflac)
- Twitter: [@abhinavflac](https://twitter.com/abhinavflac)

---

**Made with ❤️ for movie lovers who want to feel something.**
