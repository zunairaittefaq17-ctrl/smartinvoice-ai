import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/smartinvoice")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
settings = Settings()
