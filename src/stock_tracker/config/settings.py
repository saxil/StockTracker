"""Application configuration settings."""

import os
from typing import Optional


class Settings:
    """Application settings configuration."""
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_ADDRESS: Optional[str] = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Stock API Configuration
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # File Paths
    USERS_FILE: str = os.getenv("USERS_FILE", "data/users.json")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present."""
        required_settings = [
            cls.EMAIL_ADDRESS,
            cls.EMAIL_PASSWORD,
        ]
        return all(setting is not None for setting in required_settings)


settings = Settings()
