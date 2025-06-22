from sqlalchemy import inspect, text, Table, MetaData
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
# Import the User model
from .models import User

def get_all_table_names() -> list[str]:
    """
    Inspects the database and returns a list of all table names.
    """
    inspector = inspect(engine)
    return [name for name in inspector.get_table_names() if name != 'alembic_version']

def get_table_data(table_name: str, limit: int = 20, offset: int = 0) -> list[dict]:
    """
    Fetches rows from a specified table with pagination.
    """
    with engine.connect() as connection:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        query = text(f"SELECT * FROM {table.name} LIMIT :limit OFFSET :offset")
        result = connection.execute(query, {"limit": limit, "offset": offset})
        rows = [dict(row) for row in result.mappings()]
        return rows

# --- Add the new function below ---

def seed_database():
    """
    Adds initial data to the database if it's empty.
    Returns a message indicating what was done.
    """
    db = SessionLocal()
    try:
        # Check if the users table is empty
        user_count = db.query(User).count()
        if user_count > 0:
            return {"message": "Database already seeded."}

        # Create sample users
        admin_user = User(
            username='admin',
            email='admin@example.com',
            full_name='Admin User',
            password='admin_password', # In a real app, hash this!
            role='admin'
        )
        regular_user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            password='test_password',
            role='regular_user'
        )
        
        db.add(admin_user)
        db.add(regular_user)
        db.commit()
        
        return {"message": "Database seeded successfully with 2 users."}
    finally:
        db.close()
