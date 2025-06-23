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

def get_table_schema(table_name: str) -> list[dict]:
    """Get the schema information for a specific table"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    schema = []
    
    for column in columns:
        schema.append({
            "name": column["name"],
            "type": str(column["type"]),
            "nullable": column["nullable"],
            "primary_key": column.get("primary_key", False),
            "default": column.get("default", None)
        })
    
    return schema

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

def get_pending_changes(db: Session):
    """Get all pending changes for approval"""
    changes = db.query(models.PendingChange).filter(
        models.PendingChange.status == "pending"
    ).all()
    return changes

def approve_change(db: Session, change_id: int):
    """Approve a pending change and apply it to the target table"""
    # Get the pending change
    change = db.query(models.PendingChange).filter(
        models.PendingChange.id == change_id
    ).first()
    
    if not change:
        raise ValueError(f"Change with id {change_id} not found")
    
    if change.status != models.ChangeStatus.PENDING:
        raise ValueError(f"Change {change_id} is not pending (current status: {change.status})")
    
    try:
        # Apply the change to the target table
        _apply_change_to_table(db, change)
        
        # Create a snapshot of the entire table state
        _create_table_snapshot(db, change.table_name, change_id)
        
        # Update the change status to approved
        change.status = models.ChangeStatus.APPROVED
        db.commit()
        
        return change
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to approve change: {str(e)}")

def reject_change(db: Session, change_id: int):
    """Reject a pending change"""
    change = db.query(models.PendingChange).filter(
        models.PendingChange.id == change_id
    ).first()
    
    if not change:
        raise ValueError(f"Change with id {change_id} not found")
    
    if change.status != models.ChangeStatus.PENDING:
        raise ValueError(f"Change {change_id} is not pending (current status: {change.status})")
    
    change.status = models.ChangeStatus.REJECTED
    db.commit()
    return change

def delete_record(db: Session, table_name: str, record_id: int):
    """Deletes a record from the specified table."""
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    primary_key_col = None
    for col in table.columns:
        if col.primary_key:
            primary_key_col = col
            break
    
    if primary_key_col is None:
        raise ValueError(f"No primary key found for table {table_name}")

    delete_stmt = table.delete().where(primary_key_col == record_id)
    
    result = db.execute(delete_stmt)
    
    if result.rowcount == 0:
        raise ValueError(f"No record found with id {record_id} in table {table_name}")
    
    db.commit()

def _apply_change_to_table(db: Session, change: models.PendingChange):
    """Apply the change to the actual table"""
    table_name = change.table_name
    new_values = change.new_values
    record_id = change.record_id
    
    # Get table metadata
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    
    if record_id is None:
        # This is a new record - INSERT
        insert_stmt = table.insert().values(**new_values)
        db.execute(insert_stmt)
    else:
        # This is an update to an existing record - UPDATE
        # Find the primary key column
        primary_key_col = None
        for col in table.columns:
            if col.primary_key:
                primary_key_col = col
                break
        
        if primary_key_col is None:
            raise ValueError(f"No primary key found for table {table_name}")
        
        update_stmt = table.update().where(
            primary_key_col == record_id
        ).values(**new_values)
        
        result = db.execute(update_stmt)
        if result.rowcount == 0:
            raise ValueError(f"No record found with id {record_id} in table {table_name}")

def _create_table_snapshot(db: Session, table_name: str, change_id: int):
    """Create a snapshot of the entire table state"""
    # Get all records from the table
    table_data = get_table_data(table_name, limit=10000)  # Get all records
    
    # Create a single snapshot record representing the entire table state
    snapshot = models.Snapshot(
        table_name=table_name,
        record_id=0,  # Use 0 to indicate this is a full table snapshot
        data={"table_snapshot": table_data},
        change_id=change_id
    )
    
    db.add(snapshot)
