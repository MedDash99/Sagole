from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, Table, MetaData
import json
from typing import Optional
import datetime
import decimal
from passlib.context import CryptContext
import os

# Use relative imports
from .database import engine, SessionLocal
from . import models, schemas, auth

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _make_record_serializable(record: Optional[dict]) -> Optional[dict]:
    """
    Recursively iterates through a dictionary and makes its values JSON serializable.
    Handles datetime, date, and Decimal objects.
    """
    if record is None:
        return None
    
    serializable_record = {}
    for key, value in record.items():
        if isinstance(value, (datetime.datetime, datetime.date)):
            serializable_record[key] = value.isoformat()
        elif isinstance(value, decimal.Decimal):
            serializable_record[key] = float(value)
        elif isinstance(value, dict):
            serializable_record[key] = _make_record_serializable(value)
        elif isinstance(value, list):
            serializable_record[key] = [_make_record_serializable(v) if isinstance(v, dict) else v for v in value]
        else:
            serializable_record[key] = value
            
    return serializable_record

def get_all_table_names() -> list[str]:
    inspector = inspect(engine)
    return [name for name in inspector.get_table_names() if name != 'alembic_version']

def get_table_data(
    table_name: str, 
    limit: int = 20, 
    offset: int = 0, 
    filters_json: Optional[str] = None
) -> list[dict]:
    with engine.connect() as connection:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        query = f"SELECT * FROM {table.name}"
        params = {"limit": limit, "offset": offset}
        
        if filters_json:
            try:
                filters = json.loads(filters_json)
                if filters:
                    where_clauses = []
                    for i, f in enumerate(filters):
                        # Basic validation
                        if not all(k in f for k in ['column', 'operator', 'value']):
                            continue
                        
                        column = f['column']
                        operator = f['operator']
                        value = f['value']
                        
                        # Prevent SQL injection by validating column and operator
                        if column not in [c.name for c in table.columns]:
                            continue
                        
                        allowed_operators = ['=', '!=', '>', '<', '>=', '<=', 'LIKE']
                        if operator not in allowed_operators:
                            continue
                        
                        param_name = f"value_{i}"
                        where_clauses.append(f"{column} {operator} :{param_name}")
                        params[param_name] = value
                    
                    if where_clauses:
                        query += " WHERE " + " AND ".join(where_clauses)
            except (json.JSONDecodeError, TypeError):
                # Ignore invalid JSON
                pass

        query += " LIMIT :limit OFFSET :offset"
        
        result = connection.execute(text(query), params)
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

def seed_database(schema: Optional[str] = None):
    if schema is None:
        schema = os.environ.get("DB_SCHEMA", "dev")

    db = SessionLocal()
    try:
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        db.commit()

        # Debugging: list tables
        inspector = inspect(engine)
        result = db.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"))
        print(f"Tables in schema {schema}: {[row[0] for row in result]}")

        # Check if the users table exists before trying to query it.
        if not inspector.has_table("users", schema=schema):
            print(f"Users table not found in schema '{schema}'. Skipping seeding. Migrations might be running.")
            return

        seed_data_for_schema = {
            "dev": {
                "users": [
                    {'username': 'admin_dev', 'email': 'admin.dev@example.com', 'full_name': 'Dev Admin', 'password_hash': pwd_context.hash('admin123'), 'role': 'admin'},
                    {'username': 'user_dev', 'email': 'user.dev@example.com', 'full_name': 'Dev User', 'password_hash': pwd_context.hash('user123'), 'role': 'user'},
                    {'username': 'guest_dev', 'email': 'guest.dev@example.com', 'full_name': 'Dev Guest', 'password_hash': pwd_context.hash('guest123'), 'role': 'guest'},
                ],
                "products": [
                    {'name': 'Laptop', 'description': 'A high-performance laptop for developers.', 'price': 1200.50, 'stock_quantity': 15, 'category': 'Electronics'},
                    {'name': 'Coffee Mug', 'description': 'A mug to hold your favorite beverage.', 'price': 15.00, 'stock_quantity': 150, 'category': 'Kitchenware'},
                    {'name': 'Desk Chair', 'description': 'An ergonomic chair for long hours of coding.', 'price': 350.75, 'stock_quantity': 30, 'category': 'Furniture'},
                ]
            },
            "test": {
                "users": [
                    {'username': 'admin_test', 'email': 'admin.test@example.com', 'full_name': 'Test Admin', 'password_hash': pwd_context.hash('admin123'), 'role': 'admin'},
                    {'username': 'user_test', 'email': 'user.test@example.com', 'full_name': 'Test User', 'password_hash': pwd_context.hash('user123'), 'role': 'user'},
                ],
                "products": [
                    {'name': 'Laptop', 'description': 'A high-performance laptop for developers.', 'price': 1250.00, 'stock_quantity': 10, 'category': 'Electronics'},
                    {'name': 'Coffee Mug', 'description': 'A standard issue mug.', 'price': 12.50, 'stock_quantity': 95, 'category': 'Kitchenware'},
                ]
            }
        }

        if schema not in seed_data_for_schema:
            print(f"No seed data for schema {schema}")
            return

        data_to_seed = seed_data_for_schema[schema]

        if db.query(models.User).count() == 0:
            for user_data in data_to_seed["users"]:
                db.add(models.User(**user_data))
            db.commit()
            print(f"Seeded users for schema {schema}")

        if db.query(models.Product).count() == 0:
            for product_data in data_to_seed["products"]:
                db.add(models.Product(**product_data))
            db.commit()
            print(f"Seeded products for schema {schema}")

    finally:
        db.close()

def create_change_request(db: Session, change_data: schemas.ChangeRequest, user: models.User):
    """Creates a new entry in the pending_changes table."""
    new_change = models.PendingChange(
        table_name=change_data.table_name,
        record_id=change_data.record_id,
        old_values=change_data.old_values,
        new_values=change_data.new_values,
        submitted_by=user.username
    )
    db.add(new_change)
    db.commit()
    db.refresh(new_change)
    return new_change

def get_record_by_id(table_name: str, record_id: int) -> Optional[dict]:
    """Fetches a single record from a table by its primary key."""
    if record_id is None:
        return None
    
    with engine.connect() as connection:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        primary_key_col = next((c for c in table.columns if c.primary_key), None)
        if primary_key_col is None:
            return None # Or raise an error

        query = table.select().where(primary_key_col == record_id)
        result = connection.execute(query)
        row = result.fetchone()
        return dict(row._mapping) if row else None

def get_pending_changes(db: Session):
    """Get all pending changes for approval, including the original record for context."""
    pending_changes = db.query(models.PendingChange).filter(
        models.PendingChange.status == models.ChangeStatus.PENDING
    ).all()
    
    enriched_changes = []
    for change in pending_changes:
        original_record = get_record_by_id(change.table_name, change.record_id)
        # Convert the SQLAlchemy model to a dictionary for JSON serialization
        change_dict = {
            "id": change.id,
            "table_name": change.table_name,
            "record_id": change.record_id,
            "old_values": _make_record_serializable(change.old_values),
            "new_values": _make_record_serializable(change.new_values),
            "status": change.status.value,  # Convert enum to string
            "submitted_at": change.submitted_at.isoformat() if change.submitted_at else None,
            "submitted_by": change.submitted_by
        }
        enriched_changes.append({
            "change_details": change_dict,
            "original_record": _make_record_serializable(original_record)
        })
    return enriched_changes

def approve_change(db: Session, change_id: int, admin_user_id: int):
    """Approve a pending change and apply it to the target table."""
    change = db.query(models.PendingChange).filter(
        models.PendingChange.id == change_id,
        models.PendingChange.status == models.ChangeStatus.PENDING
    ).first()
    
    if not change:
        raise ValueError(f"Pending change with id {change_id} not found")

    try:
        # Get the state of the record *before* applying the change
        before_state = get_record_by_id(change.table_name, change.record_id)

        # Apply the change to the target table
        _apply_change_to_table(db, change)

        # Create an audit log entry
        audit_log_entry = models.AuditLog(
            pending_change_id=change.id,
            table_name=change.table_name,
            record_id=str(change.record_id) if change.record_id else None,
            before_state=before_state,
            after_state=change.new_values,
            approved_by_id=admin_user_id,
        )
        db.add(audit_log_entry)
        
        # Update the change status to approved
        change.status = models.ChangeStatus.APPROVED
        # Note: You would add reviewed_by, reviewed_at columns to PendingChange model
        # change.reviewed_by = admin_user_id
        # change.reviewed_at = func.now()

        db.commit()
        
        return change
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to approve change: {str(e)}")

def reject_change(db: Session, change_id: int, admin_user_id: int):
    """Reject a pending change"""
    change = db.query(models.PendingChange).filter(
        models.PendingChange.id == change_id,
        models.PendingChange.status == models.ChangeStatus.PENDING
    ).first()
    
    if not change:
        raise ValueError(f"Change with id {change_id} not found")
    
    change.status = models.ChangeStatus.REJECTED
    # Note: You would add reviewed_by, reviewed_at columns here too
    # change.reviewed_by = admin_user_id
    # change.reviewed_at = func.now()
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
    """DEPRECATED: Create a snapshot of the entire table state"""
    pass

