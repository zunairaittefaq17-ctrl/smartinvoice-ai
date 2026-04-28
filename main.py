import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from routes import auth, invoices, analytics

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 SmartInvoice AI Backend Starting...")
    logger.info(f"✅ Groq API Key loaded: {'YES' if settings.GROQ_API_KEY else 'NO'}")
    yield
    logger.info("🛑 Backend shutting down...")

app = FastAPI(
    title="SmartInvoice AI Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "https://*.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "groq_ready": bool(settings.GROQ_API_KEY)}

# Routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
