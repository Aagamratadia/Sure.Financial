"""File validation service"""
from fastapi import UploadFile, HTTPException
import magic
import os
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded PDF files"""
    
    @staticmethod
    async def validate_upload(file: UploadFile) -> None:
        """
        Validate uploaded file
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        file_size = len(content)
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Check MIME type
        try:
            mime = magic.from_buffer(content, mime=True)
            if mime not in settings.ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Expected PDF, got {mime}"
                )
        except Exception as e:
            logger.warning(f"MIME type detection failed: {e}, assuming PDF")
        
        # Verify PDF structure
        try:
            import fitz
            # Try to open as PDF
            doc = fitz.open(stream=content, filetype="pdf")
            
            if len(doc) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="PDF has no pages"
                )
            
            doc.close()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or corrupted PDF file: {str(e)}"
            )
        
        logger.info(f"File validation passed: {file.filename}, size: {file_size} bytes")
