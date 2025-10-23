"""PyMuPDF (fitz) parser implementation"""
import fitz  # PyMuPDF
from typing import Dict, Any
import os
import logging
from app.core.parsers.base import PDFParser

logger = logging.getLogger(__name__)


class PyMuPDFParser(PDFParser):
    """PDF parser using PyMuPDF library"""
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text using PyMuPDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"PyMuPDF: Extracting text from {file_path}")
            
            doc = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_content.append(text)
                logger.debug(f"PyMuPDF: Extracted {len(text)} chars from page {page_num + 1}")
            
            doc.close()
            
            full_text = "\n\n".join(text_content)
            cleaned_text = self.clean_text(full_text)
            
            logger.info(f"PyMuPDF: Total extracted {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"PyMuPDF: Error extracting text: {e}")
            return ""
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Metadata dictionary
        """
        try:
            doc = fitz.open(file_path)
            
            metadata = {
                "pages": len(doc),
                "file_size_bytes": os.path.getsize(file_path),
                "format": "PDF",
                "encrypted": doc.is_encrypted,
                "producer": doc.metadata.get("producer", ""),
                "creator": doc.metadata.get("creator", ""),
            }
            
            doc.close()
            return metadata
            
        except Exception as e:
            logger.error(f"PyMuPDF: Error extracting metadata: {e}")
            return {
                "pages": 0,
                "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "format": "PDF",
                "error": str(e)
            }
