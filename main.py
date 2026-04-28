from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from routes import auth, invoices, analytics
from models import Base
import uvicorn
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMARTINVOICE AI", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "SMARTINVOICE AI - Intelligent Invoice Automation"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
