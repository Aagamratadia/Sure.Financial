"""Pydantic schemas for data validation"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.enums import CardIssuer, JobStatus, ParserType


class DateField(BaseModel):
    """Date field with raw and formatted values"""
    raw: str = Field(description="Original date string from PDF")
    formatted: Optional[str] = Field(default=None, description="ISO 8601 formatted date (YYYY-MM-DD)")


class DateRangeField(BaseModel):
    """Date range for statement period"""
    raw: str = Field(description="Original date range string from PDF")
    start_date: Optional[str] = Field(default=None, description="Start date in ISO 8601 format")
    end_date: Optional[str] = Field(default=None, description="End date in ISO 8601 format")


class AmountField(BaseModel):
    """Currency amount field"""
    raw: str = Field(description="Original amount string from PDF")
    amount: float = Field(description="Parsed amount as float")
    currency: str = Field(default="INR", description="Currency code")


class ConfidenceScores(BaseModel):
    """Confidence scores for each extracted field"""
    card_issuer: float = Field(ge=0.0, le=1.0, description="Confidence score for card issuer")
    card_number: float = Field(ge=0.0, le=1.0, description="Confidence score for card number")
    statement_period: float = Field(ge=0.0, le=1.0, description="Confidence score for statement period")
    payment_due_date: float = Field(ge=0.0, le=1.0, description="Confidence score for payment due date")
    total_amount_due: float = Field(ge=0.0, le=1.0, description="Confidence score for total amount due")
    
    @property
    def average(self) -> float:
        """Calculate average confidence score"""
        scores = [
            self.card_issuer,
            self.card_number,
            self.statement_period,
            self.payment_due_date,
            self.total_amount_due
        ]
        return sum(scores) / len(scores)


class ParsedData(BaseModel):
    """Extracted data from credit card statement"""
    card_issuer: str = Field(description="Name of the card issuing bank")
    card_number: str = Field(description="Masked credit card number")
    statement_period: DateRangeField = Field(description="Statement billing cycle dates")
    payment_due_date: DateField = Field(description="Payment deadline")
    total_amount_due: AmountField = Field(description="Total outstanding balance")
    # Optional enhanced fields
    minimum_amount_due: Optional[AmountField] = Field(default=None, description="Minimum amount due")
    previous_balance: Optional[AmountField] = Field(default=None, description="Previous statement balance")
    available_credit_limit: Optional[AmountField] = Field(default=None, description="Available credit limit")
    reward_points_summary: Optional[str] = Field(default=None, description="Reward points summary text or total")
    transactions: Optional[list[dict]] = Field(default=None, description="List of transactions with date, merchant, amount")


class Metadata(BaseModel):
    """Processing metadata"""
    pages: int = Field(description="Number of pages in PDF")
    processing_time_ms: int = Field(description="Processing time in milliseconds")
    parser_used: ParserType = Field(description="PDF parser used")
    ocr_required: bool = Field(default=False, description="Whether OCR was required")
    file_size_bytes: int = Field(description="Size of uploaded file")


class ParseResult(BaseModel):
    """Complete parsing result"""
    job_id: str = Field(description="Unique job identifier")
    status: JobStatus = Field(description="Job status")
    filename: str = Field(description="Original filename")
    issuer: CardIssuer = Field(description="Detected card issuer")
    data: ParsedData = Field(description="Extracted data")
    confidence_scores: ConfidenceScores = Field(description="Confidence scores")
    metadata: Metadata = Field(description="Processing metadata")
    processed_at: datetime = Field(description="Processing completion timestamp")
    
    @field_validator('confidence_scores')
    @classmethod
    def check_confidence(cls, v):
        """Validate minimum confidence threshold"""
        if v.average < 0.3:  # Warning threshold, not blocking
            pass  # Could log warning here
        return v


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: JobStatus
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        arbitrary_types_allowed = True


class UploadResponse(BaseModel):
    """File upload response"""
    job_id: str
    status: JobStatus
    message: str
    estimated_time_seconds: Optional[int] = None
    created_at: datetime


class BatchUploadResponse(BaseModel):
    """Batch upload response"""
    batch_id: str
    total_files: int
    job_ids: list[str]
    status: JobStatus
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response"""
    error: Dict[str, Any]
    timestamp: datetime
