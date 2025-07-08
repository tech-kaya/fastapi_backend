import asyncio
import json
import time
import requests
from typing import Optional, Dict, Any, List
from loguru import logger
from app.core.config import settings
from app.services.prompts import create_form_submission_prompt
from app.services.structure_output import StructuredOutputHandler


class BrowserUseAPIClient:
    """Browser-use cloud API client based on official documentation pattern"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.browser-use.com/api/v1'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def create_task(self, instructions: str, structured_output_schema: dict = None, config: Dict[str, Any] = None) -> str:
        """Create a new browser automation task"""
        payload = {
            "task": instructions
        }
        
        # Add structured output if provided
        if structured_output_schema:
            payload["structured_output_json"] = json.dumps(structured_output_schema)
        
        # Add configuration options
        if config:
            for key, value in config.items():
                if key != "structured_output_json":  # Already handled above
                    payload[key] = value
        
        try:
            response = requests.post(f'{self.base_url}/run-task', headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['id']
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> str:
        """Get current task status"""
        try:
            response = requests.get(f'{self.base_url}/task/{task_id}/status', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise
    
    def get_task_details(self, task_id: str) -> dict:
        """Get full task details including output"""
        try:
            response = requests.get(f'{self.base_url}/task/{task_id}', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get task details: {e}")
            raise
    
    def wait_for_completion(self, task_id: str, poll_interval: int = None, show_steps: bool = None) -> dict:
        """Poll task status until completion with real-time step monitoring"""
        if poll_interval is None:
            poll_interval = settings.poll_interval
        if show_steps is None:
            show_steps = settings.show_agent_steps
            
        unique_steps = []
        
        while True:
            details = self.get_task_details(task_id)
            new_steps = details.get('steps', [])
            
            # Show new steps in real-time
            if show_steps and new_steps != unique_steps:
                for step in new_steps:
                    if step not in unique_steps:
                        logger.info(f"🤖 Agent Step: {json.dumps(step, indent=2)}")
                unique_steps = new_steps
            
            status = details.get('status', 'unknown')
            
            if status in ['finished', 'failed', 'stopped']:
                return details
            
            logger.info(f"⏳ Task status: {status}")
            time.sleep(poll_interval)
    
    async def run_task(self, task_prompt: str, allowed_domains: List[str] = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a complete browser automation task"""
        try:
            # Get structured output schema
            structured_output_schema = StructuredOutputHandler.get_form_submission_schema()
            
            # Add allowed domains to config
            if allowed_domains:
                if not config:
                    config = {}
                config["allowed_domains"] = allowed_domains
            
            # Create task
            task_id = self.create_task(task_prompt, structured_output_schema, config)
            logger.info(f"🚀 Task created with ID: {task_id}")
            
            # Wait for completion with real-time monitoring
            result = self.wait_for_completion(task_id)
            
            # Process result
            if result.get('status') == 'finished':
                output = result.get('output', '')
                
                # Try to parse structured output
                structured_output = None
                if output:
                    try:
                        structured_output = json.loads(output)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse structured output: {output}")
                
                return {
                    "status": "success",
                    "output": output,
                    "structured_output": structured_output,
                    "task_id": task_id,
                    "steps": result.get('steps', [])
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Task failed with status: {result.get('status')}",
                    "task_id": task_id,
                    "steps": result.get('steps', [])
                }
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


class FormSubmitter:
    def __init__(self):
        """Initialize FormSubmitter with browser-use cloud API"""
        self.api_client: Optional[BrowserUseAPIClient] = None
        
    async def __aenter__(self):
        if not settings.browser_use_api_key:
            raise RuntimeError("BROWSER_USE_API_KEY is required. Please set it in your .env file")
        
        self.api_client = BrowserUseAPIClient(settings.browser_use_api_key)
        await self.api_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.api_client:
            await self.api_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def submit_contact_form(
        self, 
        website_url: str, 
        user_data: Dict[str, Any],
        user_id: Optional[int] = None,
        place_id: Optional[int] = None,
        db_session: Optional[Any] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"🚀 Starting form submission for {website_url}")
            
            # Check if this user has already successfully submitted to this place
            if user_id and place_id and db_session:
                from app.db.crud.form_submission import check_existing_successful_submission, check_existing_skipped_submission
                existing_submission = await check_existing_successful_submission(db_session, user_id, place_id)
                if existing_submission:
                    logger.info(f"✅ User {user_id} already has successful submission for place {place_id} (submission #{existing_submission.id})")
                    return {
                        "status": "skipped",
                        "message": f"User already has successful submission for this place (submission #{existing_submission.id})",
                        "existing_submission_id": existing_submission.id,
                        "website_url": website_url
                    }
                
                # Check if this place has already been marked as skipped (no contact form)
                existing_skipped_submission = await check_existing_skipped_submission(db_session, place_id)
                if existing_skipped_submission:
                    logger.info(f"📭 Place {place_id} already marked as skipped (no contact form) - submission #{existing_skipped_submission.id}")
                    return {
                        "status": "skipped",
                        "message": f"Place already marked as having no contact form (submission #{existing_skipped_submission.id})",
                        "existing_submission_id": existing_skipped_submission.id,
                        "website_url": website_url
                    }
            
            # Create the form submission prompt for the AI agent
            task_prompt = create_form_submission_prompt(website_url, user_data)
            
            # For browser-use cloud API, prepend navigation instruction
            task_prompt = f"First, navigate to {website_url} and then: {task_prompt}"
            
            # Use browser-use cloud API for form submission
            logger.info("🔗 Using browser-use cloud API for form submission with real-time monitoring")
            
            # Extract domain from website_url for allowed_domains
            from urllib.parse import urlparse
            parsed_url = urlparse(website_url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            result = await self.api_client.run_task(
                task_prompt=task_prompt,
                allowed_domains=[domain],
                config={
                    "llm_model": settings.llm_model,
                    "browser_viewport_width": settings.browser_viewport_width,
                    "browser_viewport_height": settings.browser_viewport_height,
                    "use_adblock": settings.use_adblock,
                    "highlight_elements": settings.highlight_elements,
                    "save_browser_data": settings.save_browser_data,
                    "max_agent_steps": settings.max_agent_steps,
                    "headless": settings.headless
                }
            )
            
            logger.info(f"✅ Form submission completed for {website_url}")
            
            # Process result using StructuredOutputHandler
            if result.get("status") == "success":
                # Add website_url to result for handler
                result["website_url"] = website_url
                
                # Parse structured output using the handler
                structured_output = StructuredOutputHandler.parse_structured_output(result)
                
                # Analyze agent steps for additional insights
                agent_analysis = self._analyze_agent_steps_for_success(result.get("steps", []))
                
                # Enhance structured output with agent analysis
                final_output = StructuredOutputHandler.enhance_with_agent_analysis(structured_output, agent_analysis)
                
                # Build final result
                return {
                    "status": final_output["status"],
                    "message": final_output["message"],
                    "form_found": final_output["form_found"],
                    "fields_filled": final_output["fields_filled"],
                    "errors": final_output["errors"],
                    "agent_result": str(result),
                    "agent_analysis": agent_analysis,
                    "website_url": website_url
                }
            
            # Handle case where task failed
            logger.error(f"❌ Form submission failed for {website_url}")
            return {
                "status": "failed",
                "message": "Form submission failed - no valid response from API",
                "error": "Invalid API response",
                "agent_result": str(result),
                "website_url": website_url
            }
            
        except Exception as e:
            error_msg = f"Form submission failed for {website_url}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            }
    
    def _analyze_agent_steps_for_success(self, agent_steps: List[Dict]) -> Dict[str, Any]:
        """
        Analyze agent steps to determine if form submission was likely successful.
        This implements the "step 20+ emergency checkpoint" logic from the prompts.
        """
        if not agent_steps:
            return {"likely_success": False, "reason": "No agent steps available"}
        
        # Extract step information
        total_steps = len(agent_steps)
        last_step = agent_steps[-1] if agent_steps else {}
        
        # Look for key success indicators in agent steps
        form_filled_steps = []
        submit_clicked_steps = []
        success_search_steps = []
        
        for step in agent_steps:
            step_goal = step.get("next_goal", "").lower()
            step_eval = step.get("evaluation_previous_goal", "").lower()
            
            # Check for form filling activities
            if any(keyword in step_goal for keyword in ["fill", "input", "enter", "click", "select"]):
                if any(field in step_goal for field in ["name", "email", "phone", "message", "checkbox"]):
                    form_filled_steps.append(step)
            
            # Check for submit button clicks
            if "submit" in step_goal or "submit" in step_eval:
                if any(keyword in step_eval for keyword in ["clicked", "successfully", "success"]):
                    submit_clicked_steps.append(step)
            
            # Check for success confirmation searches
            if any(keyword in step_goal for keyword in ["check", "verify", "success", "confirmation", "indicator"]):
                success_search_steps.append(step)
        
        # Analyze patterns for success indicators
        
        # Pattern 1: Step 20+ Emergency Checkpoint (from prompts)
        if total_steps >= 20:
            # Check if agent has been searching for success indicators for many steps
            recent_search_steps = [s for s in agent_steps[-10:] if 
                                 any(keyword in s.get("next_goal", "").lower() for keyword in 
                                     ["check", "verify", "success", "confirmation", "indicator", "scroll"])]
            
            if len(recent_search_steps) >= 5:  # Been searching for success for 5+ recent steps
                return {
                    "likely_success": True,
                    "reason": f"Step 20+ emergency checkpoint: {total_steps} steps completed, agent has been searching for success indicators for {len(recent_search_steps)} recent steps, indicating form was likely submitted successfully",
                    "total_steps": total_steps,
                    "success_search_steps": len(success_search_steps)
                }
        
        # Pattern 2: Submit button clicked successfully + prolonged success search
        if submit_clicked_steps:
            last_submit_step = submit_clicked_steps[-1]
            submit_step_num = last_submit_step.get("step", 0)
            
            # Count how many steps after submit are just searching for success
            steps_after_submit = [s for s in agent_steps if s.get("step", 0) > submit_step_num]
            success_search_after_submit = [s for s in steps_after_submit if 
                                         any(keyword in s.get("next_goal", "").lower() for keyword in 
                                             ["check", "verify", "success", "confirmation", "indicator", "scroll"])]
            
            if len(success_search_after_submit) >= 5:  # 5+ steps of just searching for success
                return {
                    "likely_success": True,
                    "reason": f"Submit button clicked successfully at step {submit_step_num}, followed by {len(success_search_after_submit)} steps of searching for success indicators - form likely submitted successfully",
                    "submit_step": submit_step_num,
                    "total_steps": total_steps,
                    "success_search_after_submit": len(success_search_after_submit)
                }
        
        # Pattern 3: Form filling completed + submit clicked + extended execution
        if form_filled_steps and submit_clicked_steps and total_steps >= 15:
            return {
                "likely_success": True,
                "reason": f"Form filling completed ({len(form_filled_steps)} fill steps), submit clicked ({len(submit_clicked_steps)} submit steps), and {total_steps} total steps indicates successful submission",
                "form_filled_steps": len(form_filled_steps),
                "submit_clicked_steps": len(submit_clicked_steps),
                "total_steps": total_steps
            }
        
        # Pattern 4: Look for explicit success indicators in step evaluations
        success_keywords = ["success", "submitted", "completed", "filled", "clicked submit"]
        for step in agent_steps:
            step_eval = step.get("evaluation_previous_goal", "").lower()
            if any(keyword in step_eval for keyword in success_keywords):
                if "submit" in step_eval or "form" in step_eval:
                    return {
                        "likely_success": True,
                        "reason": f"Found explicit success indicator in step {step.get('step', 'unknown')}: {step_eval}",
                        "success_step": step.get("step", "unknown"),
                        "total_steps": total_steps
                    }
        
        # Pattern 5: No success indicators found
        return {
            "likely_success": False,
            "reason": f"No clear success indicators found in {total_steps} steps. Form filling: {len(form_filled_steps)} steps, Submit clicked: {len(submit_clicked_steps)} steps, Success search: {len(success_search_steps)} steps",
            "form_filled_steps": len(form_filled_steps),
            "submit_clicked_steps": len(submit_clicked_steps),
            "success_search_steps": len(success_search_steps),
            "total_steps": total_steps
        } 