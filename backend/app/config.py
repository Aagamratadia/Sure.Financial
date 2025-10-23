"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Credit Card Statement Parser API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "credit_card_parser"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_MIME_TYPES: list = ["application/pdf"]
    TEMP_DIR: str = "/tmp/pdf_parser"
    
    # OCR Settings
    TESSERACT_DPI: int = 300
    TESSERACT_LANG: str = "eng"
    TESSERACT_CONFIG: str = "--psm 6"
    
    # Processing Settings
    MIN_TEXT_THRESHOLD: int = 100  # Minimum characters to consider text-based PDF
    DEFAULT_CURRENCY: str = "INR"
    
    # Confidence Thresholds
    MIN_CONFIDENCE_SCORE: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
