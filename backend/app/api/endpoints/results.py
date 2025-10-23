"""API endpoints for statement results"""
from fastapi import APIRouter, Body, HTTPException, Depends
from typing import Dict, Any, List
from app.db.database import MongoDB
from bson import ObjectId
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/save", response_model=Dict[str, Any])
async def save_result(data: Dict[str, Any] = Body(...)):
    """Save parsed statement result to database"""
    try:
        # Convert data to proper format for MongoDB
        result_data = {
            "card_number": data.get("card_number", {}).get("value"),
            "card_issuer": data.get("card_issuer"),
            "statement_date": data.get("statement_date", {}).get("value"),
            "due_date": data.get("due_date", {}).get("value"),
            "total_amount_due": data.get("total_amount_due", {}).get("value"),
            "overall_confidence": data.get("overall_confidence"),
            "parser_used": data.get("parser_used"),
            "raw_data": data,
            "created_at": datetime.utcnow()
        }
        
        # Insert into MongoDB (use 'results' collection for consistency with repository)
        result = await MongoDB.db.results.insert_one(result_data)
        
        # Return success response with ID
        return {
            "success": True,
            "message": "Result saved successfully",
            "result_id": str(result.inserted_id)
        }
    except Exception as e:
        logger.error(f"Error saving result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save result: {str(e)}")

@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
async def list_results(limit: int = 100):
    """List saved results from MongoDB, newest first"""
    try:
        # Read from 'results' collection (where existing data likely resides)
        cursor = MongoDB.db.results.find({}).sort([("_id", -1)])
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d["_id"] = str(d["_id"])  # convert ObjectId
            # Ensure created_at is ISO if present
            if "created_at" in d and isinstance(d["created_at"], datetime):
                d["created_at"] = d["created_at"].isoformat()
        return docs
    except Exception as e:
        logger.error(f"Error listing results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list results: {str(e)}")

@router.get("/{result_id}", response_model=Dict[str, Any])
async def get_result(result_id: str):
    """Get a saved result by ID"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(result_id):
            raise HTTPException(status_code=400, detail="Invalid result ID format")
        
        # Find result in database (use 'results' collection)
        result = await MongoDB.db.results.find_one({"_id": ObjectId(result_id)})
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Convert ObjectId to string for JSON serialization
        result["_id"] = str(result["_id"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {str(e)}")