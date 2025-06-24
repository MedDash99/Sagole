from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app import models, auth

# Use absolute imports starting from 'app'
from app.database import SessionLocal
from app.api import router as api_router # Import the router correctly
from app.dependencies import get_db
from app import db_manager

app = FastAPI(title="Sagole Database Admin Panel API")

# This line tells FastAPI to run our function when the application starts up
@app.on_event("startup")
def on_startup():
    print("Running startup tasks...")
    # Only call the seed function from your db_manager
    db_manager.seed_database() 
    print("Startup tasks complete.")

# CORS middleware to allow frontend requests
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sagole Admin API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Checks the database connection."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}
