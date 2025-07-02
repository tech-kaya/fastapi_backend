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
    
    # Browser-use Settings (for UI visibility)
    # Set HEADLESS=false in .env to show browser UI
    headless: bool = False  # Default to show UI for monitoring
    form_timeout: int = 180  # Increased timeout for form operations (3 minutes)
    max_retries: int = 3
    retry_delay: int = 5
    
    # Logging
    log_level: str = "INFO"
    
    # LLM API Keys (at least one required for browser-use)
    # Add these to your .env file:
    # OPENAI_API_KEY=your_openai_key_here
    # ANTHROPIC_API_KEY=your_anthropic_key_here
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Browser-use UI Settings (optional)
    browser_use_ui: bool = True
    browser_use_ui_port: int = 7788
    browser_use_ui_host: str = "127.0.0.1"
    
    # Legacy browser settings (kept for compatibility)
    browser_headless: bool = False  # Show browser UI for monitoring
    
    # Stealth Mode & Anti-Detection Settings
    stealth_mode: bool = True  # Enable stealth mode to avoid bot detection
    use_random_user_agent: bool = True  # Randomize user agent
    human_delays: bool = True  # Add human-like delays between actions
    disable_webdriver_flags: bool = True  # Hide webdriver automation flags
    randomize_viewport: bool = True  # Randomize browser viewport size
    enable_plugins: bool = True  # Enable browser plugins to appear more human
    captcha_timeout: int = 120  # Maximum time to spend on CAPTCHA (2 minutes)
    captcha_max_attempts: int = 2  # Maximum CAPTCHA solve attempts before abandoning
    
    # Anti-Bot Evasion Settings
    max_redirects: int = 10  # Maximum page redirects to follow
    page_load_timeout: int = 30  # Maximum time to wait for page loads
    element_timeout: int = 10  # Maximum time to wait for elements
    human_typing_speed: bool = True  # Type at human-like speeds
    scroll_behavior: bool = True  # Add natural scrolling behavior
    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual PostgreSQL credentials"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def setup_browser_use_env(self):
        """Set up environment variables for browser-use"""
        # Set headless mode for browser-use
        os.environ["HEADLESS"] = str(self.headless).lower()
        
        # Set display for browser UI (helps with GUI display)
        if not self.headless and "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0"
        
        # Set API keys in environment if they exist
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        if self.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_api_key
        
        # Configure stealth mode settings
        if self.stealth_mode:
            os.environ["STEALTH_MODE"] = "true"
            os.environ["DISABLE_BLINK_FEATURES"] = "AutomationControlled"
            os.environ["HIDE_WEBDRIVER"] = str(self.disable_webdriver_flags).lower()
            
        # Configure user agent settings
        if self.use_random_user_agent:
            os.environ["RANDOMIZE_USER_AGENT"] = "true"
            # Set a default realistic user agent
            os.environ["USER_AGENT"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Configure human behavior settings
        if self.human_delays:
            os.environ["HUMAN_DELAYS"] = "true"
            os.environ["HUMAN_TYPING_SPEED"] = str(self.human_typing_speed).lower()
            
        if self.randomize_viewport:
            os.environ["RANDOMIZE_VIEWPORT"] = "true"
            os.environ["VIEWPORT_SIZE"] = "1366x768,1920x1080,1440x900"  # Common resolutions
            
        if self.scroll_behavior:
            os.environ["NATURAL_SCROLLING"] = "true"
        
        # Configure timeouts
        os.environ["PAGE_LOAD_TIMEOUT"] = str(self.page_load_timeout)
        os.environ["ELEMENT_TIMEOUT"] = str(self.element_timeout)
        os.environ["CAPTCHA_TIMEOUT"] = str(self.captcha_timeout)
        
        # Additional anti-detection measures
        os.environ["DISABLE_FEATURES"] = "VizDisplayCompositor"
        os.environ["DISABLE_WEB_SECURITY"] = "false"
        os.environ["ENABLE_PLUGINS"] = str(self.enable_plugins).lower()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Initialize settings
settings = Settings()

# Set up browser-use environment variables
settings.setup_browser_use_env() 