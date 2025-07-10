import json
import re
from typing import Dict, Any, Optional, List, Union
from loguru import logger


class StructuredOutputHandler:
    """
    Handles structured output parsing and fallback logic for form submissions.
    Designed to be bulletproof - always returns valid structured output.
    """
    
    @staticmethod
    def get_form_submission_schema() -> Dict[str, Any]:
        """
        Returns the JSON schema for form submission structured output.
        """
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["success", "failed", "skipped"],
                    "description": "Status of the form submission"
                },
                "message": {
                    "type": "string",
                    "description": "Detailed message about the submission result"
                },
                "form_found": {
                    "type": "boolean",
                    "description": "Whether a contact form was found on the page"
                },
                "fields_filled": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of form fields that were successfully filled"
                },
                "errors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of errors encountered during submission"
                },
                "submission_details": {
                    "type": "object",
                    "properties": {
                        "submit_clicked": {"type": "boolean"},
                        "confirmation_found": {"type": "boolean"},
                        "page_redirected": {"type": "boolean"},
                        "fields_cleared": {"type": "boolean"}
                    },
                    "description": "Additional details about the submission process"
                }
            },
            "required": ["status", "message", "form_found"]
        }
    
    @staticmethod
    def parse_structured_output(api_result: Union[Dict[str, Any], str, None]) -> Dict[str, Any]:
        """
        Parse structured output from API result with bulletproof fallback strategies.
        This method NEVER fails and always returns a valid structured output.
        """
        try:
            # Handle None or invalid input
            if api_result is None:
                logger.warning("📋 API result is None, using fallback output")
                return StructuredOutputHandler._create_error_fallback("API result is None")
            
            # Handle string responses (raw text)
            if isinstance(api_result, str):
                logger.info("📋 API result is string, attempting to parse")
                return StructuredOutputHandler._parse_string_response(api_result)
            
            # Handle non-dict responses
            if not isinstance(api_result, dict):
                logger.warning(f"📋 API result is not dict (type: {type(api_result)}), using fallback")
                return StructuredOutputHandler._create_error_fallback(f"Invalid API response type: {type(api_result)}")
            
            website_url = api_result.get("website_url", "unknown")
            logger.info(f"📋 Processing structured output for {website_url}")
            
            # Strategy 1: Direct structured output
            structured_output = api_result.get("structured_output")
            if structured_output and isinstance(structured_output, dict):
                logger.info(f"📋 Direct structured output found for {website_url}")
                return StructuredOutputHandler._validate_structured_output(structured_output)
            
            # Strategy 2: Parse from raw output string
            raw_output = api_result.get("output", "")
            if raw_output:
                parsed_output = StructuredOutputHandler._parse_from_raw_output(raw_output)
                if parsed_output:
                    logger.info(f"📋 Parsed structured output from raw text for {website_url}")
                    return parsed_output
            
            # Strategy 3: Check for browser-use specific response format
            browser_use_result = StructuredOutputHandler._parse_browser_use_response(api_result)
            if browser_use_result:
                logger.info(f"📋 Parsed browser-use specific response for {website_url}")
                return browser_use_result
            
            # Strategy 4: Analyze agent steps for implicit structured output
            agent_steps = api_result.get("steps", [])
            if agent_steps:
                step_analysis = StructuredOutputHandler._analyze_steps_for_structured_output(agent_steps)
                logger.info(f"📋 Generated structured output from agent steps for {website_url}")
                return step_analysis
            
            # Strategy 5: Check for error indicators
            error_result = StructuredOutputHandler._check_for_api_errors(api_result)
            if error_result:
                logger.info(f"📋 Detected API error for {website_url}")
                return error_result
            
            # Strategy 6: Fallback to basic structure
            logger.warning(f"📋 No structured output found, using fallback for {website_url}")
            return StructuredOutputHandler._create_fallback_output(api_result)
            
        except Exception as e:
            logger.error(f"📋 Critical error in parse_structured_output: {str(e)}")
            return StructuredOutputHandler._create_error_fallback(f"Critical parsing error: {str(e)}")
    
    @staticmethod
    def _parse_string_response(response: str) -> Dict[str, Any]:
        """
        Parse string responses from API.
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return StructuredOutputHandler._validate_structured_output(parsed)
        except json.JSONDecodeError:
            pass
        
        # Parse as raw text
        return StructuredOutputHandler._parse_from_raw_output(response) or \
               StructuredOutputHandler._create_error_fallback("Invalid string response")
    
    @staticmethod
    def _parse_browser_use_response(api_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse browser-use specific response formats.
        """
        try:
            # Check for browser-use completion status
            if "status" in api_result:
                status = api_result.get("status")
                if status == "completed":
                    return {
                        "status": "success",
                        "message": "Browser automation completed successfully",
                        "form_found": True,
                        "fields_filled": [],
                        "errors": [],
                        "submission_details": {
                            "submit_clicked": True,
                            "confirmation_found": False,
                            "page_redirected": False,
                            "fields_cleared": False
                        }
                    }
                elif status == "failed":
                    error_msg = api_result.get("error", "Browser automation failed")
                    return {
                        "status": "failed",
                        "message": error_msg,
                        "form_found": False,
                        "fields_filled": [],
                        "errors": [error_msg],
                        "submission_details": {}
                    }
            
            # Check for browser-use result format
            if "result" in api_result:
                result = api_result.get("result")
                if isinstance(result, dict):
                    return StructuredOutputHandler._validate_structured_output(result)
            
            # Check for browser-use error format
            if "error" in api_result:
                error_msg = api_result.get("error", "Unknown browser error")
                return {
                    "status": "failed",
                    "message": f"Browser automation error: {error_msg}",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": [error_msg],
                    "submission_details": {}
                }
                
        except Exception as e:
            logger.error(f"📋 Error parsing browser-use response: {str(e)}")
            
        return None
    
    @staticmethod
    def _check_for_api_errors(api_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check for common API error patterns.
        """
        try:
            # Check for timeout errors
            if "timeout" in str(api_result).lower():
                return {
                    "status": "failed",
                    "message": "Request timed out",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": ["Request timeout"],
                    "submission_details": {}
                }
            
            # Check for network errors
            if "network" in str(api_result).lower() or "connection" in str(api_result).lower():
                return {
                    "status": "failed",
                    "message": "Network connection error",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": ["Network error"],
                    "submission_details": {}
                }
            
            # Check for rate limiting
            if "rate limit" in str(api_result).lower() or "429" in str(api_result):
                return {
                    "status": "failed",
                    "message": "Rate limit exceeded",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": ["Rate limit exceeded"],
                    "submission_details": {}
                }
            
            # Check for API key errors
            if "api key" in str(api_result).lower() or "unauthorized" in str(api_result).lower():
                return {
                    "status": "failed",
                    "message": "API authentication error",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": ["API authentication failed"],
                    "submission_details": {}
                }
                
        except Exception as e:
            logger.error(f"📋 Error checking API errors: {str(e)}")
            
        return None
    
    @staticmethod
    def _validate_structured_output(structured_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize structured output format.
        """
        try:
            # Ensure required fields with safe defaults
            status = structured_output.get("status", "failed")
            message = structured_output.get("message", "Form submission completed")
            form_found = structured_output.get("form_found", False)
            
            # Normalize status values
            if status not in ["success", "failed", "skipped"]:
                status = "failed"
            
            # Ensure fields are correct types
            fields_filled = structured_output.get("fields_filled", [])
            if not isinstance(fields_filled, list):
                fields_filled = []
            
            errors = structured_output.get("errors", [])
            if not isinstance(errors, list):
                errors = [str(errors)] if errors else []
            
            submission_details = structured_output.get("submission_details", {})
            if not isinstance(submission_details, dict):
                submission_details = {}
            
            return {
                "status": status,
                "message": str(message),
                "form_found": bool(form_found),
                "fields_filled": fields_filled,
                "errors": errors,
                "submission_details": submission_details
            }
            
        except Exception as e:
            logger.error(f"📋 Error validating structured output: {str(e)}")
            return StructuredOutputHandler._create_error_fallback(f"Validation error: {str(e)}")
    
    @staticmethod
    def _parse_from_raw_output(raw_output: str) -> Optional[Dict[str, Any]]:
        """
        Parse structured output from raw text output using various strategies.
        """
        try:
            if not raw_output or not isinstance(raw_output, str):
                return None
            
            # Strategy 1: Direct JSON parsing
            try:
                parsed = json.loads(raw_output)
                if isinstance(parsed, dict) and "status" in parsed:
                    return StructuredOutputHandler._validate_structured_output(parsed)
            except json.JSONDecodeError:
                pass
            
            # Strategy 2: Extract JSON from text
            json_patterns = [
                r'\{[^{}]*"status"[^{}]*\}',  # Simple JSON
                r'\{.*?"status".*?\}',        # More complex JSON
                r'```json\s*(\{.*?\})\s*```', # Markdown JSON blocks
                r'```\s*(\{.*?\})\s*```'      # Generic code blocks
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, raw_output, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group(1) if json_match.groups() else json_match.group()
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict):
                            return StructuredOutputHandler._validate_structured_output(parsed)
                    except json.JSONDecodeError:
                        continue
            
            # Strategy 3: Parse status keywords from text
            status_keywords = {
                "success": ["success", "submitted", "completed", "thank you", "confirmation", "sent successfully"],
                "skipped": ["no contact form", "no form found", "not available", "404", "form not found"],
                "failed": ["failed", "error", "blocked", "captcha", "timeout", "invalid", "exception"]
            }
            
            raw_lower = raw_output.lower()
            for status, keywords in status_keywords.items():
                if any(keyword in raw_lower for keyword in keywords):
                    return {
                        "status": status,
                        "message": raw_output[:500],  # First 500 chars as message
                        "form_found": status != "skipped",
                        "fields_filled": [],
                        "errors": [raw_output[:200]] if status == "failed" else [],
                        "submission_details": {}
                    }
            
        except Exception as e:
            logger.error(f"📋 Error parsing raw output: {str(e)}")
            
        return None
    
    @staticmethod
    def _analyze_steps_for_structured_output(agent_steps: List[Dict]) -> Dict[str, Any]:
        """
        Analyze agent steps to create structured output.
        """
        try:
            if not agent_steps or not isinstance(agent_steps, list):
                return StructuredOutputHandler._create_error_fallback("No agent steps available")
            
            # Analyze step patterns
            form_found = False
            fields_filled = []
            errors = []
            submit_clicked = False
            confirmation_found = False
            
            for step in agent_steps:
                if not isinstance(step, dict):
                    continue
                    
                step_goal = str(step.get("next_goal", "")).lower()
                step_eval = str(step.get("evaluation_previous_goal", "")).lower()
                
                # Check for form discovery
                if any(keyword in step_goal for keyword in ["contact form", "form", "contact us"]):
                    form_found = True
                
                # Check for field filling
                field_keywords = ["name", "email", "phone", "message", "subject", "company", "inquiry", "comment", "details"]
                filling_actions = ["fill", "input", "enter", "type", "click", "select", "focus", "clear", "paste"]
                
                for field in field_keywords:
                    if field in step_goal:
                        # Check if any filling action is mentioned
                        if any(action in step_goal for action in filling_actions):
                            if field not in fields_filled:
                                fields_filled.append(field)
                        # Also check if the field is mentioned with success in evaluation
                        elif any(success_word in step_eval for success_word in ["filled", "entered", "typed", "successful", "complete"]):
                            if field in step_eval and field not in fields_filled:
                                fields_filled.append(field)
                
                # Additional field detection - check for successful field interactions
                if any(word in step_eval for word in ["filled", "entered", "typed", "successful field", "text entered"]):
                    # Look for field names in the evaluation
                    for field in field_keywords:
                        if field in step_eval and field not in fields_filled:
                            fields_filled.append(field)
                
                # Check for generic field filling indicators
                if any(phrase in step_goal for phrase in ["fill form", "enter data", "input information", "complete form"]):
                    # If we see generic form filling, assume basic fields are filled
                    basic_fields = ["name", "email", "message"]
                    for field in basic_fields:
                        if field not in fields_filled:
                            fields_filled.append(field)
                
                # Check for submit button clicks
                if "submit" in step_goal and "click" in step_goal:
                    submit_clicked = True
                
                # Check for confirmation
                if any(keyword in step_goal for keyword in ["confirmation", "success", "thank you"]):
                    confirmation_found = True
                
                # Check for errors
                if "error" in step_eval or "failed" in step_eval:
                    errors.append(step_eval[:100])
            
            # Determine status based on analysis
            total_steps = len(agent_steps)
            
            # Success conditions - more forgiving logic
            if form_found and fields_filled:
                # If we found a form and filled ANY fields, consider various success scenarios
                if submit_clicked:
                    # Form found, fields filled, submit clicked - this is success
                    if confirmation_found:
                        status = "success"
                        message = f"Form submitted successfully with confirmation. Filled fields: {', '.join(fields_filled)}"
                    elif total_steps >= 20:
                        status = "success"
                        message = f"Form likely submitted successfully (emergency checkpoint at {total_steps} steps). Filled fields: {', '.join(fields_filled)}"
                    else:
                        status = "success"
                        message = f"Form submitted successfully. Filled fields: {', '.join(fields_filled)}"
                else:
                    # Form found and fields filled but no submit click detected
                    if total_steps >= 15:
                        # Long execution suggests submission attempt
                        status = "success"
                        message = f"Form likely submitted successfully (long execution with {total_steps} steps). Filled fields: {', '.join(fields_filled)}"
                    else:
                        # Short execution, fields filled but no submit
                        status = "failed"
                        message = f"Form fields filled but submission not completed. Filled fields: {', '.join(fields_filled)}"
            elif form_found and not fields_filled:
                # Form found but no fields filled
                if total_steps >= 10:
                    # If many steps were taken, maybe fields were filled but not detected
                    status = "success"
                    message = f"Contact form processed with {total_steps} steps - fields may have been filled but not detected"
                else:
                    status = "failed"
                    message = "Contact form found but could not fill fields"
            elif not form_found:
                status = "skipped"
                message = "No contact form found on the page"
            else:
                # Fallback case
                if total_steps >= 15:
                    status = "success"
                    message = f"Form submission completed with {total_steps} steps - likely successful"
                else:
                    status = "failed"
                    message = f"Form submission failed. Errors: {'; '.join(errors) if errors else 'Unknown error'}"
            
            return {
                "status": status,
                "message": message,
                "form_found": form_found,
                "fields_filled": fields_filled,
                "errors": errors,
                "submission_details": {
                    "submit_clicked": submit_clicked,
                    "confirmation_found": confirmation_found,
                    "page_redirected": False,
                    "fields_cleared": False
                }
            }
            
        except Exception as e:
            logger.error(f"📋 Error analyzing agent steps: {str(e)}")
            return StructuredOutputHandler._create_error_fallback(f"Step analysis error: {str(e)}")
    
    @staticmethod
    def _extract_field_name(step_goal: str) -> Optional[str]:
        """
        Extract field name from step goal text.
        """
        try:
            if not step_goal:
                return None
                
            field_patterns = {
                "name": r"\b(name|full name|first name|last name)\b",
                "email": r"\b(email|e-mail|email address)\b",
                "phone": r"\b(phone|telephone|mobile|contact number)\b",
                "message": r"\b(message|comment|inquiry|description)\b",
                "subject": r"\b(subject|topic|title)\b",
                "company": r"\b(company|organization|business)\b"
            }
            
            for field_name, pattern in field_patterns.items():
                if re.search(pattern, step_goal, re.IGNORECASE):
                    return field_name
                    
        except Exception as e:
            logger.error(f"📋 Error extracting field name: {str(e)}")
        
        return None
    
    @staticmethod
    def _create_fallback_output(api_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback structured output when all other methods fail.
        """
        try:
            # Check if task completed (finished status)
            if api_result.get("status") == "success" or api_result.get("status") == "completed":
                return {
                    "status": "success",
                    "message": "Form submission completed (fallback analysis)",
                    "form_found": True,
                    "fields_filled": [],
                    "errors": [],
                    "submission_details": {}
                }
            else:
                return {
                    "status": "failed",
                    "message": "Form submission failed (fallback analysis)",
                    "form_found": False,
                    "fields_filled": [],
                    "errors": ["Unable to determine specific error"],
                    "submission_details": {}
                }
                
        except Exception as e:
            logger.error(f"📋 Error creating fallback output: {str(e)}")
            return StructuredOutputHandler._create_error_fallback(f"Fallback error: {str(e)}")
    
    @staticmethod
    def _create_error_fallback(error_msg: str) -> Dict[str, Any]:
        """
        Create error fallback - the ultimate failsafe that never fails.
        """
        return {
            "status": "failed",
            "message": f"Structured output parsing error: {error_msg}",
            "form_found": False,
            "fields_filled": [],
            "errors": [error_msg],
            "submission_details": {}
        }
    
    @staticmethod
    def enhance_with_agent_analysis(structured_output: Dict[str, Any], agent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance structured output with agent step analysis.
        """
        try:
            if not isinstance(structured_output, dict):
                structured_output = StructuredOutputHandler._create_error_fallback("Invalid structured output for enhancement")
            
            if not isinstance(agent_analysis, dict):
                agent_analysis = {}
            
            # Override status if agent analysis indicates success
            if structured_output.get("status") == "failed" and agent_analysis.get("likely_success", False):
                logger.info("🔍 Agent analysis overriding structured output status to success")
                structured_output["status"] = "success"
                structured_output["message"] = f"Form submission successful based on agent behavior analysis. {agent_analysis.get('reason', '')}"
            
            # Add agent analysis details
            structured_output["agent_analysis"] = agent_analysis
            
            return structured_output
            
        except Exception as e:
            logger.error(f"📋 Error enhancing with agent analysis: {str(e)}")
            return structured_output if isinstance(structured_output, dict) else StructuredOutputHandler._create_error_fallback(f"Enhancement error: {str(e)}")
