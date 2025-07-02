# Contact Form Automation API

A production-ready FastAPI application that automates contact form submissions across websites using browser automation. The system visits websites stored in a PostgreSQL database, fills out contact forms using user data, and tracks submission results.

## 🎯 Overview

This application provides:
- **AI-Powered Form Automation**: Uses browser-use AI agents to intelligently fill and submit contact forms
- **Visual Browser Monitoring**: Real-time browser UI for watching automation in action
- **Bulk Processing**: Process all websites in the database with a single API call
- **Individual Submissions**: Submit forms for specific websites
- **Form Analysis**: Analyze website contact forms before automation
- **Multiple LLM Support**: Works with OpenAI, Anthropic, and other AI models
- **Comprehensive Logging**: Track submission status, errors, and success indicators
- **RESTful API**: Clean, documented endpoints for all operations
- **Production Ready**: Async/await, proper error handling, background tasks

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tech_kaya
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (required for browser-use)
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your database credentials and API keys
   ```

5. **Add LLM API Keys** (Required for browser-use agent)
   ```bash
   # Add to your .env file:
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

6. **Start the FastAPI backend**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Launch Browser-Use UI** (in a separate terminal)
   ```bash
   python browser_ui.py
   ```

**Access Points:**
- **FastAPI Backend**: `http://localhost:8000`
- **Browser-Use UI**: `http://localhost:7788` 
- **API Documentation**: `http://localhost:8000/docs`

**Note**: Database tables will be created automatically on first startup.

## 📁 Project Structure

```
app/
├── api/
│   └── routes/
│       └── form_submission.py    # API endpoints
├── core/
│   └── config.py                 # Configuration settings
├── db/
│   ├── models/
│   │   └── form_submission.py    # SQLAlchemy models
│   ├── schemas/
│   │   └── form_submission.py    # Pydantic schemas
│   ├── crud/
│   │   └── form_submission.py    # Database operations
│   └── session.py                # Database session setup
├── services/
│   ├── form_submitter.py         # Browser automation service
│   └── submission_workflow.py    # Orchestration logic
├── utils/
│   └── form_selectors.py         # CSS/XPath selectors
└── main.py                       # FastAPI application
```

## 🛠️ Database Schema

### Tables

**places**
- `id`: Primary key
- `name`: Website/business name
- `website_url`: URL to visit

**users**
- `id`: Primary key
- `name`: Contact name
- `email`: Contact email
- `phone`: Phone number (optional)
- `message`: Custom message (optional)

**form_submission**
- `id`: Primary key
- `place_id`: Foreign key to places
- `user_id`: Foreign key to users
- `website_url`: URL that was visited
- `submission_status`: success/failed/pending
- `error_message`: Error details if failed
- `submitted_at`: Timestamp

## 🔧 API Endpoints

### Core Operations

- `POST /api/v1/submit-forms` - Submit forms to all websites using AI agent
- `POST /api/v1/submit-single-form/{place_id}` - Submit form to specific website
- `POST /api/v1/analyze-form/{place_id}` - Analyze website contact form structure
- `GET /api/v1/submission-status` - Get submission statistics
- `GET /api/v1/submissions` - List all submissions
- `GET /api/v1/browser-ui-info` - Get browser-use UI connection info

### Data Management

- `GET /api/v1/places` - List all places
- `POST /api/v1/places` - Create new place
- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create new user

### System

- `GET /` - API information
- `GET /health` - Health check

## 📝 Usage Examples

### 1. Start the Application

```bash
# Terminal 1: Start FastAPI backend
uvicorn app.main:app --reload

# Terminal 2: Launch Browser-Use UI
python browser_ui.py
```

### 2. Add Places and Users

```bash
# Add a place
curl -X POST "http://localhost:8000/api/v1/places" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Company",
    "website_url": "https://example.com"
  }'

# Add a user
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "message": "I am interested in your services."
  }'
```

### 3. Submit Forms

```bash
# Submit to all places (watch in browser-use UI)
curl -X POST "http://localhost:8000/api/v1/submit-forms"

# Submit to specific place with specific user
curl -X POST "http://localhost:8000/api/v1/submit-single-form/1?user_id=1"

# Analyze a website's contact form structure
curl -X POST "http://localhost:8000/api/v1/analyze-form/1"
```

**💡 Pro Tip**: Keep the Browser-Use UI open at `http://localhost:7788` to watch the AI agent work in real-time!

### 4. Check Status

```bash
# Get submission statistics
curl "http://localhost:8000/api/v1/submission-status"

# Get recent submissions
curl "http://localhost:8000/api/v1/submissions?limit=10"
```

## ⚙️ Configuration

Environment variables in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/contact_forms
SECRET_KEY=your-super-secret-key
BROWSER_HEADLESS=true
FORM_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=5
LOG_LEVEL=INFO
```

## 🎯 Features

### AI-Powered Browser Automation
- **Intelligent Form Detection**: AI agent automatically finds and analyzes contact forms
- **Smart Field Mapping**: Uses AI to understand form fields and fill them appropriately
- **Adaptive Navigation**: AI can navigate complex websites to find contact pages
- **Visual Monitoring**: Real-time browser UI shows exactly what the AI is doing
- **Success Detection**: AI analyzes page content and URLs to verify successful submissions

### Error Handling & Retry Logic
- **Configurable Retries**: Automatic retry with exponential backoff
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Graceful Failures**: Continues processing even if individual submissions fail

### Performance & Scalability
- **Async Processing**: All operations use async/await for maximum performance
- **Background Tasks**: Form submissions run as background tasks
- **Database Optimization**: Efficient queries with proper indexing
- **Connection Pooling**: Optimized database connections

## 🔍 Monitoring & Debugging

### Logs
- Console output with colored formatting
- Configurable log levels

### Health Checks
- Database connectivity: `GET /health`
- Application status: `GET /`

## 🚀 Production Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🛡️ Security Considerations

- Environment-based configuration for sensitive data
- Input validation using Pydantic
- SQL injection protection with SQLAlchemy
- CORS middleware for API access control

## 🧪 Testing

The application includes comprehensive error handling and logging for easy debugging. Monitor the logs for:
- Form detection failures
- Field mapping issues
- Submission success/failure
- Network timeouts
- Database errors

## 📈 Performance Tips

1. **Batch Processing**: Use bulk submission endpoint for multiple sites
2. **User Data**: Prepare user data in advance to avoid repeated queries
3. **Browser Settings**: Adjust headless mode and timeouts based on your needs
4. **Database**: Use connection pooling and optimize queries for large datasets

## 🤝 Contributing

1. Follow the existing code structure
2. Use async/await for all I/O operations
3. Add proper error handling and logging
4. Update documentation for new features
5. Test thoroughly before submitting PRs

## 📄 License

This project is licensed under the MIT License. 