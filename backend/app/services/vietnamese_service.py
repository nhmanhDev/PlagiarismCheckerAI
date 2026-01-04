"""
Vietnamese Text Processor Module

This module provides comprehensive Vietnamese text processing capabilities:
- Text normalization (lowercase, unicode normalization)
- Vietnamese word segmentation using underthesea
- Tone mark removal (optional)
- Vietnamese stop words removal
- Special character cleaning while preserving Vietnamese diacritics

Based on research: "Vietnamese Sentence Paraphrase Identification Using Sentence-BERT and PhoBERT" (2024)
"""

import re
import unicodedata
from typing import List, Set

try:
    from underthesea import word_tokenize
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    UNDERTHESEA_AVAILABLE = False
    word_tokenize = None


# Vietnamese stop words - common words that don't carry much meaning
VIETNAMESE_STOPWORDS: Set[str] = {
    # Articles and determiners
    "các", "một", "những", "cái", "chiếc", "con",
    
    # Pronouns
    "tôi", "tui", "mình", "bạn", "anh", "chị", "em", "ông", "bà",
    "nó", "họ", "chúng", "ta", "chúng_ta", "chúng_tôi",
    
    # Prepositions
    "của", "cho", "với", "từ", "tại", "trong", "ngoài", "trên", "dưới",
    "về", "đến", "đi", "vào", "ra", "lên", "xuống", "qua", "bên",
    
    # Conjunctions
    "và", "hoặc", "nhưng", "mà", "hay", "với", "cùng", "nên", "thì",
    
    # Common verbs
    "là", "có", "được", "bị", "làm", "đang", "sẽ", "đã",
    
    # Adverbs
    "rất", "lắm", "quá", "cũng", "đều", "chỉ", "vẫn", "còn", "đã",
    "sẽ", "đang", "đang_là", "đã_là",
    
    # Question words
    "gì", "ai", "đâu", "sao", "thế_nào", "như_thế_nào", "bao_giờ",
    
    # Others
    "này", "đó", "kia", "nào", "nữa", "thêm", "cả", "không", "chẳng",
    "chưa", "đã", "rồi", "mới", "vừa", "vẫn"
}


def normalize_unicode(text: str) -> str:
    """
    Normalize Vietnamese unicode variants.
    Ensures consistent representation of Vietnamese characters.
    """
    # NFD = decomposed form, NFC = composed form (standard)
    return unicodedata.normalize('NFC', text)


def remove_tone_marks(text: str) -> str:
    """
    Remove Vietnamese tone marks to get base characters.
    Useful for fuzzy matching.
    
    Example: 
        "Tiếng Việt" -> "Tieng Viet"
    """
    tone_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd',
        # Uppercase
        'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        'Đ': 'D',
    }
    
    result = []
    for char in text:
        result.append(tone_map.get(char, char))
    return ''.join(result)


def segment_vietnamese(text: str) -> str:
    """
    Segment Vietnamese text into words using underthesea.
    Vietnamese is a syllable-based language, proper segmentation is crucial.
    
    Example:
        "học máy học" -> "học_máy học" (machine learning vs learning)
    """
    if not UNDERTHESEA_AVAILABLE:
        # Fallback: just return the text as-is
        return text
    
    try:
        # underthesea returns a list of words
        words = word_tokenize(text, format="text")
        return words
    except Exception as e:
        # If segmentation fails, return original text
        print(f"Warning: Vietnamese segmentation failed: {e}")
        return text


def remove_stopwords(text: str, custom_stopwords: Set[str] = None) -> str:
    """
    Remove Vietnamese stop words from text.
    Text should be word-segmented first for best results.
    """
    stopwords = VIETNAMESE_STOPWORDS
    if custom_stopwords:
        stopwords = stopwords.union(custom_stopwords)
    
    words = text.split()
    filtered_words = [w for w in words if w.lower() not in stopwords]
    return ' '.join(filtered_words)


def clean_vietnamese_text(text: str, keep_punctuation: bool = True) -> str:
    """
    Clean text while preserving Vietnamese characters.
    
    Args:
        text: Input text
        keep_punctuation: If True, keep basic punctuation marks
    """
    # Normalize unicode first
    text = normalize_unicode(text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', ' ', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # Remove special characters but keep Vietnamese, alphanumeric, and basic punctuation
    if keep_punctuation:
        # Keep: letters (including Vietnamese), numbers, basic punctuation, whitespace
        text = re.sub(
            r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
            r'ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ'
            r'0-9\s\.,;:!?()\'"_-]',
            ' ',
            text
        )
    else:
        # Only keep letters and numbers
        text = re.sub(
            r'[^a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
            r'ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ'
            r'0-9\s_]',
            ' ',
            text
        )
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def preprocess_vietnamese_text(
    text: str,
    lowercase: bool = True,
    remove_tones: bool = False,
    segment: bool = True,
    remove_stops: bool = False,
    clean: bool = True,
    custom_stopwords: Set[str] = None
) -> str:
    """
    Comprehensive Vietnamese text preprocessing pipeline.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_tones: Remove Vietnamese tone marks (for fuzzy matching)
        segment: Apply word segmentation (recommended)
        remove_stops: Remove stop words
        clean: Clean special characters
        custom_stopwords: Additional stop words to remove
    
    Returns:
        Preprocessed text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Step 1: Normalize unicode
    text = normalize_unicode(text)
    
    # Step 2: Clean text
    if clean:
        text = clean_vietnamese_text(text, keep_punctuation=True)
    
    # Step 3: Lowercase
    if lowercase:
        text = text.lower()
    
    # Step 4: Remove tones (optional, for fuzzy matching)
    if remove_tones:
        text = remove_tone_marks(text)
    
    # Step 5: Word segmentation (important for Vietnamese!)
    if segment and UNDERTHESEA_AVAILABLE:
        text = segment_vietnamese(text)
    
    # Step 6: Remove stop words
    if remove_stops:
        text = remove_stopwords(text, custom_stopwords)
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def is_vietnamese_text(text: str, threshold: float = 0.3) -> bool:
    """
    Detect if text is likely Vietnamese based on character frequency.
    
    Args:
        text: Input text
        threshold: Minimum ratio of Vietnamese characters to consider as Vietnamese
    
    Returns:
        True if text appears to be Vietnamese
    """
    if not text:
        return False
    
    # Vietnamese specific characters
    vietnamese_chars = set('àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
                          'ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ')
    
    # Count Vietnamese chars
    vn_count = sum(1 for c in text if c in vietnamese_chars)
    total_letters = sum(1 for c in text if c.isalpha())
    
    if total_letters == 0:
        return False
    
    ratio = vn_count / total_letters
    return ratio >= threshold


# Convenience function for backward compatibility
def normalize_text(text: str) -> str:
    """
    Simple normalization for general use.
    Equivalent to preprocess_vietnamese_text with default settings.
    """
    return preprocess_vietnamese_text(
        text,
        lowercase=True,
        remove_tones=False,
        segment=True,
        remove_stops=False,
        clean=True
    )


if __name__ == "__main__":
    # Test the processor
    print("=== Vietnamese Text Processor Test ===\n")
    
    test_text = "Học máy là một nhánh của trí tuệ nhân tạo, tập trung vào việc cho phép máy tính học từ dữ liệu."
    
    print(f"Original: {test_text}\n")
    
    print(f"Cleaned: {clean_vietnamese_text(test_text)}\n")
    
    if UNDERTHESEA_AVAILABLE:
        print(f"Segmented: {segment_vietnamese(test_text)}\n")
    else:
        print("Warning: underthesea not available for segmentation\n")
    
    print(f"Without tones: {remove_tone_marks(test_text.lower())}\n")
    
    print(f"Preprocessed (full): {preprocess_vietnamese_text(test_text)}\n")
    
    print(f"Is Vietnamese? {is_vietnamese_text(test_text)}")
    print(f"Is English Vietnamese? {is_vietnamese_text('Machine learning is a branch of AI')}")
