"""Tesseract OCR parser implementation"""
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageEnhance
from typing import Dict, Any
import os
import logging
from app.core.parsers.base import PDFParser
from app.config import settings

logger = logging.getLogger(__name__)


class TesseractOCRParser(PDFParser):
    """PDF parser using Tesseract OCR for image-based PDFs"""
    
    def __init__(self):
        self.dpi = settings.TESSERACT_DPI
        self.lang = settings.TESSERACT_LANG
        self.config = settings.TESSERACT_CONFIG
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text using Tesseract OCR
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Tesseract OCR: Converting PDF to images and performing OCR on {file_path}")
            
            # Convert PDF pages to images
            images = convert_from_path(
                file_path,
                dpi=self.dpi,
                fmt='png'
            )
            
            logger.info(f"Tesseract OCR: Converted to {len(images)} images")
            
            text_content = []
            
            for i, image in enumerate(images):
                # Preprocess image
                processed_image = self._preprocess_image(image)
                
                # Perform OCR
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=self.lang,
                    config=self.config
                )
                
                if text:
                    text_content.append(text)
                    logger.debug(f"Tesseract OCR: Extracted {len(text)} chars from page {i + 1}")
            
            full_text = "\n\n".join(text_content)
            cleaned_text = self.clean_text(full_text)
            
            logger.info(f"Tesseract OCR: Total extracted {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Tesseract OCR: Error performing OCR: {e}")
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
            # Convert first page to get page count
            images = convert_from_path(file_path, dpi=self.dpi)
            
            return {
                "pages": len(images),
                "file_size_bytes": os.path.getsize(file_path),
                "format": "PDF",
                "ocr_used": True,
                "dpi": self.dpi,
            }
            
        except Exception as e:
            logger.error(f"Tesseract OCR: Error extracting metadata: {e}")
            return {
                "pages": 0,
                "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "format": "PDF",
                "error": str(e)
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Processed image
        """
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(image)
        image = sharpness_enhancer.enhance(1.5)
        
        return image


def detect_if_ocr_needed(file_path: str, threshold: int = 100) -> bool:
    """
    Determine if PDF needs OCR by checking text content
    
    Args:
        file_path: Path to PDF file
        threshold: Minimum character threshold
        
    Returns:
        True if OCR is needed, False otherwise
    """
    try:
        import fitz
        doc = fitz.open(file_path)
        
        total_chars = 0
        for page in doc:
            text = page.get_text()
            total_chars += len(text.strip())
            
            # Early exit if we have enough text
            if total_chars >= threshold:
                doc.close()
                return False
        
        doc.close()
        
        # If very little text extracted, PDF is likely scanned
        logger.info(f"Detected {total_chars} characters, OCR needed: {total_chars < threshold}")
        return total_chars < threshold
        
    except Exception as e:
        logger.warning(f"Error detecting OCR need: {e}, assuming OCR needed")
        return True
