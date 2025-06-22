from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

# Use absolute imports
from app.api import router as api_router
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Sagole Database Admin Panel API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sagole Admin API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        print(f"Database connection failed: {e}")
        return {"status": "error", "database": "disconnected", "detail": str(e)}
