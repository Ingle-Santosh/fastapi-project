import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    """Application settings and configuration"""
    
    # Application
    PROJECT_NAME: str = "Car Price Prediction API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security
    API_KEY: str = os.getenv("API_KEY", "demo-key")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/app.db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/models/model.joblib")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "1.0.0")
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"


# Create settings instance
settings = Settings()

# Validate critical settings on import
def validate_settings():
    """Validate critical configuration settings"""
    errors = []
    
    if settings.is_production():
        if settings.JWT_SECRET_KEY == "change-this-in-production":
            errors.append("❌ JWT_SECRET_KEY must be changed in production!")
        
        if settings.API_KEY == "demo-key":
            errors.append("❌ API_KEY must be changed in production!")
        
        if settings.DEBUG:
            errors.append("⚠️  DEBUG should be False in production!")
    
    if errors:
        print("\n🚨 Configuration Warnings:")
        for error in errors:
            print(f"  {error}")
        print()

# Run validation
validate_settings()