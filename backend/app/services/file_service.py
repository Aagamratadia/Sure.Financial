"""File management service"""
import tempfile
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)


class FileService:
    """Manages temporary file storage"""
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Temp directory: {self.temp_dir}")
    
    async def save_upload(self, file: UploadFile) -> str:
        """
        Save uploaded file temporarily
        
        Args:
            file: Uploaded file
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = self.temp_dir / f"{file_id}.pdf"
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved file: {file_path} ({len(content)} bytes)")
        
        return str(file_path)
    
    def cleanup(self, file_path: str) -> None:
        """
        Delete temporary file
        
        Args:
            file_path: Path to file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted temp file: {file_path}")
        except OSError as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Delete files older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files deleted
        """
        now = time.time()
        deleted_count = 0
        
        for file_path in self.temp_dir.glob("*.pdf"):
            if now - file_path.stat().st_mtime > max_age_hours * 3600:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.debug(f"Cleaned up old file: {file_path}")
                except OSError as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old temporary files")
        
        return deleted_count
