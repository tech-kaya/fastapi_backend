from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger

from app.db.session import get_db
from app.db.schemas.form_submission import FormSubmission
from app.db.crud.form_submission import get_places, get_form_submissions, get_user_by_email, get_form_submissions_by_user_email
from app.services.submission_workflow import SubmissionWorkflow

router = APIRouter()


@router.post("/start-processing")
async def start_processing(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start processing all places for form submission using the specified user email.
    Returns place info and starts background processing.
    """
    try:
        # Validate user email exists in database
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with email '{email}' not found in database")
        
        # Get all places from database
        places = await get_places(db)
        
        if not places:
            raise HTTPException(status_code=404, detail="No places found in database")
        
        # Start background workflow with specific user
        workflow = SubmissionWorkflow()
        background_tasks.add_task(workflow.process_all_submissions, db, user)
        
        # Return place information
        place_info = [
            {
                "place_id": place.id,
                "website_url": place.website or "",  # Use actual DB column name
                "message": "Processing started"
            }
            for place in places
        ]
        
        logger.info(f"Started processing {len(places)} places for user: {user.first_name} ({user.email})")
        
        return {
            "message": f"Form submission processing started for all places using user: {user.first_name} ({user.email})",
            "total_places": len(places),
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name or ''}".strip(),
            "places": place_info
        }
        
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