from typing import Dict, Any


def create_form_submission_prompt(website_url: str, user_data: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt for form submission with anti-stuck measures.
    """
    return f"""
Navigate to {website_url} and fill out the contact form with the provided information.

CRITICAL: USER-SPECIFIC DUPLICATE PREVENTION
- This user ({user_data.get('name', '')} - {user_data.get('email', '')}) should ONLY submit to this website ONCE
- Before filling any form, check if this specific user has already submitted to this website
- Look for any signs that this user/email has already contacted this business
- If you find evidence of previous submission by this user, STOP immediately
- Report "User has already submitted to this website" and use the "done" action
- NEVER submit the same form multiple times for the same user

IMPORTANT: BEFORE STARTING FORM SUBMISSION
- Check if this form has already been successfully submitted
- Look for any confirmation messages, success notifications, or "already submitted" indicators
- If you find evidence that the form was already submitted successfully, STOP immediately
- Report "Form already submitted successfully" and use the "done" action
- DO NOT fill or submit the same form multiple times

CRITICAL ANTI-STUCK MEASURES (MUST FOLLOW):
- NEVER click the same element more than 2 times total
- IF same action performed 3 times → IMMEDIATELY stop and try different approach
- IF stuck on any task for 5+ steps → ABANDON that task and move to next
- IF on step 20+ → START emergency completion process
- IF on step 30+ → STOP and report what was accomplished
- MAXIMUM 3 minutes total execution time

LOOP PREVENTION (EMERGENCY):
- Same button clicked 3 times → STOP clicking it, try different element
- Same text scrolled to 3 times → STOP scrolling, continue task
- Same popup interaction 3 times → IGNORE popup completely
- Same page visited 3 times → REPORT NO_CONTACT_FORM_AVAILABLE
- ANY repetitive pattern detected → BREAK OUT immediately
- Application launch popups (FaceTime, etc.) → CANCEL immediately, don't retry

RECOVERY STRATEGIES WHEN STUCK:
1. IMMEDIATE ACTIONS when element won't click:
   - Try scrolling up/down to refresh the page view
   - Try clicking a different nearby element
   - Navigate back using browser back button
   - Try typing the URL directly in address bar

2. OVERLAY/POPUP STUCK RECOVERY:
   - If same overlay keeps appearing, STOP trying to close it
   - IGNORE the overlay completely and work around it
   - Use scrolling to access form elements behind overlay
   - Continue with form submission even if overlay remains visible
   - Focus on form fields, not overlay dismissal

3. PHONE NUMBER VALIDATION ISSUES:
   - If phone field shows format error, DO NOT retry same format
   - Clear field and try next format from the list above
   - If 3 formats fail, skip phone field entirely
   - NEVER spend more than 30 seconds on phone formatting

4. CAPTCHA HANDLING ISSUES:
   - If CAPTCHA appears, handle it immediately according to priority
   - If SKIP button available, click it without attempting to solve
   - If CAPTCHA is complex, try audio alternative or refresh page
   - If CAPTCHA fails 2 times, abandon form and report CAPTCHA_BLOCKED
   - NEVER spend more than 60 seconds on CAPTCHA challenges

5. ALTERNATIVE EXPLORATION METHODS:
   - Use browser search (Ctrl+F) to find form fields
   - Look for visible form elements without clicking everything
   - Focus on collecting visible information rather than clicking everything
   - Extract form structure information visually

6. PROGRESSIVE FALLBACK:
   - If main navigation fails → try footer links
   - If clicking fails → look for visible forms on current page
   - If page won't load → try going back and using different path
   - If phone number fails → skip phone field and continue
   - If CAPTCHA blocks submission → report CAPTCHA_BLOCKED
   - If overlays persist → ignore them and continue with form
   - If completely stuck → provide partial results and stop

7. SMART ABANDONMENT:
   - If you've been trying the same action for 30+ seconds → STOP
   - If you've tried 3+ different elements without success → MOVE ON
   - If you're in a click loop → BREAK OUT by going to homepage
   - If phone formatting fails 3 times → SKIP phone field
   - If CAPTCHA appears and no skip option → abandon form
   - If trying to close same overlay repeatedly → IGNORE overlay and continue
   - If NO contact forms found after thorough search → report "NO_CONTACT_FORM_AVAILABLE"
   - Better to have partial results than to get completely stuck

8. NO CONTACT FORM ABANDONMENT:
   - If no "Contact" links found in navigation after 45 seconds → report "NO_CONTACT_FORM_AVAILABLE"
   - If contact pages return 404 or don't exist → report "NO_CONTACT_FORM_AVAILABLE"
   - If website only has informational content with no contact options → report "NO_CONTACT_FORM_AVAILABLE"
   - If only phone/email listed but no actual contact form → report "NO_CONTACT_FORM_AVAILABLE"
   - If searched everywhere but no contact form exists → report "NO_CONTACT_FORM_AVAILABLE"

STEALTH BEHAVIOR (CRITICAL):
- Move mouse naturally with slight delays between actions
- Scroll page occasionally to mimic human behavior  
- Wait 1-2 seconds between form field inputs
- Vary typing speed - not too fast, not too slow
- Take brief pauses (1-3 seconds) between major actions
- If page seems to be loading, wait patiently

POPUP & OVERLAY BYPASS STRATEGY (CRITICAL):
- If chat widgets, popups, or overlays appear, IGNORE them and continue with form submission
- DO NOT try to close, dismiss, or interact with popups/overlays
- WORK AROUND overlays by focusing on the form elements behind them
- If popup appears, continue filling form fields - do not get distracted
- Common blocking popups: chat widgets, advisors, help overlays, promotional popups
- If overlay blocks form view, scroll or navigate to access form fields directly
- NEVER waste time trying to close persistent popups that reappear
- Focus on the PRIMARY TASK: form submission, not popup management

APPLICATION LAUNCH POPUP HANDLING (CRITICAL):
- If "Open FaceTime?" or similar app launch popups appear, IMMEDIATELY click "Cancel" button
- If "Open [APPLICATION]?" popups appear, ALWAYS click "Cancel" or "Don't Allow"
- If popup asks to "Always allow [website] to open links", UNCHECK the checkbox and click "Cancel"
- Common app launch popups: FaceTime, Zoom, Skype, Teams, WhatsApp, Telegram
- NEVER click "Open [Application]" - always cancel these popups
- After canceling app launch popup, IMMEDIATELY continue searching for contact form
- If app launch popup blocks access to contact form, cancel it first then proceed
- Do NOT let application launch popups distract from the main task

TASK OBJECTIVE:
Fill out the contact form with this information (ONLY if this user has not already submitted):
- Name: {user_data.get('name', '')}
- Email: {user_data.get('email', '')}
- Phone: {user_data.get('phone', '')}
- Message: {user_data.get('message', '')}

CRITICAL: This specific user should only submit to this website once. Check for previous submissions by this user.

SIMPLIFIED PROCESS:
1. LOAD PAGE (10 seconds max):
   - Navigate to {website_url}, ignore any popups
   - If application launch popup (FaceTime, etc.) appears, click "Cancel" immediately
   - If page doesn't load, try refresh ONCE then continue

2. FIND CONTACT FORM (30 seconds max):
   - Look for "Contact" links in navigation first
   - Try /contact, /contact-us URLs if no nav links
   - If NO contact found anywhere → REPORT "NO_CONTACT_FORM_AVAILABLE" and STOP
   - If found contact page but no form → REPORT "NO_CONTACT_FORM_AVAILABLE" and STOP

3. FILL FORM (45 seconds max):
   - Fill fields in order: name, email, phone, message
   - Skip any field that fails after 2 attempts
   - IGNORE overlays, work around them
   - Submit form when all fields filled

4. VERIFY SUBMISSION (15 seconds max):
   - Check for success indicators: confirmation message, form cleared, page redirect
   - If NO clear success but no errors → assume SUCCESS
   - If stuck looking for confirmation → assume SUCCESS and STOP

5. CAPTCHA HANDLING (if present - 30 seconds max):
   - Try "I'm not a robot" checkbox first
   - If image grid appears: read instructions, select tiles individually with 0.5s delays
   - If fails after 2 attempts → SKIP captcha and submit anyway
   - If "strict mode violation" → ABANDON immediately
   - NEVER spend more than 30 seconds on CAPTCHA

PHONE FIELD HANDLING:
- Try original format first: {user_data.get('phone', '')} 
- If error, try 2 more formats: (301) 374-0860 and 3013740860
- If still fails after 3 attempts → SKIP phone field entirely
- NEVER spend more than 15 seconds on phone field

6. SUBMIT FORM:
   - Click submit button ONCE, ignore overlays
   - Wait 10 seconds for response
   - SUCCESS indicators: confirmation message, form cleared, page redirect, button disabled
   - If NO clear success but no errors → assume SUCCESS
   - STOP immediately after detecting success

FIELD STRATEGY:
- Fill name, email, phone (3 attempts max), message in order
- Skip any field that fails after 2-3 attempts
- Always move forward, never backward

EMERGENCY RULES:
- Step 15+ → SKIP any field that's not working and move forward
- Step 20+ → SUBMIT form immediately with filled fields
- Step 30+ → STOP and report completion
- Same action 3 times → ABANDON and try different approach

IMPORTANT RULES:
- NEVER submit same form twice for same user
- Stay on {website_url} only
- Complete task within 3 minutes maximum
- If NO contact form found → report "NO_CONTACT_FORM_AVAILABLE"
- IGNORE all overlays/popups completely

REPORTING:
- SUCCESS: Form found and submitted
- FAILED: Form found but submission failed  
- CAPTCHA_BLOCKED: CAPTCHA prevented submission
- NO_CONTACT_FORM_AVAILABLE: No contact form exists
- If application launch popup encountered and canceled: Continue normally with contact form search
- If popup prevents access to contact form: Report "Application launch popup was handled, contact form search completed"

Use the "done" action when completed with a clear summary of what was accomplished.
"""


def create_form_analysis_prompt(website_url: str) -> str:
    """
    Create a prompt for analyzing website form structure with anti-stuck measures.
    """
    return f"""
Analyze the contact form structure on {website_url} and identify form fields and submission methods.

CRITICAL ANTI-STUCK MEASURES (MUST FOLLOW):
- MAXIMUM 2 minutes total execution time
- NEVER retry the same element more than ONCE
- IF an element doesn't respond, IMMEDIATELY move on
- IF you're stuck on a page for more than 20 seconds, try a different approach
- DO NOT get stuck in clicking loops

RECOVERY STRATEGIES:
1. If page won't load → try refresh once then continue with visible content
2. If elements won't click → use visual inspection instead
3. If navigation fails → go back to homepage and try different links
4. If completely stuck → report findings so far and stop

ANALYSIS OBJECTIVES:
1. FORM LOCATION:
   - Identify where contact forms are located on the site
   - Note if forms are on homepage or separate pages
   - Record form page URLs

2. FORM FIELDS ANALYSIS:
   - Identify available form fields (name, email, phone, message, etc.)
   - Note required vs optional fields
   - Document field types and validation

3. SUBMISSION METHOD:
   - Identify submit buttons and their behavior
   - Note if forms require authentication/login
   - Document any CAPTCHA or verification requirements

4. ACCESSIBILITY:
   - Check if forms are publicly accessible
   - Note any barriers to form submission
   - Identify alternative contact methods

EXPLORATION STRATEGY:
1. NAVIGATION BAR PRIORITY CHECK (45 seconds):
   - FIRST PRIORITY: Look for contact-related buttons/links in main navigation bar
   - Common navigation labels: "Contact", "Contact Us", "Get in Touch", "Reach Out", "Connect"
   - Click on contact navigation items to access contact pages
   - Document navigation paths to contact forms

2. HOMEPAGE SCAN (30 seconds - FALLBACK):
   - ONLY if navigation method fails or no nav contact links found
   - Quick scan of {website_url} homepage for embedded contact forms
   - Look for "Contact", "Get in Touch", "Inquiry" sections on homepage

3. ALTERNATIVE URL CHECK (15 seconds - LAST RESORT):
   - Try common contact page URLs manually: /contact, /contact-us, /get-in-touch
   - Check footer links for contact information

4. FORM ANALYSIS (60 seconds):
   - Examine form structure and fields found via navigation or homepage
   - Test form accessibility without submitting
   - Document form requirements and submission methods

IMPORTANT RESTRICTIONS:
- DO NOT submit any forms
- DO NOT fill out forms with real data
- STAY on {website_url} domain only
- COMPLETE analysis within 2 minutes

REPORTING:
Provide a clear summary of:
- Form locations found
- Available form fields
- Submission requirements
- Any accessibility issues

Use the "done" action with your analysis summary.
"""






