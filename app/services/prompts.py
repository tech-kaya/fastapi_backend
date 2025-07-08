from typing import Dict, Any


def create_form_submission_prompt(website_url: str, user_data: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt for form submission with enhanced anti-loop and success detection.
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

🧠 ENHANCED LOOP PREVENTION SYSTEM
TRACK YOUR ACTIONS IN MEMORY:
- Keep a mental count of how many times you've attempted the same action
- If you've tried the same action 2+ times → IMMEDIATELY try a different approach
- If you've tried 3+ different approaches for the same goal → MOVE ON to next step

SPECIFIC ANTI-LOOP RULES:
1. SUBMIT BUTTON CLICKING:
   - If submit button click fails once → check for missing required fields
   - If submit button click fails twice → STOP and declare SUCCESS (form likely submitted)
   - NEVER click submit button more than 2 times

2. FORM FIELD FILLING:
   - If field won't accept text after 2 tries → SKIP that field and continue
   - If ALL fields won't accept text → STOP and report "FORM_FILLING_FAILED"

3. PAGE NAVIGATION:
   - If contact page returns 404 → COUNT as 1 failed attempt
   - If you've tried 2 different contact URLs and both fail → STOP and report "NO_CONTACT_FORM_AVAILABLE"

4. SUCCESS CONFIRMATION SEARCH:
   - If you've been searching for success indicators for 5+ steps → STOP and declare SUCCESS
   - If no confirmation found after 10 seconds → STOP and declare SUCCESS

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
- Fill ALL fields quickly in sequence: name → email → phone → message
- Don't verify each field individually - trust your input
- If ANY field fails to accept text after 1 retry → SKIP it and continue
- Fill required checkboxes and dropdowns quickly
- Don't spend time on problematic fields

QUICK FILLING SEQUENCE:
1. Name field → Input: {user_data.get('name', '')}
2. Email field → Input: {user_data.get('email', '')}
3. Phone field → Input: {user_data.get('phone', '')}
4. Message field → Input: {user_data.get('message', '')}
5. Check any required checkboxes
6. Fill any math CAPTCHAs (calculate quickly)
7. IMMEDIATELY proceed to submit

4️⃣ SUBMIT FORM (Maximum 2 attempts, 10 seconds total)
🚨 DECISIVE SUBMISSION:
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
   → Skip problematic fields → fill what you can → proceed to submit

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

Use the "done" action with clear success/failure summary when completed.
"""






