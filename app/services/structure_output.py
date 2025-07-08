import json
import re
from typing import Dict, Any, Optional, List
from loguru import logger


class StructuredOutputHandler:
    """
    Handles structured output parsing and fallback logic for form submissions.
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
    def parse_structured_output(api_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse structured output from API result with multiple fallback strategies.
        """
        website_url = api_result.get("website_url", "unknown")
        
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
        
        # Strategy 3: Analyze agent steps for implicit structured output
        agent_steps = api_result.get("steps", [])
        if agent_steps:
            step_analysis = StructuredOutputHandler._analyze_steps_for_structured_output(agent_steps)
            logger.info(f"📋 Generated structured output from agent steps for {website_url}")
            return step_analysis
        
        # Strategy 4: Fallback to basic structure
        logger.warning(f"📋 No structured output found, using fallback for {website_url}")
        return StructuredOutputHandler._create_fallback_output(api_result)
    
    @staticmethod
    def _validate_structured_output(structured_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize structured output format.
        """
        # Ensure required fields
        status = structured_output.get("status", "failed")
        message = structured_output.get("message", "Form submission completed")
        form_found = structured_output.get("form_found", False)
        
        # Normalize status values
        if status not in ["success", "failed", "skipped"]:
            status = "failed"
        
        return {
            "status": status,
            "message": message,
            "form_found": form_found,
            "fields_filled": structured_output.get("fields_filled", []),
            "errors": structured_output.get("errors", []),
            "submission_details": structured_output.get("submission_details", {})
        }
    
    @staticmethod
    def _parse_from_raw_output(raw_output: str) -> Optional[Dict[str, Any]]:
        """
        Parse structured output from raw text output using various strategies.
        """
        # Strategy 1: Direct JSON parsing
        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, dict) and "status" in parsed:
                return StructuredOutputHandler._validate_structured_output(parsed)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from text
        json_match = re.search(r'\{[^{}]*"status"[^{}]*\}', raw_output, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return StructuredOutputHandler._validate_structured_output(parsed)
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Parse status keywords from text
        status_keywords = {
            "success": ["success", "submitted", "completed", "thank you", "confirmation"],
            "skipped": ["no contact form", "no form found", "not available", "404"],
            "failed": ["failed", "error", "blocked", "captcha", "timeout"]
        }
        
        raw_lower = raw_output.lower()
        for status, keywords in status_keywords.items():
            if any(keyword in raw_lower for keyword in keywords):
                return {
                    "status": status,
                    "message": raw_output[:200],  # First 200 chars as message
                    "form_found": status != "skipped",
                    "fields_filled": [],
                    "errors": [raw_output] if status == "failed" else [],
                    "submission_details": {}
                }
        
        return None
    
    @staticmethod
    def _analyze_steps_for_structured_output(agent_steps: List[Dict]) -> Dict[str, Any]:
        """
        Analyze agent steps to create structured output.
        """
        if not agent_steps:
            return StructuredOutputHandler._create_fallback_output({"steps": []})
        
        # Analyze step patterns
        form_found = False
        fields_filled = []
        errors = []
        submit_clicked = False
        confirmation_found = False
        
        for step in agent_steps:
            step_goal = step.get("next_goal", "").lower()
            step_eval = step.get("evaluation_previous_goal", "").lower()
            
            # Check for form discovery
            if "contact form" in step_goal or "form" in step_goal:
                form_found = True
            
            # Check for field filling
            if any(field in step_goal for field in ["name", "email", "phone", "message"]):
                if "fill" in step_goal or "input" in step_goal:
                    field_name = StructuredOutputHandler._extract_field_name(step_goal)
                    if field_name and field_name not in fields_filled:
                        fields_filled.append(field_name)
            
            # Check for submit button clicks
            if "submit" in step_goal or "submit" in step_eval:
                if "click" in step_goal or "clicked" in step_eval:
                    submit_clicked = True
            
            # Check for confirmation
            if any(keyword in step_goal for keyword in ["confirmation", "success", "thank you"]):
                confirmation_found = True
            
            # Check for errors
            if "error" in step_eval or "failed" in step_eval:
                errors.append(step_eval[:100])
        
        # Determine status based on analysis
        total_steps = len(agent_steps)
        
        # Success conditions
        if form_found and fields_filled and submit_clicked and total_steps >= 15:
            if confirmation_found:
                status = "success"
                message = f"Form submitted successfully with confirmation found. Filled fields: {', '.join(fields_filled)}"
            elif total_steps >= 20:
                # Emergency checkpoint logic
                status = "success"
                message = f"Form likely submitted successfully (emergency checkpoint at {total_steps} steps). Filled fields: {', '.join(fields_filled)}"
            else:
                status = "success"
                message = f"Form submitted successfully. Filled fields: {', '.join(fields_filled)}"
        elif not form_found:
            status = "skipped"
            message = "No contact form found on the page"
        elif form_found and not fields_filled:
            status = "failed"
            message = "Contact form found but could not fill fields"
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
    
    @staticmethod
    def _extract_field_name(step_goal: str) -> Optional[str]:
        """
        Extract field name from step goal text.
        """
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
        
        return None
    
    @staticmethod
    def _create_fallback_output(api_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback structured output when all other methods fail.
        """
        # Check if task completed (finished status)
        if api_result.get("status") == "success":
            return {
                "status": "failed",
                "message": "Form submission completed but no structured output available",
                "form_found": True,
                "fields_filled": [],
                "errors": ["No structured output available"],
                "submission_details": {}
            }
        else:
            return {
                "status": "failed",
                "message": "Form submission failed - no valid response from API",
                "form_found": False,
                "fields_filled": [],
                "errors": ["Invalid API response"],
                "submission_details": {}
            }
    
    @staticmethod
    def enhance_with_agent_analysis(structured_output: Dict[str, Any], agent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance structured output with agent step analysis.
        """
        # Override status if agent analysis indicates success
        if structured_output["status"] == "failed" and agent_analysis.get("likely_success", False):
            logger.info(f"🔍 Agent analysis overriding structured output status to success")
            structured_output["status"] = "success"
            structured_output["message"] = f"Form submission successful based on agent behavior analysis. {agent_analysis.get('reason', '')}"
        
        # Add agent analysis details
        structured_output["agent_analysis"] = agent_analysis
        
        return structured_output
