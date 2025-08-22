"""
Configuration settings for Sol OS MVP
Environment variables and settings management
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-12345678901234567890123456789012")
    DATA_ENCRYPTION_MASTER_KEY: str = os.getenv("DATA_ENCRYPTION_MASTER_KEY", "dev-encryption-key-1234567890123456789012345678901234567890123456789012345678901234")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/sol_os_mvp.db")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Google Calendar API
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Application URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3001")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8004")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3001",
        "http://localhost:3000",
        "https://sol-os-mvp.com",  # Production domain when available
    ]
    
    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Google Calendar sync settings
    CALENDAR_SYNC_DAYS_AHEAD: int = 30
    CALENDAR_SYNC_INTERVAL_MINUTES: int = 15

settings = Settings()