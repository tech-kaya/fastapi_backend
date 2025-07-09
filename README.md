# Contact Form Automation API

A FastAPI application that automatically fills out contact forms on websites. Just give it a website URL and your contact details, and it will find the contact form and submit it for you using AI.

## 🎯 What This Does

This app helps you:
- **Auto-fill contact forms**: AI finds and fills contact forms on any website
- **Watch it work**: See real-time logs of what the AI is doing
- **Handle multiple websites**: Submit forms to many websites at once
- **Prevent duplicates**: Won't submit the same form twice
- **Smart detection**: Knows when a form was successfully submitted
- **Easy to use**: Simple REST API with clear endpoints

## 🚀 Getting Started

### What You Need

- Python 3.11+
- PostgreSQL database
- Browser-use API key (for the AI agent)

### Setup Steps

1. **Download the code**
   ```bash
   git clone <your-repo-url>
   cd fastapi_backend
   ```

2. **Install Python packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your environment file**
   ```bash
   cp .env.template .env
   # Edit .env with your database info and API key
   ```

4. **Add your API key**
   ```bash
   # Add this line to your .env file:
   BROWSER_USE_API_KEY=your_api_key_here
   ```

5. **Start the app**
   ```bash
   uvicorn app.main:app --reload
   ```

**Where to find things:**
- **API**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`

## 📁 How It's Organized

```
app/
├── api/routes/          # API endpoints (the URLs you call)
├── core/                # Settings and configuration  
├── db/                  # Database stuff (models, connections)
├── services/            # The main logic (AI agent, form submission)
├── utils/               # Helper functions
└── main.py              # Starts the application
```

## 🗄️ Database Tables

**places** - Websites to visit
- `name`: Company name
- `website`: Website URL

**users** - Contact information to submit
- `first_name`, `last_name`: Your name
- `email`: Your email
- `phone`: Your phone (optional)

**form_submission** - Track what happened
- `submission_status`: success/failed/skipped
- `error_message`: What went wrong (if anything)
- `submitted_at`: When it happened

## 🔧 How to Use It

### Main Functions

- `POST /api/v1/submit-forms` - Submit to all websites
- `POST /api/v1/submit-single-form/{place_id}` - Submit to one website
- `GET /api/v1/submission-status` - See how many succeeded/failed
- `GET /api/v1/submissions` - List all submissions

### Step by Step

**1. Start the app**
```bash
uvicorn app.main:app --reload
```

**2. Add a website**
```bash
curl -X POST "http://localhost:8000/api/v1/places" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Company",
    "website": "https://example.com"
  }'
```

**3. Add your contact info**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john@example.com",
    "phone": "+1234567890"
  }'
```

**4. Submit forms**
```bash
# Submit to all websites
curl -X POST "http://localhost:8000/api/v1/submit-forms"

# Or submit to just one website
curl -X POST "http://localhost:8000/api/v1/submit-single-form/1?user_id=1"
```

**💡 Tip**: Watch the console logs to see what the AI is doing in real-time!

**5. Check results**
```bash
# See summary
curl "http://localhost:8000/api/v1/submission-status"

# See details
curl "http://localhost:8000/api/v1/submissions"
```

## ⚙️ Settings

Put these in your `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/contact_forms

# AI Agent (Required)
BROWSER_USE_API_KEY=your_api_key_here

# Optional Settings
MAX_AGENT_STEPS=30          # How many steps before giving up
FORM_TIMEOUT=120            # Seconds to wait
SHOW_AGENT_STEPS=true       # Show what AI is doing
HEADLESS=false              # Show browser window (true to hide)
```

## 🎯 Cool Features

### Smart AI Agent
- **Finds forms automatically**: No need to tell it where the contact form is
- **Fills forms intelligently**: Knows which field is for name, email, etc.
- **Handles different websites**: Works with most contact form designs
- **Never gets stuck**: Has smart rules to prevent infinite loops

### What You See
Watch the AI work in real-time:
```
🤖 Agent Step: Finding contact form on homepage...
🤖 Agent Step: Found contact form, filling name field...
🤖 Agent Step: Filling email field...
🤖 Agent Step: Clicking submit button...
✅ Success: Form submitted successfully!
```

### Smart Success Detection
The AI knows a form was submitted successfully when:
- Thank you message appears
- Page redirects to success page
- Form fields get cleared
- No error messages after clicking submit

### Prevents Problems
- **No duplicates**: Won't submit to the same website twice
- **No infinite loops**: Stops if it gets stuck and tries something else
- **Handles errors**: Keeps going even if one website fails
- **Clear logging**: Easy to see what went wrong

## 🔍 Watching What Happens

### Real-time Logs
The app shows you exactly what the AI is doing:
- Which website it's visiting
- What form fields it found
- What it's typing in each field
- Whether the submission worked

### Results Tracking
Check your results anytime:
- How many forms submitted successfully
- Which websites had problems
- What errors occurred
- When everything happened

## 🚀 Running It

### Simple Way (Development)
```bash
uvicorn app.main:app --reload
```

### Docker Way
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🛠️ Common Settings

**For testing/development:**
```env
SHOW_AGENT_STEPS=true
HEADLESS=false
MAX_AGENT_STEPS=25
```

**For running lots of forms:**
```env
SHOW_AGENT_STEPS=false
HEADLESS=true
MAX_AGENT_STEPS=20
```

## 🐛 If Something Goes Wrong

**"No structured output" error**
- The app handles this automatically with backup methods
- Check the logs to see which method worked

**AI gets stuck in loops**
- Built-in protection stops infinite loops
- AI will give up and try a different approach after a few attempts

**Database errors**
- Make sure PostgreSQL is running
- Check your DATABASE_URL in .env file

**Forms not submitting**
- Some websites have complex forms or CAPTCHAs
- Check the logs to see what the AI tried
- The AI might mark it as "skipped" if no form was found

## 💡 Tips for Better Results

1. **Start small**: Try one website first to make sure everything works
2. **Watch the logs**: They show you exactly what's happening
3. **Check your data**: Make sure email addresses are valid
4. **Be patient**: Complex websites might take longer
5. **Test your API key**: Make sure it's working with browser-use

## 🤝 Contributing

Want to help improve this? Here's how:
1. Keep the code simple and well-commented
2. Add helpful log messages so people can see what's happening
3. Test with different types of websites
4. Update this README if you add new features

## 📄 License

MIT License - feel free to use this however you want! # Force deployment Wed Jul  9 20:32:24 PKT 2025
