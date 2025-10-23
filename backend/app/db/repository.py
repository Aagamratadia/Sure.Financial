"""MongoDB repository for data access"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.schemas import ParseResult, JobStatusResponse
from app.models.enums import JobStatus
import logging

logger = logging.getLogger(__name__)


class JobRepository:
    """Repository for managing parsing jobs and results"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.jobs_collection = db["jobs"]
        self.results_collection = db["results"]
    
    async def create_job(self, job_id: str, filename: str) -> None:
        """Create a new parsing job"""
        job_doc = {
            "job_id": job_id,
            "filename": filename,
            "status": JobStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "progress_percentage": 0,
            "message": "Job created"
        }
        await self.jobs_collection.insert_one(job_doc)
        logger.info(f"Created job: {job_id}")
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Update job status"""
        update_doc = {
            "status": status.value,
            "updated_at": datetime.utcnow()
        }
        
        if progress is not None:
            update_doc["progress_percentage"] = progress
        
        if message:
            update_doc["message"] = message
        
        if error:
            update_doc["error_message"] = error
        
        if status == JobStatus.COMPLETED:
            update_doc["completed_at"] = datetime.utcnow()
        
        await self.jobs_collection.update_one(
            {"job_id": job_id},
            {"$set": update_doc}
        )
        logger.info(f"Updated job {job_id}: {status.value}")
    
    async def get_job_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """Get job status"""
        job = await self.jobs_collection.find_one({"job_id": job_id})
        
        if not job:
            return None
        
        return JobStatusResponse(
            job_id=job["job_id"],
            status=JobStatus(job["status"]),
            progress_percentage=job.get("progress_percentage"),
            message=job.get("message"),
            created_at=job["created_at"],
            updated_at=job["updated_at"]
        )
    
    async def save_result(self, result: ParseResult) -> None:
        """Save parsing result to MongoDB"""
        # Convert ParseResult to dict
        result_doc = {
            "job_id": result.job_id,
            "filename": result.filename,
            "issuer": result.issuer.value,
            "data": {
                "card_issuer": result.data.card_issuer,
                "card_number": result.data.card_number,
                "statement_period": {
                    "raw": result.data.statement_period.raw,
                    "start_date": result.data.statement_period.start_date,
                    "end_date": result.data.statement_period.end_date
                },
                "payment_due_date": {
                    "raw": result.data.payment_due_date.raw,
                    "formatted": result.data.payment_due_date.formatted
                },
                "total_amount_due": {
                    "raw": result.data.total_amount_due.raw,
                    "amount": result.data.total_amount_due.amount,
                    "currency": result.data.total_amount_due.currency
                }
            },
            "confidence_scores": {
                "card_issuer": result.confidence_scores.card_issuer,
                "card_number": result.confidence_scores.card_number,
                "statement_period": result.confidence_scores.statement_period,
                "payment_due_date": result.confidence_scores.payment_due_date,
                "total_amount_due": result.confidence_scores.total_amount_due,
                "average": result.confidence_scores.average
            },
            "metadata": {
                "pages": result.metadata.pages,
                "processing_time_ms": result.metadata.processing_time_ms,
                "parser_used": result.metadata.parser_used.value,
                "ocr_required": result.metadata.ocr_required,
                "file_size_bytes": result.metadata.file_size_bytes
            },
            "status": result.status.value,
            "processed_at": result.processed_at,
            "created_at": datetime.utcnow()
        }
        
        await self.results_collection.insert_one(result_doc)
        logger.info(f"Saved result for job: {result.job_id}")
    
    async def get_result(self, job_id: str) -> Optional[ParseResult]:
        """Get parsing result"""
        result_doc = await self.results_collection.find_one({"job_id": job_id})
        
        if not result_doc:
            return None
        
        # Convert MongoDB doc back to ParseResult
        from app.models.schemas import (
            ParsedData, DateRangeField, DateField, AmountField,
            ConfidenceScores, Metadata
        )
        from app.models.enums import CardIssuer, ParserType
        
        return ParseResult(
            job_id=result_doc["job_id"],
            status=JobStatus(result_doc["status"]),
            filename=result_doc["filename"],
            issuer=CardIssuer(result_doc["issuer"]),
            data=ParsedData(
                card_issuer=result_doc["data"]["card_issuer"],
                card_number=result_doc["data"]["card_number"],
                statement_period=DateRangeField(**result_doc["data"]["statement_period"]),
                payment_due_date=DateField(**result_doc["data"]["payment_due_date"]),
                total_amount_due=AmountField(**result_doc["data"]["total_amount_due"]),
                minimum_amount_due=AmountField(**result_doc["data"]["minimum_amount_due"]) if result_doc["data"].get("minimum_amount_due") else None,
                previous_balance=AmountField(**result_doc["data"]["previous_balance"]) if result_doc["data"].get("previous_balance") else None,
                available_credit_limit=AmountField(**result_doc["data"]["available_credit_limit"]) if result_doc["data"].get("available_credit_limit") else None,
                reward_points_summary=result_doc["data"].get("reward_points_summary"),
                transactions=result_doc["data"].get("transactions"),
            ),
            confidence_scores=ConfidenceScores(
                card_issuer=result_doc["confidence_scores"]["card_issuer"],
                card_number=result_doc["confidence_scores"]["card_number"],
                statement_period=result_doc["confidence_scores"]["statement_period"],
                payment_due_date=result_doc["confidence_scores"]["payment_due_date"],
                total_amount_due=result_doc["confidence_scores"]["total_amount_due"]
            ),
            metadata=Metadata(
                pages=result_doc["metadata"]["pages"],
                processing_time_ms=result_doc["metadata"]["processing_time_ms"],
                parser_used=ParserType(result_doc["metadata"]["parser_used"]),
                ocr_required=result_doc["metadata"]["ocr_required"],
                file_size_bytes=result_doc["metadata"]["file_size_bytes"]
            ),
            processed_at=result_doc["processed_at"]
        )
    
    async def create_indexes(self) -> None:
        """Create database indexes for better query performance"""
        # Index on job_id for fast lookups
        await self.jobs_collection.create_index("job_id", unique=True)
        await self.results_collection.create_index("job_id", unique=True)
        
        # Index on created_at for time-based queries
        await self.jobs_collection.create_index("created_at")
        await self.results_collection.create_index("created_at")
        
        # Index on status for filtering
        await self.jobs_collection.create_index("status")
        
        logger.info("Created MongoDB indexes")
