"""Application configuration settings."""

import os
from typing import Optional


class Settings:
    """Application settings configuration."""
    
    # Email Configuration (Optional - for alerts)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_ADDRESS: Optional[str] = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Note: This app uses Yahoo Finance (yfinance) which doesn't require API keys
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # File Paths
    USERS_FILE: str = os.getenv("USERS_FILE", "data/users.json")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate email settings if email functionality is needed."""
        # Email settings are optional - only validate if EMAIL_ADDRESS is provided
        if cls.EMAIL_ADDRESS:
            return cls.EMAIL_PASSWORD is not None
        return True  # Email functionality is optional


settings = Settings()
