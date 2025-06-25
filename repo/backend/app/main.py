# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text # We need this to execute raw SQL

from app.api import router as api_router
from app.database import engine, Base
from app import db_manager
from app import models 

# --- Part 1: Setup that runs when the file is first loaded ---

print("Ensuring 'dev' schema and database tables exist...")
with engine.connect() as connection:
    # Create the 'dev' schema if it doesn't already exist
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS dev"))
    connection.commit() # Commit the transaction

# Create all tables (they will be created in the 'dev' schema as configured in models)
print("Creating database tables in 'dev' schema...")
Base.metadata.create_all(bind=engine)
print("Table check complete.")


# --- Part 2: Application Configuration ---
app = FastAPI(title="Sagole Database Admin Panel API")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


# --- Part 3: Events and Basic Routes ---
@app.on_event("startup")
def on_startup():
    print("Server startup event: Seeding database...")
    db_manager.seed_database()
    print("Database seeding complete. Application is ready.")

@app.get("/")
def read_root():
    return {"message": "Welcome! The Sagole Admin API is running."}
