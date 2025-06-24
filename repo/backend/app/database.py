import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# The schema to operate in (e.g. dev, test, etc.)
schema = os.environ.get('DB_SCHEMA', 'public')

# Use the DATABASE_URL from our settings
# Add connect_args to set the default schema
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"options": f"-csearch_path={schema}"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Attach the schema to the MetaData so every model automatically falls under it.
metadata = MetaData(schema=schema)

# Use a declarative base bound to the metadata with the default schema.
Base = declarative_base(metadata=metadata)