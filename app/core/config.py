import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
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
    
    # CAPTCHA handling settings
    captcha_detection_enabled: bool = False  # Disable aggressive CAPTCHA detection
    captcha_loop_threshold: int = 20  # Increase from 5 to 20 consecutive CAPTCHA steps
    captcha_total_threshold: int = 30  # Increase from 10 to 30 total CAPTCHA steps
    captcha_skip_enabled: bool = False  # Don't skip websites with CAPTCHA protection

    # Browser Use Cloud proxy settings for automatic CAPTCHA solving
    use_proxy: bool = True  # Enable proxy for automatic CAPTCHA solving
    proxy_country_code: str = "us"  # Proxy country code (us, uk, ca, etc.)
    
    # Loop detection and prevention settings
    loop_detection_enabled: bool = True
    max_consecutive_same_action: int = 3  # Max times the same action can be repeated
    emergency_checkpoint_steps: int = 20  # Steps at which to trigger emergency checkpoint
    max_success_search_steps: int = 10  # Max steps to search for success indicators
    
    # Form submission optimization settings
    field_fill_timeout: int = 30  # Seconds to wait for field filling
    submit_retry_attempts: int = 2  # Number of times to retry submit button
    success_detection_timeout: int = 10  # Seconds to wait for success confirmation
    
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
    
    def get_browser_use_config(self) -> Dict[str, Any]:
        """Get browser-use configuration for API calls"""
        return {
            "llm_model": self.llm_model,
            "browser_viewport_width": self.browser_viewport_width,
            "browser_viewport_height": self.browser_viewport_height,
            "use_adblock": self.use_adblock,
            "highlight_elements": self.highlight_elements,
            "save_browser_data": self.save_browser_data,
            "max_agent_steps": self.max_agent_steps,
            "headless": self.headless,
            "use_proxy": self.use_proxy,
            "proxy_country_code": self.proxy_country_code,
            "captcha_detection_enabled": self.captcha_detection_enabled,
            "captcha_loop_threshold": self.captcha_loop_threshold,
            "captcha_total_threshold": self.captcha_total_threshold,
            "loop_detection_enabled": self.loop_detection_enabled,
            "max_consecutive_same_action": self.max_consecutive_same_action,
            "emergency_checkpoint_steps": self.emergency_checkpoint_steps,
            "max_success_search_steps": self.max_success_search_steps,
            "field_fill_timeout": self.field_fill_timeout,
            "submit_retry_attempts": self.submit_retry_attempts,
            "success_detection_timeout": self.success_detection_timeout
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Initialize settings
settings = Settings()

# Set up browser-use environment variables
settings.setup_browser_use_env() 