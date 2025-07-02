from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger

from app.db.session import get_db
from app.db.schemas.form_submission import FormSubmission
from app.db.crud.form_submission import get_places, get_form_submissions
from app.services.submission_workflow import SubmissionWorkflow

router = APIRouter()


@router.post("/start-processing")
async def start_processing(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start processing all places for form submission.
    Returns place info and starts background processing.
    """
    try:
        # Get all places from database
        places = await get_places(db)
        
        if not places:
            raise HTTPException(status_code=404, detail="No places found in database")
        
        # Start background workflow
        workflow = SubmissionWorkflow()
        background_tasks.add_task(workflow.process_all_submissions, db)
        
        # Return place information
        place_info = [
            {
                "place_id": place.id,
                "website_url": place.website or "",  # Use actual DB column name
                "message": "Processing started"
            }
            for place in places
        ]
        
        logger.info(f"Started processing {len(places)} places")
        
        return {
            "message": "Form submission processing started for all places",
            "total_places": len(places),
            "places": place_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting form submission process: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results")
async def get_results(db: AsyncSession = Depends(get_db)):
    """
    Get all form submission results from the database.
    Returns place_id, website_url, submission_status, submitted_at.
    """
    try:
        # Get all form submissions
        submissions = await get_form_submissions(db, skip=0, limit=1000)
        
        # Format results
        results = [
            {
                "place_id": submission.place_id,
                "website_url": submission.website_url,
                "submission_status": submission.submission_status,
                "submitted_at": submission.submitted_at,
                "error_message": submission.error_message if submission.error_message else None
            }
            for submission in submissions
        ]
        
        return {
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error getting form submission results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 