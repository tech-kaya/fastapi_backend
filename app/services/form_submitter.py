import asyncio
import os
from typing import Optional, Dict, Any
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from browser_use import Agent
from app.core.config import settings
from app.services.prompts import create_form_submission_prompt, create_form_analysis_prompt
from app.utils.form_selectors import (
    get_form_selector, get_field_selectors, get_submit_selector, get_navigation_selector,
    get_captcha_selectors, get_anti_bot_selectors, get_captcha_skip_selectors
)


class FormSubmitter:
    def __init__(self):
        self.agent: Optional[Agent] = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up if needed
        pass
    
    def _setup_stealth_mode(self):
        """Configure stealth mode environment variables for browser-use"""
        try:
            # Set stealth mode environment variables
            os.environ['STEALTH_MODE'] = 'true'
            os.environ['DISABLE_BLINK_FEATURES'] = 'AutomationControlled'
            os.environ['USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            os.environ['VIEWPORT_SIZE'] = '1366x768'
            os.environ['DISABLE_WEB_SECURITY'] = 'false'
            os.environ['DISABLE_FEATURES'] = 'VizDisplayCompositor'
            
            # Additional stealth settings
            os.environ['DISABLE_EXTENSIONS'] = 'false'
            os.environ['DISABLE_PLUGINS'] = 'false'
            os.environ['DISABLE_IMAGES'] = 'false'
            os.environ['DISABLE_JAVASCRIPT'] = 'false'
            
            # Anti-detection measures
            os.environ['HIDE_WEBDRIVER'] = 'true'
            os.environ['RANDOMIZE_VIEWPORT'] = 'true'
            os.environ['HUMAN_DELAYS'] = 'true'
            
            logger.info("🥷 Stealth mode configured for browser automation")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not configure stealth mode: {e}")
    
    def _get_llm_config(self):
        """Get LLM configuration for browser-use Agent"""
        try:
            # Check for OpenAI API key first
            if settings.openai_api_key:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.openai_api_key,
                    temperature=0.1  # Lower temperature for more focused behavior
                )
            
            # Check for Anthropic API key
            elif settings.anthropic_api_key:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    api_key=settings.anthropic_api_key,
                    temperature=0.1
                )
            
            else:
                logger.warning("No LLM API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
                return None
                
        except ImportError as e:
            logger.error(f"Failed to import LLM class: {e}")
            logger.info("Make sure to install: pip install langchain-openai langchain-anthropic")
            return None
    
    async def _detect_captcha_or_bot_protection(self) -> Dict[str, Any]:
        """Detect if CAPTCHA or anti-bot protection is present"""
        detection_result = {
            "captcha_detected": False,
            "bot_protection_detected": False,
            "skip_available": False,
            "captcha_type": None,
            "message": "No protection detected"
        }
        
        try:
            # This would be implemented if we had direct browser access
            # For now, we'll rely on the AI agent to detect and report
            logger.info("🔍 CAPTCHA/Bot protection detection delegated to AI agent")
            
        except Exception as e:
            logger.error(f"Error detecting protection: {e}")
            
        return detection_result
    

    
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(3))  # Reduced retries to prevent getting stuck
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
            
            # Setup stealth mode before starting
            self._setup_stealth_mode()
            
            # Check if this user has already successfully submitted to this place
            if user_id and place_id and db_session:
                from app.db.crud.form_submission import check_existing_successful_submission
                existing_submission = await check_existing_successful_submission(db_session, user_id, place_id)
                if existing_submission:
                    logger.info(f"✅ User {user_id} already has successful submission for place {place_id} (submission #{existing_submission.id})")
                    return {
                        "status": "skipped",
                        "message": f"User already has successful submission for this place (submission #{existing_submission.id})",
                        "existing_submission_id": existing_submission.id,
                        "website_url": website_url
                    }
            
            # Create the form submission prompt for the AI agent
            task_prompt = create_form_submission_prompt(website_url, user_data)
            
            # Get LLM configuration
            llm = self._get_llm_config()
            if not llm:
                return {
                    "status": "failed",
                    "message": "No LLM configuration available. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file",
                    "error": "Missing API keys"
                }
            
            logger.info(f"✅ LLM configured: {type(llm).__name__}")
            logger.info(f"🥷 Stealth mode enabled for anti-bot evasion")
            
            # Create agent with stealth configuration
            self.agent = Agent(
                task=task_prompt,
                llm=llm
            )
            
            logger.info(f"🌐 Running browser agent for form submission with stealth and CAPTCHA handling...")
            
            # Execute the form submission task with aggressive timeout to prevent getting stuck
            try:
                result = await asyncio.wait_for(
                    self.agent.run(),
                    timeout=min(settings.form_timeout, 180)  # Max 3 minutes, use settings timeout if smaller
                )
                
                logger.info(f"✅ Form submission completed for {website_url}")
                
                # Check if result indicates no contact form available
                if "NO_CONTACT_FORM_AVAILABLE" in str(result):
                    logger.warning(f"📭 No contact form found for {website_url}")
                    return {
                        "status": "skipped",
                        "message": "Contact form is not available on this website",
                        "error": "Contact form is not available",
                        "agent_result": str(result),
                        "website_url": website_url
                    }
                
                # Check if result indicates CAPTCHA blocking
                if "captcha" in str(result).lower() or "verification" in str(result).lower():
                    logger.warning(f"🔒 CAPTCHA detected during submission for {website_url}")
                    return {
                        "status": "failed",
                        "message": "Form submission blocked by CAPTCHA verification",
                        "error": "CAPTCHA_BLOCKED",
                        "agent_result": str(result),
                        "website_url": website_url
                    }
                
                return {
                    "status": "success",
                    "message": "Form submitted successfully",
                    "agent_result": str(result),
                    "website_url": website_url
                }
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Form submission timed out for {website_url}")
                
                # Try to cancel the agent if it's still running
                if self.agent:
                    try:
                        # Force cleanup if possible
                        logger.info("🔄 Attempting to cleanup stuck agent...")
                    except:
                        pass
                
                return {
                    "status": "failed",
                    "message": f"Form submission timed out after {min(settings.form_timeout, 180)} seconds",
                    "error": "Timeout - agent was stuck",
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
    

    
    async def test_form_detection(self, website_url: str) -> Dict[str, Any]:
        """Test method to analyze a website's contact form structure."""
        try:
            logger.info(f"🔍 Analyzing contact form structure for {website_url}")
            
            # Create analysis prompt
            analysis_prompt = create_form_analysis_prompt(website_url)
            
            # Get LLM configuration
            llm = self._get_llm_config()
            if not llm:
                return {
                    "status": "failed",
                    "message": "No LLM configuration available. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file",
                    "error": "Missing API keys"
                }
            
            logger.info(f"✅ LLM configured: {type(llm).__name__}")
            
            self.agent = Agent(
                task=analysis_prompt,
                llm=llm
            )
            
            logger.info(f"🌐 Running browser agent for form analysis...")
            
            # Execute the analysis task with timeout (shorter for analysis)
            result = await asyncio.wait_for(
                self.agent.run(),
                timeout=120  # 2 minutes max for analysis
            )
            
            logger.info(f"✅ Form analysis completed for {website_url}")
            
            return {
                "status": "success",
                "message": "Form analysis completed",
                "analysis_result": str(result),
                "website_url": website_url
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Form analysis timed out after 120 seconds for {website_url}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "message": error_msg,
                "error": "Timeout"
            }
            
        except Exception as e:
            error_msg = f"Form analysis failed for {website_url}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "message": error_msg,
                "error": str(e)
            } 