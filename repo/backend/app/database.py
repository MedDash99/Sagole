from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. We define the correct, hardcoded URL
SQLALCHEMY_DATABASE_URL = "postgresql://sagole_user:password@localhost/db"


# 2. We use that URL directly to create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. The rest of the setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session in your API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()