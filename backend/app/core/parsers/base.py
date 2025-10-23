"""Base parser interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFParser(ABC):
    """Abstract base class for PDF parsers"""
    
    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with metadata (pages, file_size, etc.)
        """
        pass
    
    def has_sufficient_text(self, text: str, threshold: int = 100) -> bool:
        """
        Check if extracted text is sufficient for parsing
        
        Args:
            text: Extracted text
            threshold: Minimum character count
            
        Returns:
            True if text length exceeds threshold
        """
        if not text:
            return False
        
        # Remove whitespace and count
        cleaned = text.strip()
        char_count = len(cleaned)
        
        logger.debug(f"Extracted {char_count} characters (threshold: {threshold})")
        return char_count >= threshold
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        # Remove empty lines
        lines = [line for line in lines if line]
        # Join with single newline
        return '\n'.join(lines)
