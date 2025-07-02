import asyncio
from typing import Dict, Any, List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.form_submitter import FormSubmitter
from app.core.config import settings
from app.db.crud.form_submission import (
    get_places, get_random_user, create_form_submission, 
    update_form_submission_status, check_existing_successful_submission
)
from app.db.schemas.form_submission import FormSubmissionCreate


class SubmissionWorkflow:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    async def process_all_submissions(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Process form submissions for all places in the database.
        Uses a random user for each submission.
        """
        logger.info("🚀 Starting automated form submission workflow")
        
        # Check if API keys are configured
        if not settings.openai_api_key and not settings.anthropic_api_key:
            error_msg = "❌ No LLM API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file"
            logger.error(error_msg)
            return {"status": "failed", "message": error_msg}
        
        # Get all places
        places = await get_places(db)
        if not places:
            logger.warning("❌ No places found in database")
            return {"status": "completed", "message": "No places to process"}
        
        # Get a random user for submissions
        user = await get_random_user(db)
        if not user:
            logger.error("❌ No users found in database")
            return {"status": "failed", "message": "No users available for form submission"}
        
        logger.info(f"📋 Processing {len(places)} places using user: {user.first_name} ({user.email})")
        logger.info(f"⚙️ Browser UI enabled: {not settings.headless}")
        logger.info(f"⏱️ Form timeout: {settings.form_timeout} seconds")
        
        successful_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Process each place sequentially
        for i, place in enumerate(places, 1):
            try:
                logger.info(f"🌐 [{i}/{len(places)}] Processing: {place.name} - {place.website or 'No website'}")
                
                result = await self._process_single_place(db, place, user)
                self.results.append(result)
                
                if result["status"] == "success":
                    successful_count += 1
                    logger.info(f"✅ [{i}/{len(places)}] Success: {place.name}")
                elif result["status"] == "skipped":
                    skipped_count += 1
                    if "Contact form is not available" in result.get("error", ""):
                        logger.info(f"📭 [{i}/{len(places)}] Skipped: {place.name} - No contact form available")
                    else:
                        logger.warning(f"⚠️ [{i}/{len(places)}] Skipped: {place.name} - {result.get('error', 'Unknown reason')}")
                else:
                    failed_count += 1
                    logger.error(f"❌ [{i}/{len(places)}] Failed: {place.name} - {result.get('error', 'Unknown error')}")
                
                # Add delay between submissions to be respectful
                if i < len(places):  # Don't wait after the last one
                    logger.info(f"⏳ Waiting 3 seconds before next submission...")
                    await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"💥 Unexpected error processing {place.name}: {str(e)}")
                failed_count += 1
                
                # Still record the failed attempt
                self.results.append({
                    "place_id": place.id,
                    "place_name": place.name,
                    "website_url": place.website or "",
                    "status": "failed",
                    "error": f"Workflow error: {str(e)}"
                })
        
        final_result = {
            "status": "completed",
            "total_places": len(places),
            "successful": successful_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "user_used": {
                "id": user.id,
                "name": user.first_name,
                "email": user.email
            },
            "processing_results": self.results,
            "configuration": {
                "headless_mode": settings.headless,
                "form_timeout": settings.form_timeout,
                "llm_provider": "OpenAI" if settings.openai_api_key else "Anthropic" if settings.anthropic_api_key else "None"
            }
        }
        
        logger.info(f"🏁 Workflow completed: {successful_count} successful, {failed_count} failed, {skipped_count} skipped")
        return final_result
    
    async def _process_single_place(self, db: AsyncSession, place, user) -> Dict[str, Any]:
        """
        Process form submission for a single place.
        """
        # Skip if no website URL
        if not place.website:
            logger.warning(f"⚠️ No website URL for place {place.name}")
            return {
                "place_id": place.id,
                "place_name": place.name,
                "website_url": "",
                "status": "skipped",
                "error": "No website URL available"
            }
        
        # Check if user already has a successful submission for this place
        existing_submission = await check_existing_successful_submission(db, user.id, place.id)
        if existing_submission:
            logger.info(f"✅ User {user.first_name} ({user.email}) already has successful submission for {place.name} (submission #{existing_submission.id})")
            return {
                "place_id": place.id,
                "place_name": place.name,
                "website_url": place.website,
                "status": "skipped",
                "error": "User already has successful submission for this place",
                "existing_submission_id": existing_submission.id,
                "existing_submission_date": existing_submission.submitted_at
            }
        
        # Validate website URL
        website_url = place.website.strip()
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        # Create initial form submission record
        submission_data = FormSubmissionCreate(
            place_id=place.id,
            user_id=user.id,
            website_url=website_url,
            submission_status="pending"
        )
        
        db_submission = await create_form_submission(db, submission_data)
        logger.info(f"📝 Created submission record #{db_submission.id} for {place.name}")
        
        try:
            # Prepare user data for form submission
            user_data = {
                "name": f"{user.first_name} {user.last_name or ''}".strip(),
                "email": user.email,
                "phone": user.phone or "",
                "message": f"Hello, I'm interested in your services. Please contact me at {user.email}."
            }
            
            logger.info(f"👤 User data prepared for {place.name}: {user_data['name']} ({user_data['email']})")
            
            # Use FormSubmitter to fill and submit the contact form
            async with FormSubmitter() as submitter:
                logger.info(f"🔧 Starting form submission for {place.name}...")
                
                submission_result = await submitter.submit_contact_form(
                    website_url=website_url, 
                    user_data=user_data,
                    user_id=user.id,
                    place_id=place.id,
                    db_session=db
                )
            
            # Update database based on result
            if submission_result["status"] == "success":
                await update_form_submission_status(db, db_submission.id, "success")
                logger.info(f"💾 Database updated: submission #{db_submission.id} marked as success")
                
                return {
                    "submission_id": db_submission.id,
                    "place_id": place.id,
                    "place_name": place.name,
                    "website_url": website_url,
                    "status": "success",
                    "message": submission_result["message"]
                }
            elif submission_result["status"] == "skipped":
                await update_form_submission_status(
                    db, 
                    db_submission.id, 
                    "skipped", 
                    submission_result.get("error", "Contact form is not available")
                )
                logger.info(f"💾 Database updated: submission #{db_submission.id} marked as skipped")
                
                return {
                    "submission_id": db_submission.id,
                    "place_id": place.id,
                    "place_name": place.name,
                    "website_url": website_url,
                    "status": "skipped",
                    "error": submission_result.get("error", "Contact form is not available")
                }
            else:
                await update_form_submission_status(
                    db, 
                    db_submission.id, 
                    "failed", 
                    submission_result.get("message", "Unknown error")
                )
                logger.warning(f"💾 Database updated: submission #{db_submission.id} marked as failed")
                
                return {
                    "submission_id": db_submission.id,
                    "place_id": place.id,
                    "place_name": place.name,
                    "website_url": website_url,
                    "status": "failed",
                    "error": submission_result.get("message", "Unknown error")
                }
                
        except asyncio.TimeoutError:
            error_message = f"Form submission timed out after {settings.form_timeout} seconds"
            logger.error(f"⏰ {error_message} for {place.name}")
            
            # Update database with timeout error
            await update_form_submission_status(
                db, 
                db_submission.id, 
                "failed", 
                error_message
            )
            
            return {
                "submission_id": db_submission.id,
                "place_id": place.id,
                "place_name": place.name,
                "website_url": website_url,
                "status": "failed",
                "error": error_message
            }
            
        except Exception as e:
            error_message = f"Exception during form submission: {str(e)}"
            logger.error(f"💥 {error_message} for {place.name}")
            
            # Update database with error
            await update_form_submission_status(
                db, 
                db_submission.id, 
                "failed", 
                error_message
            )
            
            return {
                "submission_id": db_submission.id,
                "place_id": place.id,
                "place_name": place.name,
                "website_url": website_url,
                "status": "failed",
                "error": error_message
            } 