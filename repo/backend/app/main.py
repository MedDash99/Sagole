# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, MetaData

from app.api import router as api_router
from app.database import Base
from app import db_manager
from app import models  # This import is CRITICAL - it registers all models with Base.metadata
from app.config import settings

# --- Part 1: Setup that runs when the file is first loaded ---

print("--- Initializing application setup ---")

# In a multi-tenant setup where each environment has its own database and schema,
# we need to ensure that the schema and tables are created for each one.
for env, db_url in db_manager.DATABASE_URLS.items():
    print(f"Processing environment: '{env}'...")
    try:
        engine = create_engine(db_url)
        
        # Create the schema if it doesn't already exist.
        with engine.connect() as connection:
            print(f"  -> Ensuring schema '{env}' exists...")
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {env}"))
            connection.commit()
            print(f"  -> Schema '{env}' is ready.")

        # Create all tables for the current environment's schema.
        # We need to create a new metadata instance for each environment
        print(f"  -> Creating tables in schema '{env}'...")
        
        # Create a new metadata object to avoid conflicts between environments
        env_metadata = MetaData(schema=env)
        
        # Copy all tables from the base metadata to the environment-specific metadata
        for table in Base.metadata.tables.values():
            table.tometadata(env_metadata)
        
        # Create all tables with the environment-specific metadata
        env_metadata.create_all(bind=engine)
        print(f"  -> Tables for '{env}' created successfully.")

    except Exception as e:
        print(f"  -> ERROR processing environment '{env}': {e}")
        import traceback
        print(f"  -> Traceback: {traceback.format_exc()}")

print("--- Application setup finished ---")


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
    print("--- Running startup tasks ---")
    print("Seeding all configured databases...")
    for env in db_manager.DATABASE_URLS.keys():
        print(f"  -> Seeding environment: '{env}'")
        try:
            db_manager.seed_database(schema=env)
            print(f"  -> Seeding for '{env}' complete.")
        except Exception as e:
            print(f"  -> ERROR seeding environment '{env}': {e}")
    print("--- Startup tasks finished ---")

@app.get("/")
def read_root():
    return {"message": "Welcome! The Sagole Admin API is running."}
