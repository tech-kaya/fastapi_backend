from typing import Dict, Any


def create_form_submission_prompt(website_url: str, user_data: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt for form submission with anti-stuck measures.
    """
    return f"""
✅ OBJECTIVE: Submit Contact Form at {website_url} (ONLY ONCE per User)
USER DETAILS (DO NOT DUPLICATE):

Name: {user_data.get('name', '')}

Email: {user_data.get('email', '')}

Phone: {user_data.get('phone', '')}

Message: {user_data.get('message', '')}

🛑 CRITICAL DUPLICATE PREVENTION
Before filling anything:

Check if this user/email has already submitted (look for thank-you messages, confirmation texts, or disabled forms).

If any sign of prior submission:
→ STOP and report: "User has already submitted to this website"
→ Action: done

🧠 CONTACT FORM SEARCH MEMORY SYSTEM
Keep track of failed contact form searches to prevent infinite loops:

FAILED ATTEMPT TRACKING:
- 404 errors on contact pages = 1 failed attempt
- "Contact" navigation links that don't work = 1 failed attempt  
- Contact pages with no actual forms = 1 failed attempt
- Any dead-end contact search = 1 failed attempt

STOP RULE:
- After 2-3 failed contact form search attempts → IMMEDIATELY report "NO_CONTACT_FORM_AVAILABLE"
- DO NOT keep trying the same approaches repeatedly
- DO NOT go back to homepage after multiple failed contact searches
- DO NOT retry URLs that already returned 404 errors

SMART ABANDONMENT:
- If you've tried main nav contact links + direct URLs (/contact, /contact-us) and both failed → STOP
- If homepage has no contact forms and contact page is 404 → STOP  
- If you've searched for 60+ seconds with no contact form found → STOP
- If you're on step 15+ with no contact form progress → STOP and report "NO_CONTACT_FORM_AVAILABLE"

🧭 STEP-BY-STEP EXECUTION
🚨 CRITICAL SEQUENCE: FILL ALL FIELDS FIRST, THEN SUBMIT
1. Find contact form
2. Fill ALL basic fields (name, email, phone, message) + VERIFY they appear on page
3. Fill ALL required fields (checkboxes, math problems, dropdowns) + VERIFY they are set
4. LOOK at the page and confirm ALL fields show correct values
5. ONLY THEN click submit button
6. Wait for confirmation

🚨 MEMORY vs REALITY CHECK:
- Your memory might say "fields are filled" but the page might be empty
- ALWAYS trust what you SEE on the page, not what you remember doing
- If submit doesn't work, LOOK at the page first before trying again
- If you see empty fields on the page, fill them even if you think you already did

1️⃣ LOAD WEBSITE (10 seconds max)
Navigate to {website_url}

Cancel any app launch popups (FaceTime, Zoom, etc.) immediately

Ignore chat widgets, modals, popups — do not engage or try to close

If page doesn't load in 10s → refresh once
Still fails? → STOP and report "NO_CONTACT_FORM_AVAILABLE"

2️⃣ FIND CONTACT FORM (30 seconds max)
ATTEMPT 1: Main navigation → Look for: "Contact", "Get in Touch", "Let's Talk", etc.
- If nav contact link works and has form → PROCEED to fill form
- If nav contact link is 404 or broken → COUNT as failed attempt (1/3)

ATTEMPT 2: Direct URL testing → Try: {website_url}/contact
- If page loads with form → PROCEED to fill form  
- If 404 error or no form → COUNT as failed attempt (2/3)

ATTEMPT 3: Alternative URL → Try: {website_url}/contact-us
- If page loads with form → PROCEED to fill form
- If 404 error or no form → COUNT as failed attempt (3/3)

STOP CONDITIONS (CHECK AFTER EACH ATTEMPT):
- 2 failed attempts → IMMEDIATELY report "NO_CONTACT_FORM_AVAILABLE" and Action: done
- 3 failed attempts → IMMEDIATELY report "NO_CONTACT_FORM_AVAILABLE" and Action: done
- Any 404 errors + no homepage contact form → IMMEDIATELY report "NO_CONTACT_FORM_AVAILABLE" and Action: done
- DO NOT go back to homepage after failed contact searches
- DO NOT retry the same URLs multiple times

3️⃣ FILL FORM (45 seconds max)
🚨 CRITICAL: FILL ALL FIELDS FIRST - DO NOT SUBMIT UNTIL ALL FIELDS ARE COMPLETELY FILLED

STEP 1: Fill basic contact fields in EXACT order with verification:
1. Click name field → Input: {user_data.get('name', '')} → VERIFY text appears in field
2. Click email field → Input: {user_data.get('email', '')} → VERIFY text appears in field  
3. Click phone field → Input: {user_data.get('phone', '')} → VERIFY text appears in field
4. Click message field → Input: {user_data.get('message', '')} → VERIFY text appears in field

🚨 CRITICAL: After each field input, VISUALLY CONFIRM the text actually appears in the field on the page

STEP 2: Fill ALL other required fields with verification:
1. Find math problems → Calculate answer → Input answer → VERIFY answer appears in field
2. Find required checkboxes → CHECK them → VERIFY they become checked
3. Find dropdown menus → Select option → VERIFY selection is made
4. Find radio buttons → Select option → VERIFY selection is made

🚨 CRITICAL: After each action, VISUALLY CONFIRM the field actually changed on the page

STEP 3: FINAL VERIFICATION - Look at the actual page:
- VISUALLY CHECK that name field shows: {user_data.get('name', '')}
- VISUALLY CHECK that email field shows: {user_data.get('email', '')}
- VISUALLY CHECK that phone field shows: {user_data.get('phone', '')}
- VISUALLY CHECK that message field shows: {user_data.get('message', '')}
- VISUALLY CHECK that required checkboxes are checked
- VISUALLY CHECK that math problems are answered

🚨 IMPORTANT: DO NOT CLICK SUBMIT BUTTON until you can SEE all fields are filled on the actual page

🚨 IF FIELDS DON'T FILL PROPERLY:
- If you try to input text but the field remains empty → Try clicking the field first, then input
- If text doesn't appear after input → Try clearing the field and typing again
- If fields keep appearing empty → Try different input methods or skip that field
- DO NOT proceed to submit if you cannot see the text in the fields

🔲 REQUIRED FIELDS CHECK (CRITICAL):
🚨 COMPLETE THIS STEP BEFORE CLICKING SUBMIT - scan the ENTIRE form for ALL required fields:

CHECKBOX IDENTIFICATION & HANDLING:
- Look for checkboxes near text like: "I agree", "Terms", "Privacy", "Newsletter", "Accept", "Consent"
- Check for checkboxes marked with * or "required"
- Look for checkboxes with labels containing: "agree", "accept", "terms", "privacy", "policy", "consent"
- If checkbox is UNCHECKED → CLICK it to check it
- If checkbox is ALREADY CHECKED → leave it alone
- Check ALL visible checkboxes that seem required for form submission

MATH/CAPTCHA FIELDS:
- Look for math problems like "5+2=?" or "What is 3+4?"
- Calculate the answer and input the number
- Look for fields asking simple questions like "What is 7+0?" → input "7"

OTHER REQUIRED FIELDS:
- Radio buttons → Select first reasonable option
- Dropdown menus → Select relevant option (not "Select..." or blank)
- Any field marked with * or "required" → Fill it
- Text fields marked "required" → Fill with appropriate content

SUBMISSION VALIDATION CHECK:
🚨 ONLY if form doesn't submit after clicking submit button:
1. Look for error messages or red text indicating missing fields
2. Scan form again for any unchecked required checkboxes
3. Check for any empty required fields
4. Fill/check any missing required fields
5. Try submit again ONCE

🚨 REMEMBER: Fill ALL fields FIRST, then submit - not the other way around

SMART REQUIRED FIELD DETECTION:
- If submit button doesn't work → immediately scan for checkboxes
- If you see validation errors → look for checkbox requirements
- If form keeps asking for more info → check for unchecked boxes

4️⃣ CAPTCHA HANDLING (30 seconds max)
If "I'm not a robot" checkbox → click once

If grid challenge appears:

Try solving with 0.5s delay between tiles

Fails after 2 tries? → Skip captcha and attempt submission

If MATH PROBLEM appears:
- Simple math like "5+2=?" → calculate and input answer
- Questions like "What is 7+0?" → input "7"  
- "Enter the sum of 3+4" → input "7"
- Always input just the number, no extra text

Complex CAPTCHA blocks submission?
→ Report: "CAPTCHA_BLOCKED" and stop

5️⃣ SUBMIT FORM (ONLY AFTER VISUAL CONFIRMATION ALL FIELDS ARE FILLED)
🚨 CRITICAL: BEFORE CLICKING SUBMIT - LOOK AT THE ACTUAL PAGE:
- LOOK at name field → Confirm it contains: {user_data.get('name', '')}
- LOOK at email field → Confirm it contains: {user_data.get('email', '')}
- LOOK at phone field → Confirm it contains: {user_data.get('phone', '')}
- LOOK at message field → Confirm it contains: {user_data.get('message', '')}
- LOOK at checkboxes → Confirm they are checked (not unchecked)
- LOOK at math fields → Confirm they contain the correct answer

🚨 CRITICAL: If ANY field is empty or incorrect on the page → DO NOT SUBMIT → Go back and fix it

ONLY AFTER SEEING ALL FIELDS ARE CORRECTLY FILLED ON THE PAGE:
- Click submit button ONCE
- Wait up to 10s for confirmation (but STOP IMMEDIATELY if any success indicator detected)

⏰ DURING WAITING PERIOD:
- If form fields clear/become empty → STOP waiting, report SUCCESS
- If memory shows "form submitted successfully" → STOP waiting, report SUCCESS  
- If no errors appear for 10 seconds → STOP waiting, report SUCCESS
- DO NOT wait longer than 10 seconds for confirmation messages

🎯 SUCCESS DETECTION SYSTEM:

EXPLICIT SUCCESS INDICATORS:
- "Thank you" message or confirmation text
- Page redirect to thank-you/success page
- Form fields cleared after submission
- Submit button disabled/changed to "Submitted"
- Success notification or popup

MEMORY-BASED SUCCESS DETECTION:
- Form was filled completely and submit clicked without errors
- Page reloaded or refreshed after submission
- Contact form becomes "available again" (indicates previous submission)
- No validation errors appeared after clicking submit
- Browser stayed on same domain (didn't redirect to error page)
- Agent memory shows "Form submitted successfully" or similar
- Form fields became empty/cleared after submission (common success indicator)

CONTEXT CLUES FOR SUCCESS:
- Submit button was clicked successfully
- No error messages appeared for 5+ seconds after submission
- Form behavior changed (reset, disabled, or modified)
- URL parameters changed (often indicates form processing)
- Page content shifted or updated after submission

SMART SUCCESS DECISION:
- If ANY explicit success indicator → Report: "SUCCESS"
- If ALL fields VISUALLY confirmed filled + submit clicked + no errors for 10 seconds → Report: "SUCCESS"
- If memory indicates "contact form available again" → Report: "SUCCESS"
- If ALL fields were VISUALLY confirmed filled and submitted without validation errors → Report: "SUCCESS"
- If agent memory shows "Form submitted successfully" AND fields were VISUALLY confirmed filled → STOP WAITING and Report: "SUCCESS"
- If form fields cleared/became empty after submission → Report: "SUCCESS"

🛑 STOP WAITING CONDITIONS:
- If you've waited 10+ seconds after clicking submit → STOP and declare SUCCESS
- If memory shows "form submitted successfully" → STOP and declare SUCCESS immediately
- If form fields became empty after submission → STOP and declare SUCCESS immediately
- If no error messages appeared for 10+ seconds → STOP and declare SUCCESS
- If memory shows "form submission status is unclear" for 5+ steps → STOP and declare SUCCESS
- DO NOT wait indefinitely for confirmation messages
- DO NOT keep waiting if memory already indicates successful submission

ONLY report failure if:
- Clear error messages appeared
- Submit button failed to click
- Validation errors blocked submission
- CAPTCHA explicitly blocked submission

⛔ SMART ABANDONMENT & EMERGENCY TRIGGERS
Trigger STOP if any of these:

3+ clicks on same element → abandon that element

3+ scrolls to same position → move on

Submit button clicked 3+ times → STOP and report SUCCESS (form likely submitted)

Step 15+ → skip problematic fields

Step 20+ → EMERGENCY CHECKPOINT:
- If still trying to submit → STOP and LOOK at the actual page
- Check what fields are VISUALLY empty or incorrect on the page
- Fill ONLY the fields that are actually empty on the page
- Check ONLY the checkboxes that are actually unchecked on the page
- If page shows all fields filled correctly → declare SUCCESS and stop (form likely submitted)

Step 30+ or time > 3 mins → stop and summarize actions

🔁 LOOP/STUCK PREVENTION
DO NOT try same action 3x

DO NOT retry stuck phone/captcha fields

DO NOT try to close overlays/persistent modals

DO NOT retry failed contact form searches (remember: 2-3 failed attempts = STOP)

DO NOT go back to homepage after multiple failed contact searches

DO NOT click submit button more than 2 times → If first submit fails, check for required fields, fill them, then try submit once more

🚨 EMERGENCY LOOP DETECTION:
- If you've tried the same action 3+ times in a row → STOP that action
- If you're on step 15+ and still trying to submit → STOP and LOOK at the actual page to see if fields are really filled
- If you keep inputting the same value → STOP and VISUALLY CHECK if previous fields actually got filled
- If status remains "unclear" for 5+ steps → STOP and LOOK at the page to verify ALL fields before submitting
- If you clicked submit but form didn't work → LOOK at the page and check what's actually missing

🚨 FIELD REFILLING PREVENTION:
- If checkboxes are already checked → DO NOT click them again (this unchecks them)
- If fields already contain correct text → DO NOT refill them
- If math problems already have answers → DO NOT input again
- ONLY fill empty fields or fix incorrect fields

🚨 VISUAL CONFIRMATION REQUIRED:
- DO NOT trust your memory about field states
- ALWAYS look at the actual page to see current field values
- If you think fields are filled but submit doesn't work → LOOK at the page to see what's really there

If stuck for 30+ seconds → abandon step, move forward

If completely stuck anywhere → report partial status and stop

FINAL ACTIONS
✅ If form submitted (use SUCCESS DETECTION SYSTEM above):
→ Report "SUCCESS" with confirmation indicator or memory evidence

❌ If no form:
→ Report "NO_CONTACT_FORM_AVAILABLE"

🧱 CAPTCHA blocks:
→ Report "CAPTCHA_BLOCKED"

🔁 Duplicate found:
→ Report "User has already submitted to this website"

🎯 SUCCESS REPORTING EXAMPLES:
- "SUCCESS - Thank you message displayed after visually confirming all fields filled and submitting"
- "SUCCESS - All fields visually confirmed filled, form submitted successfully, no errors detected"
- "SUCCESS - Contact form available again after complete submission with visual field confirmation"
- "SUCCESS - All fields visually confirmed filled, form submitted, fields cleared and submit button disabled"
- "SUCCESS - All required fields visually confirmed filled and submitted without validation errors"
- "SUCCESS - All fields visually confirmed filled, agent memory shows form submitted successfully, no confirmation needed"
- "SUCCESS - All fields visually confirmed filled, form submitted, fields became empty after submission"
- "SUCCESS - All fields visually confirmed filled, submit button clicked successfully, waited 10 seconds with no errors"
- "SUCCESS - All fields visually confirmed filled, form submission status unclear but reached step 20+, assuming success"

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






