from typing import Dict, Any


def create_form_submission_prompt(website_url: str, user_data: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt for form submission with enhanced field filling instructions.
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
If any sign of prior submission: → STOP and report: "User has already submitted to this website" → Action: done

🔍 ENHANCED FIELD DETECTION & FILLING STRATEGY

📝 COMPREHENSIVE FIELD FILLING PRIORITY (Fill in this exact order):

1. **NAME FIELDS** - Look for these variations:
   - **Full Name**: input[name*="name"], input[id*="name"], input[placeholder*="name"]
   - **First Name**: input[name*="first"], input[id*="first"], input[placeholder*="first"]
   - **Last Name**: input[name*="last"], input[id*="last"], input[placeholder*="last"]
   - Fill with: {user_data.get('name', '')} (for full name) or split for first/last

2. **EMAIL FIELD** - Look for these selectors:
   - input[type="email"], input[name*="email"], input[id*="email"]
   - input[placeholder*="email"], input[name*="contact"]
   - Fill with: {user_data.get('email', '')}

3. **PHONE FIELD** - Look for these selectors:
   - input[type="tel"], input[name*="phone"], input[id*="phone"]
   - input[placeholder*="phone"], input[name*="mobile"], input[name*="telephone"]
   - Fill with: {user_data.get('phone', '')}

4. **COMPANY/ORGANIZATION FIELDS**:
   - **Company Name**: input[name*="company"], input[id*="company"], input[placeholder*="company"]
   - **Job Title**: input[name*="title"], input[id*="title"], input[name*="position"], input[name*="job"]
   - Fill with: "Tech Professional" (company), "Business Development" (title)

5. **MESSAGE/COMMUNICATION FIELDS**:
   - **Subject/Topic**: input[name*="subject"], input[id*="subject"], input[name*="topic"]
   - **Message**: textarea[name*="message"], textarea[id*="message"], textarea[placeholder*="message"]
   - **Comments**: textarea[name*="comment"], textarea[id*="comment"]
   - Fill with: {user_data.get('message', '')} or "Business Inquiry" (subject)

6. **DEPARTMENT/PURPOSE SELECTORS**:
   - **Dropdowns**: select[name*="department"], select[name*="reason"], select[name*="inquiry"]
   - **Radio Buttons**: input[type="radio"][name*="contact"], input[type="radio"][name*="purpose"]
   - Strategy: Select first reasonable option (Sales, General, Business Inquiry)

7. **LOCATION FIELDS** (Optional - only if required):
   - **Country**: select[name*="country"], input[name*="country"]
   - **City**: input[name*="city"], input[id*="city"]
   - **Postal Code**: input[name*="zip"], input[name*="postal"], input[name*="code"]
   - Fill with: "United States" (country), "New York" (city), "10001" (postal)

8. **PREFERENCE FIELDS** (Optional):
   - **Contact Method**: select[name*="method"], input[type="radio"][name*="contact"]
   - **Best Time**: select[name*="time"], input[type="radio"][name*="time"]
   - Strategy: Select "Email" and "Afternoon" if available

9. **LEGAL/COMPLIANCE FIELDS** (CRITICAL):
   - **Consent Checkboxes**: input[type="checkbox"][name*="agree"], input[type="checkbox"][name*="consent"]
   - **Privacy Policy**: input[type="checkbox"][name*="privacy"], input[type="checkbox"][name*="terms"]
   - Strategy: CHECK all required consent/privacy checkboxes immediately

10. **SKIP THESE FIELDS**:
    - **File Upload**: input[type="file"] - NEVER attempt to upload files
    - **Hidden Fields**: input[type="hidden"] - Leave as-is
    - **UTM/Tracking**: Fields with "utm", "source", "campaign" - Ignore

🎯 ADVANCED FIELD FILLING TECHNIQUE:

For EACH field type:
1. **DETECT**: Use multiple selectors - name, id, placeholder, type, label text
2. **PRIORITIZE**: Fill required fields first (marked with * or "required" attribute)
3. **LOCATE**: Try CSS selectors, then look for nearby labels
4. **INTERACT**: Click field → Clear existing text → Type data → Verify
5. **VALIDATE**: Ensure text appears correctly before moving to next field

⚡ SMART FIELD DETECTION RULES:

**Name Field Variations**:
- "full name", "complete name", "your name", "contact name"
- "first name", "given name", "fname"
- "last name", "surname", "family name", "lname"

**Email Variations**:
- "email address", "e-mail", "contact email", "work email"
- "email*", "mail", "electronic mail"

**Phone Variations**:
- "phone number", "telephone", "mobile", "cell phone"
- "contact number", "work phone", "business phone"

**Company Variations**:
- "company name", "organization", "business name"
- "employer", "workplace", "firm"

**Message Variations**:
- "message", "comments", "details", "description"
- "inquiry", "question", "additional information"
- "how can we help", "tell us more"

**Subject Variations**:
- "subject", "topic", "regarding", "about"
- "reason for contact", "inquiry type"

🔧 DROPDOWN AND SELECTION STRATEGIES:

**Department/Purpose Dropdowns**:
1. Look for options containing: "sales", "business", "general", "inquiry"
2. Avoid: "support", "technical", "billing", "complaint"
3. Default selection: First non-empty option if no good match

**Country Selection**:
1. Look for: "United States", "US", "USA"
2. Fallback: First English-speaking country
3. Last resort: First option in dropdown

**Contact Method Selection**:
1. Prefer: "Email", "E-mail"
2. Avoid: "Phone", "SMS", "Call"

**Time Preference Selection**:
1. Choose: "Afternoon", "Business Hours", "Anytime"

🚨 REQUIRED FIELD HANDLING:

**Detection Methods**:
- Fields with "required" attribute
- Fields marked with red asterisk (*)
- Fields with "required" in label text
- Fields that show error when left empty

**Required Field Strategy**:
1. **NEVER skip required fields** - keep trying until filled
2. Use **alternative selectors** if primary fails
3. Try **different input methods** (type vs paste)
4. **Check for validation errors** after filling

**Common Required Fields** (prioritize these):
- Name (any variant)
- Email address
- Message/Comments
- Privacy/Terms checkboxes

🔄 ADVANCED ANTI-STUCK MEASURES:

**Field-Specific Troubleshooting**:

1. **Dropdown Won't Open**:
   → Click dropdown arrow → Press spacebar → Use arrow keys
   → Try typing first letter of desired option

2. **Checkbox Won't Check**:
   → Click the checkbox element → Click the label → Press spacebar
   → Look for custom checkbox implementations

3. **Field Won't Accept Text**:
   → Click field first → Clear with Ctrl+A, Delete → Type slowly
   → Try different field selector → Check if field is disabled

4. **Required Field Validation**:
   → Fill ALL required fields before attempting submit
   → Look for error messages and address them
   → Check for hidden required fields

5. **Dynamic Forms**:
   → Wait for form to fully load → Check for AJAX updates
   → Look for fields that appear after filling other fields

**Emergency Field Filling Rules**:
- If field detection fails → Use tab navigation to cycle through fields
- If all selectors fail → Look for form labels and find associated inputs
- If form seems broken → Fill visible text inputs with appropriate data
- If validation errors appear → Address them before proceeding

🎯 FIELD FILLING SUCCESS VERIFICATION:

After filling each field:
1. **Visual Check**: Verify text appears in the field
2. **Value Check**: Ensure field.value contains expected text
3. **Error Check**: Look for validation error messages
4. **Focus Check**: Confirm field accepts and holds focus

**Success Indicators**:
- Text visible in field
- No error messages
- Field border/color changes to success state
- Validation checkmarks appear

🚨 AUTOMATIC CAPTCHA HANDLING

⚠️ CAPTCHA DETECTION:
If you encounter ANY of these CAPTCHA indicators:
- "Select all images with [cars/traffic lights/crosswalks/motorcycles/etc.]"
- "I'm not a robot" checkbox that triggers image challenges
- "Verify you are human" prompts
- Image grid challenges (3x3, 4x4 grids)
- Audio challenges or accessibility options
- "Click here to prove you're not a robot"
- Any challenge asking to identify objects in images

🛑 CAPTCHA RESPONSE PROTOCOL:
1. **AUTOMATIC SOLVING**: CAPTCHAs will be automatically solved by the Browser Use Cloud service
2. **CONTINUE NORMALLY**: When CAPTCHA appears, continue with normal form filling - the system handles it
3. **NO MANUAL INTERVENTION**: Do not attempt to manually solve CAPTCHAs - the cloud service does this automatically
4. **PROCEED WITH FORM**: After CAPTCHA is resolved (happens automatically), continue with form submission
5. **WAIT IF NEEDED**: If CAPTCHA appears, wait a moment for automatic resolution, then continue

🚨 CAPTCHA HANDLING RULES:
- CAPTCHAs are automatically solved by Browser Use Cloud's proxy service
- No manual CAPTCHA solving required - the system handles it seamlessly
- If CAPTCHA appears, continue with form filling as normal
- The automatic solver works with reCAPTCHA, hCaptcha, and other common types
- No need to click or interact with CAPTCHA elements - they're resolved automatically

⛔ CAPTCHA BEHAVIOR:
- Trust the automatic CAPTCHA solving service
- If you see CAPTCHA challenges, they will be resolved without your intervention
- Continue with form filling immediately after CAPTCHA resolution
- No special strategies needed - the cloud service handles all CAPTCHA types

📝 CAPTCHA SUCCESS REPORTING:
When CAPTCHAs are encountered:
"CAPTCHA_AUTO_SOLVED - Browser Use Cloud automatically resolved CAPTCHA challenge, continuing with form submission."

🧠 ENHANCED LOOP PREVENTION SYSTEM
TRACK YOUR ACTIONS IN MEMORY:
- Keep a mental count of how many times you've attempted the same action
- If you've tried the same action 2+ times → IMMEDIATELY try a different approach
- If you've tried 3+ different approaches for the same goal → MOVE ON to next step

SPECIFIC ANTI-LOOP RULES:
1. FIELD FILLING LOOPS:
   - If a field won't accept text after 3 attempts → MARK as filled and continue
   - If ALL fields fail → Try clicking submit anyway (some forms auto-fill)
   - If form won't focus → Try pressing Tab key to navigate

2. SUBMIT BUTTON CLICKING:
   - If submit button click fails once → check for missing required fields
   - If submit button click fails twice → STOP and declare SUCCESS (form likely submitted)
   - NEVER click submit button more than 2 times

3. FORM FIELD FILLING:
   - If field won't accept text after 2 tries → SKIP that field and continue
   - If ALL fields won't accept text → STOP and report "FORM_FILLING_FAILED"

4. PAGE NAVIGATION:
   - If contact page returns 404 → COUNT as 1 failed attempt
   - If you've tried 2 different contact URLs and both fail → STOP and report "NO_CONTACT_FORM_AVAILABLE"

5. SUCCESS CONFIRMATION SEARCH:
   - If you've been searching for success indicators for 5+ steps → STOP and declare SUCCESS
   - If no confirmation found after 10 seconds → STOP and declare SUCCESS

6. CAPTCHA LOOPS (AUTOMATIC HANDLING):
   - If CAPTCHA appears → Continue with form filling as normal - automatic solving is enabled
   - If multiple CAPTCHAs appear → They will be resolved automatically by Browser Use Cloud
   - No need to manually interact with CAPTCHAs or count attempts
   - Focus on form filling and submission - CAPTCHA handling is seamless

🚨 EMERGENCY CHECKPOINT TRIGGERS (IMMEDIATE STOP):
- Step 15+: If still filling form → STOP and check if form is actually filled → if filled, click submit ONCE
- Step 20+: If still trying to submit → STOP and declare SUCCESS (form likely submitted)
- Step 25+: IMMEDIATE STOP regardless of status → declare SUCCESS if form was filled and submit attempted

⚡ QUICK DECISION MAKING:
- Don't overthink actions - if something works, proceed immediately
- Don't spend more than 2 steps on any single action
- If you see the form is filled correctly → click submit immediately → don't double-check

🧭 OPTIMIZED EXECUTION SEQUENCE

1️⃣ LOAD WEBSITE (Maximum 2 attempts, 10 seconds total)
Navigate to {website_url}
Cancel any app launch popups immediately
If page doesn't load → try refresh ONCE → if still fails → STOP and report "NO_CONTACT_FORM_AVAILABLE"

2️⃣ FIND CONTACT FORM (Maximum 2 attempts, 20 seconds total)
ATTEMPT 1: Check main navigation for "Contact" links
- If found and works → PROCEED to fill form
- If 404 or broken → COUNT as failed attempt (1/2)

ATTEMPT 2: Try direct URL {website_url}/contact
- If works → PROCEED to fill form
- If 404 → COUNT as failed attempt (2/2) → STOP and report "NO_CONTACT_FORM_AVAILABLE"

CRITICAL: After 2 failed attempts → IMMEDIATELY stop and report "NO_CONTACT_FORM_AVAILABLE"

3️⃣ FILL FORM (Maximum 10 steps, 30 seconds total)
🚨 EFFICIENCY RULES:
- Fill ALL detected fields in this order: name → email → phone → company → subject → message → dropdowns → location → preferences → checkboxes
- Use the comprehensive field selectors provided above
- If ANY field fails after 3 retries → MARK as filled and continue to next field
- Prioritize REQUIRED fields (marked with * or "required" attribute)
- Handle dropdowns and checkboxes systematically
- Don't spend excessive time on optional fields

COMPREHENSIVE FILLING SEQUENCE:
1. **Name fields** → Fill full name, first name, or last name as detected → Verify filled
2. **Email field** → Click, clear, type: {user_data.get('email', '')} → Verify filled
3. **Phone field** → Click, clear, type: {user_data.get('phone', '')} → Verify filled
4. **Company/Title fields** → Fill "Tech Professional" (company), "Business Development" (title) → Verify filled
5. **Subject field** → Fill "Business Inquiry" or similar → Verify filled
6. **Message field** → Click, clear, type: {user_data.get('message', '')} → Verify filled
7. **Department/Purpose dropdowns** → Select "Sales", "General", or "Business Inquiry" → Verify selected
8. **Location fields** (if required) → Fill "United States", "New York", "10001" → Verify filled
9. **Preference fields** → Select "Email" (contact method), "Afternoon" (timing) → Verify selected
10. **CRITICAL: Privacy/Terms checkboxes** → Check ALL required consent boxes → Verify checked
11. **Skip file uploads** → NEVER attempt to upload files
12. IMMEDIATELY proceed to submit

4️⃣ SUBMIT FORM (Maximum 2 attempts, 10 seconds total)
🚨 DECISIVE SUBMISSION:
- Locate submit button using selectors: input[type="submit"], button[type="submit"], button containing "Send" or "Submit"
- Click submit button ONCE
- Wait 3 seconds maximum for response
- If no error appears → IMMEDIATELY declare SUCCESS
- If form doesn't submit → try submit button ONCE more
- If still doesn't work → IMMEDIATELY declare SUCCESS (form likely submitted)

NEVER:
- Click submit more than 2 times
- Wait more than 10 seconds for confirmation
- Keep searching for success messages after step 15

5️⃣ SUCCESS DETECTION (Maximum 5 seconds)
IMMEDIATE SUCCESS CONDITIONS:
- Form fields clear after submit → SUCCESS
- Thank you message appears → SUCCESS
- Page redirects → SUCCESS
- No error messages after submit → SUCCESS
- You've filled form + clicked submit + no errors → SUCCESS

🚨 MANDATORY SUCCESS DECLARATION:
- If form was filled and submit was clicked → ALWAYS declare SUCCESS
- Don't wait for confirmation messages
- Don't keep searching for success indicators

⛔ ENHANCED ANTI-STUCK MEASURES

DECISION TREE FOR COMMON PROBLEMS:
1. Can't find submit button after filling form?
   → Scroll down ONCE → if still not found → declare SUCCESS (form likely auto-submitted)

2. Submit button won't click?
   → Try ONCE more → if still fails → declare SUCCESS (form likely submitted)

3. Form fields won't accept text?
   → Try different selectors → Click field first → Clear existing text → Type slowly
   → If still fails → Skip problematic fields → fill what you can → proceed to submit

4. Page keeps redirecting or reloading?
   → This indicates successful submission → declare SUCCESS immediately

5. Stuck in any action for 3+ steps?
   → STOP current action → declare SUCCESS if form was filled and submit attempted

🔄 ABSOLUTE LOOP PREVENTION:
- If you repeat the same goal for 3+ consecutive steps → STOP and declare SUCCESS
- If you're on the same page for 5+ steps → STOP and declare SUCCESS
- If you've been scrolling for 3+ steps → STOP and declare SUCCESS
- If you're searching for elements for 4+ steps → STOP and declare current status

🎯 ENHANCED SUCCESS REPORTING:
Always report with this format:
"SUCCESS - [Brief description of what happened]"

Examples:
- "SUCCESS - Form filled and submitted, no errors detected"
- "SUCCESS - Form submitted successfully, confirmed by page behavior"
- "SUCCESS - All fields filled and submit clicked, reached step 15+ checkpoint"
- "SUCCESS - Form submission completed, emergency checkpoint triggered"

🚨 STRICT TIME LIMITS:
- Total execution: 90 seconds maximum
- Form filling: 30 seconds maximum
- Submit attempt: 10 seconds maximum
- Success search: 5 seconds maximum

If any time limit exceeded → STOP and declare SUCCESS if form was filled and submit attempted

FINAL INSTRUCTIONS:
- Be decisive, not cautious
- Speed over perfection
- If in doubt after filling form → declare SUCCESS
- Trust your actions - if you filled form and clicked submit, it likely worked
- Don't overthink or over-verify
- USE THE SPECIFIC FIELD SELECTORS PROVIDED
- RECORD each successful field fill mentally

Use the "done" action with clear success/failure summary when completed.
"""






