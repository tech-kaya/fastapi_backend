from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger
from pydantic import BaseModel

from app.db.session import get_db
from app.db.schemas.form_submission import FormSubmission
from app.db.crud.form_submission import get_places, get_form_submissions, get_user_by_email, get_form_submissions_by_user_email, get_places_by_ids, get_places_by_place_ids
from app.services.submission_workflow import SubmissionWorkflow

router = APIRouter()


class ProcessingRequest(BaseModel):
    email: str
    place_ids: List[str]


@router.post("/start-processing")
async def start_processing(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start processing selective places for form submission using the specified user email.
    Returns place info and starts background processing.
    """
    try:
        # Validate user email exists in database
        user = await get_user_by_email(db, request.email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email '{request.email}' not found in database")
        
        # Validate place_ids are provided
        if not request.place_ids:
            raise HTTPException(status_code=400, detail="place_ids array cannot be empty")
        
        # Get requested places from database
        places = await get_places_by_place_ids(db, request.place_ids)
        
        if not places:
            raise HTTPException(status_code=404, detail="No places found for the provided place_ids")
        
        # Check for missing place IDs
        found_place_ids = {place.place_id for place in places}
        missing_place_ids = [pid for pid in request.place_ids if pid not in found_place_ids]
        
        # Start background workflow with specific user and places
        workflow = SubmissionWorkflow()
        background_tasks.add_task(workflow.process_selective_submissions_by_place_id, db, user, request.place_ids)
        
        # Return place information
        place_info = [
            {
                "place_id": place.place_id,
                "place_name": place.name,
                "website_url": place.website or "",
                "message": "Processing started"
            }
            for place in places
        ]
        
        logger.info(f"Started processing {len(places)} places for user: {user.first_name} ({user.email})")
        
        response = {
            "message": f"Form submission processing started for {len(places)} places using user: {user.first_name} ({user.email})",
            "total_places": len(places),
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "places": place_info
        }
        
        if missing_place_ids:
            response["warning"] = f"Place IDs not found in database: {missing_place_ids}"
            response["missing_place_ids"] = missing_place_ids
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting form submission process: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results")
async def get_results(email: str, db: AsyncSession = Depends(get_db)):
    """
    Get form submission results for the specified user email from the database.
    Returns place_id, website_url, submission_status, submitted_at filtered by user email.
    """
    try:
        # Validate user email exists in database
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email '{email}' not found in database")
        
        # Get form submissions for the specific user
        submissions = await get_form_submissions_by_user_email(db, email, skip=0, limit=1000)
        
        # Format results
        results = [
            {
                "submission_id": submission.id,
                "place_id": submission.place_id,
                "place_name": submission.place.name if submission.place else None,
                "website_url": submission.website_url,
                "submission_status": submission.submission_status,
                "submitted_at": submission.submitted_at,
                "error_message": submission.error_message if submission.error_message else None
            }
            for submission in submissions
        ]
        
        return {
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "total_results": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting form submission results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 