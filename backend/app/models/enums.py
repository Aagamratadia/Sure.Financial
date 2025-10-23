"""Enumerations"""
from enum import Enum


class CardIssuer(str, Enum):
    """Credit card issuers"""
    KOTAK = "Kotak Mahindra Bank"
    HDFC = "HDFC Bank"
    ICICI = "ICICI Bank"
    IDFC = "IDFC First Bank"
    AXIS = "Axis Bank"
    AMEX = "American Express Banking Corp"
    CAPITAL_ONE = "Capital One Europe Plc"
    UNKNOWN = "Unknown"


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ParserType(str, Enum):
    """PDF parser types"""
    PYMUPDF = "pymupdf"
    PDFPLUMBER = "pdfplumber"
    TESSERACT = "tesseract"
