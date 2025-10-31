"""
Configuration settings for AI Rockfall Prediction System
=======================================================

Centralized configuration management using Pydantic settings.
Supports environment variables and validation.

Author: AI Rockfall Prediction Team
Date: October 26, 2025
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with validation."""

    # Application settings
    APP_NAME: str = "AI Rockfall Prediction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/rockfall_db",
        env="DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")

    # Redis settings
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # JWT settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )

    # File upload settings
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".csv", ".las", ".json", ".jpg", ".jpeg", ".png"],
        env="ALLOWED_EXTENSIONS"
    )

    # Analysis settings
    JUPYTER_KERNEL_TIMEOUT: int = Field(default=3600, env="JUPYTER_KERNEL_TIMEOUT")  # 1 hour
    MAX_CONCURRENT_ANALYSES: int = Field(default=3, env="MAX_CONCURRENT_ANALYSES")

    # External API settings
    WEATHER_API_KEY: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    EMAIL_API_KEY: Optional[str] = Field(default=None, env="EMAIL_API_KEY")

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default="logs/api.log", env="LOG_FILE")

    # Analysis directories (relative to project root)
    BASE_DIR: str = Field(default=os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    DATA_DIR: str = Field(default=os.path.join(BASE_DIR, "Data"))
    UPLOAD_BASE_DIR: str = Field(default=os.path.join(BASE_DIR, "Upload"))
    OUTPUT_DIR: str = Field(default=os.path.join(BASE_DIR, "backend", "outputs"))

    # Analysis module paths
    LIDAR_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "LiDAR_Rockfall_Prediction.ipynb"))
    GEOPHONE_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "Geophone_Rockfall_Prediction.ipynb"))
    PIEZOMETER_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "Piezometer_Landslide_Prediction.ipynb"))
    GBINSAR_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "GB_InSAR_Rockfall_Prediction.ipynb"))
    EXTENSOMETER_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "Extensometer_Analysis.ipynb"))
    WEATHER_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "Automatic_Weather_Station_Analysis.ipynb"))
    IMAGE_ANALYSIS: str = Field(default=os.path.join(BASE_DIR, "backend", "NewImageanalysis.ipynb"))

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE) if settings.LOG_FILE else "logs", exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)