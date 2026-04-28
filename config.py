import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/smartinvoice")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-2024")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Services
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"

settings = Settings()
