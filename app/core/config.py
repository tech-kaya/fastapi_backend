import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # PostgreSQL Database Credentials (loaded from .env)
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432
    
    # Browser-use cloud API settings
    form_timeout: int = 300  # 5 minutes timeout for form operations
    max_retries: int = 3
    retry_delay: int = 5
    
    # Browser-use cloud API key (required)
    # Add this to your .env file:
    # BROWSER_USE_API_KEY=your_browser_use_api_key_here
    browser_use_api_key: Optional[str] = None
    
    # Browser-use API configuration
    llm_model: str = "gpt-4o"
    browser_viewport_width: int = 1366
    browser_viewport_height: int = 768
    use_adblock: bool = True
    highlight_elements: bool = False
    save_browser_data: bool = True
    max_agent_steps: int = 50
    headless: bool = False
    
    # Real-time monitoring settings
    show_agent_steps: bool = True  # Show real-time agent steps in logs
    poll_interval: int = 2  # Seconds between status checks
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual PostgreSQL credentials"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def setup_browser_use_env(self):
        """Set up environment variables for browser-use cloud API"""
        # Set cloud API key in environment if it exists
        if self.browser_use_api_key:
            os.environ["BROWSER_USE_API_KEY"] = self.browser_use_api_key
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Initialize settings
settings = Settings()

# Set up browser-use environment variables
settings.setup_browser_use_env() 