"""
Document Processing Service

Handles extraction of text from various file formats:
- PDF (.pdf)
- Text files (.txt)
- Word documents (.docx) - future

Uses Vietnamese NLP for text cleaning and normalization.
"""

from pathlib import Path
from typing import Optional
import io

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF processing disabled.")

# Vietnamese processing
try:
    from vietnamese_processor import VietnameseProcessor
    VN_PROCESSOR_AVAILABLE = True
except:
    try:
        from backend.app.services.vietnamese_processor import VietnameseProcessor
        VN_PROCESSOR_AVAILABLE = True
    except:
        VN_PROCESSOR_AVAILABLE = False
        VietnameseProcessor = None


class DocumentProcessor:
    """Process and extract text from various document formats"""
    
    def __init__(self):
        """Initialize document processor with Vietnamese NLP"""
        if VN_PROCESSOR_AVAILABLE and VietnameseProcessor:
            try:
                self.vn_processor = VietnameseProcessor()
            except:
                self.vn_processor = None
        else:
            self.vn_processor = None
    
    def extract_text_from_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        clean: bool = True
    ) -> str:
        """
        Extract text from file bytes.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename (for format detection)
            clean: Apply Vietnamese text cleaning
        
        Returns:
            Extracted and cleaned text
        """
        # Detect file type from extension
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            text = self._extract_from_pdf(file_bytes)
        elif file_ext in ['.txt', '.text']:
            text = self._extract_from_text(file_bytes)
        elif file_ext == '.docx':
            text = self._extract_from_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Clean and normalize Vietnamese text
        if clean and self.vn_processor:
            text = self.vn_processor.process(text)
        
        return text
    
    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_bytes: PDF file content
        
        Returns:
            Extracted text from all pages
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PyPDF2 not installed. Cannot process PDF files.")
        
        try:
            # Create PDF reader from bytes
            pdf_file = io.BytesIO(file_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_parts = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)
            
            # Combine all pages
            full_text = '\n\n'.join(text_parts)
            
            if not full_text.strip():
                raise ValueError("PDF contains no extractable text (might be image-based)")
            
            return full_text
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_from_text(self, file_bytes: bytes) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_bytes: Text file content
        
        Returns:
            Decoded text
        """
        try:
            # Try UTF-8 first
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                return file_bytes.decode('latin-1')
            except:
                raise ValueError("Unable to decode text file. Please ensure UTF-8 encoding.")
    
    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """
        Extract text from Word document.
        
        Args:
            file_bytes: DOCX file content
        
        Returns:
            Extracted text
        """
        raise NotImplementedError("DOCX extraction not yet implemented. Use PDF or TXT instead.")
    
    @property
    def supported_formats(self) -> list:
        """List of supported file formats"""
        formats = ['.txt', '.text']
        if PDF_AVAILABLE:
            formats.append('.pdf')
        return formats


# Test
if __name__ == "__main__":
    processor = DocumentProcessor()
    print(f"Supported formats: {processor.supported_formats}")
    print(f"Vietnamese processor: {'Available' if processor.vn_processor else 'Not available'}")
