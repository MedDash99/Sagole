from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, Table, MetaData

# Use relative imports
from .database import engine, SessionLocal
from . import models, schemas

def get_all_table_names() -> list[str]:
    inspector = inspect(engine)
    return [name for name in inspector.get_table_names() if name != 'alembic_version']

def get_table_data(table_name: str, limit: int = 20, offset: int = 0) -> list[dict]:
    with engine.connect() as connection:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        query = text(f"SELECT * FROM {table.name} LIMIT :limit OFFSET :offset")
        result = connection.execute(query, {"limit": limit, "offset": offset})
        rows = [dict(row) for row in result.mappings()]
        return rows

def seed_database():
    db = SessionLocal()
    try:
        if db.query(models.User).count() > 0:
            return {"message": "Database already seeded."}
        
        admin_user = models.User(username='admin', email='admin@example.com', full_name='Admin User', password='admin_password', role='admin')
        regular_user = models.User(username='testuser', email='test@example.com', full_name='Test User', password='test_password', role='regular_user')
        
        db.add_all([admin_user, regular_user])
        db.commit()
        return {"message": "Database seeded successfully with 2 users."}
    finally:
        db.close()

def create_change_request(db: Session, change_data: schemas.ChangeRequest):
    """Creates a new entry in the pending_changes table."""
    new_change = models.PendingChange(
        table_name=change_data.table_name,
        record_id=change_data.record_id,
        old_values=change_data.old_values,
        new_values=change_data.new_values,
        submitted_by="admin" # Placeholder for user auth
    )
    db.add(new_change)
    db.commit()
    db.refresh(new_change)
    return new_change
