"""
Vietnamese Processor Wrapper for Service

Simple wrapper around Vietnamese text processing functions
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from vietnamese_service import (
        preprocess_vietnamese_text,
        is_vietnamese_text,
        normalize_text
    )
    VN_AVAILABLE = True
except ImportError:
    VN_AVAILABLE = False
    preprocess_vietnamese_text = None
    is_vietnamese_text = None
    normalize_text = None


class VietnameseProcessor:
    """Simple Vietnamese text processor"""
    
    def __init__(self):
        self.available = VN_AVAILABLE
    
    def process(self, text: str) -> str:
        """Process Vietnamese text"""
        if not self.available or not text:
            return text.lower().strip()
        
        return normalize_text(text)
    
    def is_vietnamese(self, text: str) -> bool:
        """Check if text is Vietnamese"""
        if not self.available:
            # Simple heuristic: check for Vietnamese characters
            vn_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
            return any(c in text.lower() for c in vn_chars)
        
        return is_vietnamese_text(text)
