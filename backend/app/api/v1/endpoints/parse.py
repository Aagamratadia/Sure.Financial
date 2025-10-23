"""Parsing endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from app.models.schemas import (
    ParseResult, JobStatusResponse, UploadResponse,
    BatchUploadResponse
)
from app.models.enums import JobStatus
from app.services.validation import FileValidator
from app.services.file_service import FileService
from app.core.orchestrator import ParserOrchestrator
from app.db.database import get_database
from app.db.repository import JobRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
file_validator = FileValidator()
file_service = FileService()
orchestrator = ParserOrchestrator()


@router.post("/upload", response_model=ParseResult, status_code=200)
async def upload_statement(
    file: UploadFile = File(...),
    use_ocr: bool = True,
    db=Depends(get_database)
):
    """
    Upload a credit card statement PDF for parsing
    
    Args:
        file: PDF file to parse
        use_ocr: Force OCR processing (default: True for better accuracy)
        
    Returns:
        ParseResult with extracted data
    """
    # Validate file
    await file_validator.validate_upload(file)
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create repository
    repo = JobRepository(db)
    
    # Save file temporarily
    file_path = None
    
    try:
        # Create job record
        await repo.create_job(job_id, file.filename)
        await repo.update_job_status(
            job_id, JobStatus.PROCESSING, progress=10, message="File uploaded, starting parsing"
        )
        
        # Save file
        file_path = await file_service.save_upload(file)
        logger.info(f"Processing job {job_id}: {file.filename}")
        
        await repo.update_job_status(
            job_id, JobStatus.PROCESSING, progress=30, message="Extracting text from PDF"
        )
        
        # Parse PDF
        result = await orchestrator.parse(file_path, file.filename, job_id, use_ocr)
        
        await repo.update_job_status(
            job_id, JobStatus.PROCESSING, progress=90, message="Finalizing results"
        )
        
        # Save results
        await repo.save_result(result)
        await repo.update_job_status(
            job_id, JobStatus.COMPLETED, progress=100, message="Parsing completed successfully"
        )
        
        logger.info(f"Job {job_id} completed successfully")
        return result
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        await repo.update_job_status(
            job_id, JobStatus.FAILED, error=str(e), message="Parsing failed"
        )
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temporary file
        if file_path:
            file_service.cleanup(file_path)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db=Depends(get_database)):
    """
    Check parsing job status
    
    Args:
        job_id: Job identifier
        
    Returns:
        JobStatusResponse with current status and result if completed
    """
    repo = JobRepository(db)
    status = await repo.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If job is completed, include the result in simplified format
    if status.status == JobStatus.COMPLETED:
        result = await repo.get_result(job_id)
        if result:
            # Convert to simplified format for frontend
            simplified_result = {
                "job_id": result.job_id,
                "status": result.status.value,
                "card_issuer": result.data.card_issuer,
                "parser_used": result.metadata.parser_used.value,
                "card_number": {
                    "value": result.data.card_number,
                    "confidence": result.confidence_scores.card_number,
                    "raw_text": result.data.card_number
                },
                "statement_date": {
                    # Use end_date if start_date is empty (for single-date statements like Capital One)
                    "value": result.data.statement_period.start_date or result.data.statement_period.end_date,
                    "confidence": result.confidence_scores.statement_period,
                    "raw_text": result.data.statement_period.raw
                },
                "billing_period": {
                    "start_date": result.data.statement_period.start_date,
                    "end_date": result.data.statement_period.end_date,
                    "confidence": result.confidence_scores.statement_period,
                    "raw_text": result.data.statement_period.raw
                },
                "total_amount_due": {
                    "value": f"{result.data.total_amount_due.currency} {result.data.total_amount_due.amount}",
                    "confidence": result.confidence_scores.total_amount_due,
                    "raw_text": result.data.total_amount_due.raw,
                    "currency": result.data.total_amount_due.currency
                },
                "payment_due_date": {
                    "value": result.data.payment_due_date.formatted,
                    "confidence": result.confidence_scores.payment_due_date,
                    "raw_text": result.data.payment_due_date.raw
                },
                "confidence_scores": {
                    "overall": result.confidence_scores.average,
                    "card_number": result.confidence_scores.card_number,
                    "statement_date": result.confidence_scores.statement_period,
                    "billing_period": result.confidence_scores.statement_period,
                    "total_amount_due": result.confidence_scores.total_amount_due,
                    "payment_due_date": result.confidence_scores.payment_due_date
                },
                "processing_time": result.metadata.processing_time_ms
            }
            # Store as dict - Pydantic will handle it
            status.result = simplified_result
    
    return status


@router.get("/results/{job_id}", response_model=ParseResult)
async def get_results(job_id: str, db=Depends(get_database)):
    """
    Get parsing results
    
    Args:
        job_id: Job identifier
        
    Returns:
        ParseResult with extracted data
    """
    repo = JobRepository(db)
    result = await repo.get_result(job_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return result


@router.post("/batch", response_model=BatchUploadResponse)
async def batch_upload(
    files: List[UploadFile] = File(...),
    use_ocr: bool = False,
    db=Depends(get_database)
):
    """
    Upload multiple statements for batch processing
    
    Args:
        files: List of PDF files
        use_ocr: Force OCR processing
        
    Returns:
        BatchUploadResponse with job IDs
    """
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
    
    batch_id = str(uuid.uuid4())
    job_ids = []
    repo = JobRepository(db)
    
    # Create jobs for each file
    for file in files:
        # Validate
        await file_validator.validate_upload(file)
        
        # Create job
        job_id = str(uuid.uuid4())
        await repo.create_job(job_id, file.filename)
        job_ids.append(job_id)
    
    logger.info(f"Created batch {batch_id} with {len(job_ids)} jobs")
    
    # Note: In production, you would queue these jobs for background processing
    # For now, we just create the job records
    
    return BatchUploadResponse(
        batch_id=batch_id,
        total_files=len(files),
        job_ids=job_ids,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow()
    )
