"""pdfplumber parser implementation"""
import pdfplumber
from typing import Dict, Any
import os
import logging
from app.core.parsers.base import PDFParser

logger = logging.getLogger(__name__)


class PDFPlumberParser(PDFParser):
    """PDF parser using pdfplumber library"""
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text using pdfplumber
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"pdfplumber: Extracting text from {file_path}")
            
            with pdfplumber.open(file_path) as pdf:
                text_content = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        logger.debug(f"pdfplumber: Extracted {len(text)} chars from page {page_num + 1}")
                
                full_text = "\n\n".join(text_content)
                cleaned_text = self.clean_text(full_text)
                
                logger.info(f"pdfplumber: Total extracted {len(cleaned_text)} characters")
                return cleaned_text
                
        except Exception as e:
            logger.error(f"pdfplumber: Error extracting text: {e}")
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
            with pdfplumber.open(file_path) as pdf:
                metadata = {
                    "pages": len(pdf.pages),
                    "file_size_bytes": os.path.getsize(file_path),
                    "format": "PDF",
                }
                
                # Add PDF metadata if available
                if pdf.metadata:
                    metadata.update({
                        "producer": pdf.metadata.get("Producer", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                    })
                
                return metadata
                
        except Exception as e:
            logger.error(f"pdfplumber: Error extracting metadata: {e}")
            return {
                "pages": 0,
                "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "format": "PDF",
                "error": str(e)
            }
