import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Model Configuration
    FINBERT_MODEL = os.getenv("FINBERT_MODEL", "ProsusAI/finbert")
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./models/cache")
    FINE_TUNED_MODEL_DIR = os.getenv("FINE_TUNED_MODEL_DIR", "./models/fine_tuned")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_chatbot.db")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # External APIs
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Fine-tuning Configuration
    MAX_TRAINING_SAMPLES = int(os.getenv("MAX_TRAINING_SAMPLES", 10000))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", 2e-5))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))
    NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", 3))

settings = Settings()
