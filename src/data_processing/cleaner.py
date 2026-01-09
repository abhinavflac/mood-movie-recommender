"""
Data Cleaner
============
Text cleaning and data validation utilities.
"""

import re
import html
from typing import Optional, Dict, Any
from loguru import logger


class TextCleaner:
    """
    Clean and normalize text data for emotion analysis.
    
    Methods handle various text preprocessing tasks needed
    before running NLP models on reviews.
    """
    
    # Patterns to remove
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    URL_PATTERN = re.compile(r'http[s]?://\S+|www\.\S+')
    EMAIL_PATTERN = re.compile(r'\S+@\S+\.\S+')
    MULTIPLE_SPACES = re.compile(r'\s+')
    MULTIPLE_NEWLINES = re.compile(r'\n{3,}')
    
    # Spoiler indicators
    SPOILER_PATTERNS = [
        re.compile(r'\*{2,}spoiler\*{2,}', re.IGNORECASE),
        re.compile(r'\[spoiler\]', re.IGNORECASE),
        re.compile(r'SPOILER ALERT', re.IGNORECASE),
    ]
    
    @classmethod
    def clean_review_text(
        cls,
        text: str,
        min_length: int = 50,
        max_length: int = 10000
    ) -> Optional[str]:
        """
        Clean review text for emotion analysis.
        
        Args:
            text: Raw review text
            min_length: Minimum length after cleaning
            max_length: Maximum length (truncate if exceeded)
            
        Returns:
            Cleaned text or None if invalid
        """
        if not text or not isinstance(text, str):
            return None
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = cls.HTML_TAG_PATTERN.sub(' ', text)
        
        # Remove URLs
        text = cls.URL_PATTERN.sub(' ', text)
        
        # Remove email addresses
        text = cls.EMAIL_PATTERN.sub(' ', text)
        
        # Normalize whitespace
        text = cls.MULTIPLE_SPACES.sub(' ', text)
        text = cls.MULTIPLE_NEWLINES.sub('\n\n', text)
        
        # Strip whitespace
        text = text.strip()
        
        # Length checks
        if len(text) < min_length:
            return None
            
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @classmethod
    def clean_movie_title(cls, title: str) -> str:
        """
        Normalize movie title.
        
        Args:
            title: Raw movie title
            
        Returns:
            Cleaned title
        """
        if not title:
            return ""
        
        # Decode HTML entities
        title = html.unescape(title)
        
        # Remove year in parentheses at end (e.g., "Inception (2010)")
        title = re.sub(r'\s*\(\d{4}\)\s*$', '', title)
        
        # Remove extra whitespace
        title = cls.MULTIPLE_SPACES.sub(' ', title)
        
        return title.strip()
    
    @classmethod
    def has_spoiler(cls, text: str) -> bool:
        """
        Check if text contains spoiler indicators.
        
        Args:
            text: Text to check
            
        Returns:
            True if spoiler detected
        """
        if not text:
            return False
            
        for pattern in cls.SPOILER_PATTERNS:
            if pattern.search(text):
                return True
                
        return False
    
    @classmethod
    def extract_sentiment_phrases(cls, text: str) -> list:
        """
        Extract emotionally charged phrases from text.
        
        Useful for focusing emotion analysis on key sentences.
        
        Args:
            text: Full review text
            
        Returns:
            List of potentially emotional sentences
        """
        if not text:
            return []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        emotional_phrases = []
        
        # Keywords that indicate emotional content
        emotion_keywords = [
            'love', 'hate', 'amazing', 'terrible', 'beautiful',
            'boring', 'exciting', 'sad', 'happy', 'cry', 'laugh',
            'scared', 'frightened', 'moved', 'touched', 'stunning',
            'worst', 'best', 'incredible', 'disappointing', 'perfect',
            'masterpiece', 'waste', 'brilliant', 'awful'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            sentence_lower = sentence.lower()
            
            # Check for emotion keywords
            has_emotion = any(
                keyword in sentence_lower 
                for keyword in emotion_keywords
            )
            
            # Check for emphasis (all caps, multiple punctuation)
            has_emphasis = (
                sentence.isupper() or 
                '!!' in sentence or 
                '??' in sentence
            )
            
            if has_emotion or has_emphasis:
                emotional_phrases.append(sentence)
        
        return emotional_phrases


class DataValidator:
    """
    Validate data quality for movies and reviews.
    """
    
    # Required fields for valid records
    REQUIRED_MOVIE_FIELDS = ['tmdb_id', 'title']
    REQUIRED_REVIEW_FIELDS = ['content']
    
    @classmethod
    def validate_movie_record(cls, record: Dict[str, Any]) -> bool:
        """
        Check if movie record is valid.
        
        Args:
            record: Movie data dictionary
            
        Returns:
            True if valid
        """
        for field in cls.REQUIRED_MOVIE_FIELDS:
            if not record.get(field):
                return False
        
        return True
    
    @classmethod
    def validate_review_record(cls, record: Dict[str, Any]) -> bool:
        """
        Check if review record is valid.
        
        Args:
            record: Review data dictionary
            
        Returns:
            True if valid
        """
        for field in cls.REQUIRED_REVIEW_FIELDS:
            if not record.get(field):
                return False
        
        # Content length check
        content = record.get('content', '')
        if len(content) < 50:
            return False
        
        return True
    
    @classmethod
    def validate_rating(
        cls, 
        rating: Any, 
        min_val: float = 0, 
        max_val: float = 10
    ) -> Optional[float]:
        """
        Validate and normalize rating value.
        
        Args:
            rating: Raw rating value
            min_val: Minimum valid value
            max_val: Maximum valid value
            
        Returns:
            Normalized rating or None if invalid
        """
        if rating is None:
            return None
            
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            return None
        
        if rating < min_val or rating > max_val:
            return None
            
        return rating
    
    @classmethod
    def validate_date(cls, date_str: str) -> Optional[str]:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            ISO format date or None if invalid
        """
        if not date_str:
            return None
            
        # Common date formats to try
        from datetime import datetime
        
        formats = [
            '%Y-%m-%d',
            '%d %B %Y',
            '%B %d, %Y',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.date().isoformat()
            except ValueError:
                continue
                
        return None


# Utility functions
def clean_and_validate_movies(records: list) -> list:
    """
    Clean and validate a list of movie records.
    
    Args:
        records: List of movie dictionaries
        
    Returns:
        Cleaned and validated records
    """
    cleaner = TextCleaner()
    validator = DataValidator()
    
    valid_records = []
    
    for record in records:
        if not validator.validate_movie_record(record):
            continue
            
        # Clean text fields
        record['title'] = cleaner.clean_movie_title(record.get('title', ''))
        
        if record.get('overview'):
            record['overview'] = cleaner.clean_review_text(
                record['overview'],
                min_length=10
            )
        
        valid_records.append(record)
    
    logger.info(
        f"Validated movies: {len(records)} → {len(valid_records)}"
    )
    
    return valid_records


def clean_and_validate_reviews(records: list) -> list:
    """
    Clean and validate a list of review records.
    
    Args:
        records: List of review dictionaries
        
    Returns:
        Cleaned and validated records
    """
    cleaner = TextCleaner()
    validator = DataValidator()
    
    valid_records = []
    
    for record in records:
        # Clean content first
        cleaned_content = cleaner.clean_review_text(record.get('content', ''))
        
        if not cleaned_content:
            continue
            
        record['content'] = cleaned_content
        
        if not validator.validate_review_record(record):
            continue
        
        # Check for spoilers
        record['is_spoiler'] = cleaner.has_spoiler(cleaned_content)
        
        # Validate rating
        if record.get('rating'):
            record['rating'] = validator.validate_rating(record['rating'])
        
        valid_records.append(record)
    
    logger.info(
        f"Validated reviews: {len(records)} → {len(valid_records)}"
    )
    
    return valid_records


if __name__ == "__main__":
    # Test cleaning
    test_review = """
    <p>This movie was AMAZING!!! I absolutely loved it. 
    Check out more at http://example.com/review
    
    The acting was incredible and I cried at the end. ****SPOILER****
    The main character dies but it was so beautifully done.
    
    
    10/10 would watch again!!!
    </p>
    """
    
    cleaner = TextCleaner()
    cleaned = cleaner.clean_review_text(test_review)
    print("Original length:", len(test_review))
    print("Cleaned length:", len(cleaned))
    print("Cleaned text:", cleaned)
    print("Has spoiler:", cleaner.has_spoiler(test_review))
    print("Emotional phrases:", cleaner.extract_sentiment_phrases(cleaned))
