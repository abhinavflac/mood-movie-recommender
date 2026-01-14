"""
Emotion Classifier
===================
Detect emotions from text using pre-trained NLP models.
"""

import os
from typing import Dict, List, Optional
from loguru import logger

# Lazy load transformers to avoid slow imports
_classifier = None


def get_classifier():
    """
    Get or create the emotion classifier (lazy loading).
    
    Returns:
        HuggingFace pipeline for emotion classification
    """
    global _classifier
    
    if _classifier is None:
        logger.info("Loading emotion classification model...")
        
        try:
            from transformers import pipeline
            
            # Use a lightweight emotion model
            # Options:
            # - j-hartmann/emotion-english-distilroberta-base (7 emotions)
            # - SamLowe/roberta-base-go_emotions (28 emotions)
            # - bhadresh-savani/distilbert-base-uncased-emotion (6 emotions)
            
            _classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None,  # Return all emotion scores
                device=-1    # CPU (-1) or GPU (0, 1, etc.)
            )
            
            logger.success("Emotion model loaded!")
            
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            raise
    
    return _classifier


def classify_text(text: str, max_length: int = 512) -> Dict[str, float]:
    """
    Classify emotions in a text.
    
    Args:
        text: Input text to analyze
        max_length: Maximum text length (truncate if longer)
        
    Returns:
        Dictionary of emotion -> score (0-1)
    """
    if not text or len(text.strip()) < 10:
        return {}
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    try:
        classifier = get_classifier()
        results = classifier(text)
        
        # Convert to dict: [{label: score}, ...] -> {label: score}
        if results and isinstance(results[0], list):
            results = results[0]
        
        emotions = {r['label'].lower(): r['score'] for r in results}
        return emotions
        
    except Exception as e:
        logger.warning(f"Classification error: {e}")
        return {}


def classify_batch(texts: List[str], batch_size: int = 32) -> List[Dict[str, float]]:
    """
    Classify emotions in multiple texts.
    
    Args:
        texts: List of input texts
        batch_size: Batch size for processing
        
    Returns:
        List of emotion dictionaries
    """
    classifier = get_classifier()
    results = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Clean and truncate
        batch = [t[:512] if t else "" for t in batch]
        
        try:
            batch_results = classifier(batch)
            
            for result in batch_results:
                if isinstance(result, list):
                    emotions = {r['label'].lower(): r['score'] for r in result}
                else:
                    emotions = {result['label'].lower(): result['score']}
                results.append(emotions)
                
        except Exception as e:
            logger.warning(f"Batch classification error: {e}")
            results.extend([{} for _ in batch])
    
    return results


# Mapping from model emotions to our emotion categories
MODEL_TO_CATEGORY = {
    # j-hartmann model outputs
    'joy': 'pure_joy',
    'sadness': 'cathartic_sadness',
    'anger': 'righteous_anger',
    'fear': 'controlled_fear',
    'surprise': 'mind_blown',
    'disgust': 'controlled_fear',  # Map to similar
    'neutral': None,  # Skip neutral
    
    # Alternative model outputs
    'love': 'romantic_warmth',
    'excitement': 'thrilling_tension',
    'admiration': 'triumphant_inspired',
    'amusement': 'pure_joy',
    'gratitude': 'bittersweet_hope',
    'optimism': 'bittersweet_hope',
    'relief': 'cozy_comfort',
    'pride': 'triumphant_inspired',
    'curiosity': 'intellectual_stimulation',
    'confusion': 'mind_blown',
    'nervousness': 'thrilling_tension',
    'remorse': 'cathartic_sadness',
    'grief': 'cathartic_sadness',
    'disappointment': 'cathartic_sadness',
    'embarrassment': 'cathartic_sadness',
    'realization': 'mind_blown',
    'approval': 'cozy_comfort',
    'caring': 'romantic_warmth',
    'desire': 'romantic_warmth',
    'annoyance': 'righteous_anger',
    'disapproval': 'righteous_anger',
}


def map_to_categories(emotions: Dict[str, float]) -> Dict[str, float]:
    """
    Map model emotion outputs to our emotion categories.
    
    Args:
        emotions: Raw emotion scores from model
        
    Returns:
        Mapped emotion scores in our categories
    """
    category_scores = {}
    
    for emotion, score in emotions.items():
        category = MODEL_TO_CATEGORY.get(emotion.lower())
        
        if category:
            if category in category_scores:
                category_scores[category] = max(category_scores[category], score)
            else:
                category_scores[category] = score
    
    return category_scores


if __name__ == "__main__":
    # Test the classifier
    test_texts = [
        "A heartwarming story about family and love that will make you cry tears of joy.",
        "A terrifying horror film that will keep you on the edge of your seat.",
        "A mind-bending thriller with shocking twists that will blow your mind.",
        "A feel-good comedy that will have you laughing from start to finish."
    ]
    
    print("Testing Emotion Classifier")
    print("=" * 50)
    
    for text in test_texts:
        print(f"\nText: {text[:60]}...")
        emotions = classify_text(text)
        print(f"Raw emotions: {emotions}")
        
        categories = map_to_categories(emotions)
        print(f"Mapped categories: {categories}")
