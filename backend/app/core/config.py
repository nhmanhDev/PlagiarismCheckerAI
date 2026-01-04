"""
Configuration Module for Plagiarism Checker

Centralized settings for the application.
"""

import os
from pathlib import Path

class Settings:
    """Application settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    CORPUS_STORAGE_DIR = DATA_DIR / "corpora"
    
    # File upload settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    UPLOAD_TEMP_DIR = DATA_DIR / "temp"
    
    # Corpus settings
    MAX_CORPUS_SIZE = 10000  # Maximum segments per corpus
    DEFAULT_SPLIT_MODE = "auto"
    
    # Model settings
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    PHOBERT_MODEL = "vinai/phobert-base"  # Optional Vietnamese-specific model
    USE_PHOBERT = False  # Set to True to use PhoBERT for Vietnamese
    
    # Hybrid retrieval defaults
    DEFAULT_ALPHA = 0.4
    DEFAULT_TOP_K_LEX = 10
    DEFAULT_TOP_K_SEM = 10
    DEFAULT_TOP_N = 5
    DEFAULT_THRESHOLD = 0.75
    
    # API settings
    RATE_LIMIT_PER_MINUTE = 10
    
    # UI settings
    RESULTS_PER_PAGE = 10
    APP_TITLE = "PlagiarismChecker AI"
    APP_DESCRIPTION = "Advanced Plagiarism Detection with Vietnamese NLP Support"
    
    # Feature flags
    ENABLE_HISTORY = True
    ENABLE_EXPORT = True
    ENABLE_OCR = False  # Requires pytesseract
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CORPUS_STORAGE_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_TEMP_DIR.mkdir(exist_ok=True)


# Create singleton instance
settings = Settings()
settings.ensure_directories()
