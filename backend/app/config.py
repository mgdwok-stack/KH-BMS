"""
Configuration Management
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "Bid-Bot Clone")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bidbot:bidbot_password@localhost:5432/bidbot_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Keys
    PROCUREMENT_API_KEY: str = os.getenv("PROCUREMENT_API_KEY", "")
    PROCUREMENT_API_BASE_URL: str = os.getenv(
        "PROCUREMENT_API_BASE_URL",
        "http://apis.data.go.kr/1230000/ScsbidInfoService"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # ML Models
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    DNBP_MODEL_PATH: str = os.getenv("DNBP_MODEL_PATH", "./models/dnbp_model.h5")
    LSTM_MODEL_PATH: str = os.getenv("LSTM_MODEL_PATH", "./models/lstm_model.h5")
    ENSEMBLE_WEIGHTS: List[float] = [
        float(w) for w in os.getenv("ENSEMBLE_WEIGHTS", "0.6,0.4").split(",")
    ]
    
    # Data Collection
    DATA_COLLECTION_INTERVAL: int = int(os.getenv("DATA_COLLECTION_INTERVAL", "3600"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "200"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")

    class Config:
        case_sensitive = True


settings = Settings()
