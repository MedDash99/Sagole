from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, text, Table, MetaData
from sqlalchemy.orm import sessionmaker
from fastapi import Path, HTTPException
import json
from typing import Optional
import datetime
import decimal
from passlib.context import CryptContext
import os

# Use relative imports
from . import models, schemas, auth
from .config import settings

# Load DB URLs from environment variables
DATABASE_URLS = {
    "dev": os.getenv("DEV_DATABASE_URL", "postgresql://sagole_user:password@localhost/dev_db"),
    "test": os.getenv("TEST_DATABASE_URL", "postgresql://sagole_user:password@localhost/test_db"),
    "prod": os.getenv("PROD_DATABASE_URL", "postgresql://sagole_user:password@localhost/prod_db"),
}

def get_db(env: str = Path(..., title="Environment", description="The environment to connect to (e.g., 'dev', 'test')")):
    if env not in DATABASE_URLS or not DATABASE_URLS[env]:
        raise HTTPException(status_code=404, detail=f"Environment '{env}' not found or not configured.")
    
    db_url = DATABASE_URLS[env]
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Set the search path for the session
        db.execute(text(f"SET search_path TO {env}, public"))
        # Attach engine to the session so we can use it in other functions
        db.get_engine = lambda: engine
        yield db
    finally:
        db.close()

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

def get_all_table_names(db: Session) -> list[str]:
    engine = db.get_engine()
    inspector = inspect(engine)
    env = next((env for env, url in DATABASE_URLS.items() if engine.url.database in url), None)
    if not env:
        return []
    return [name for name in inspector.get_table_names(schema=env) if name != 'alembic_version']

def get_table_data(
    db: Session,
    table_name: str, 
    limit: int = 20, 
    offset: int = 0, 
    filters_json: Optional[str] = None
) -> list[dict]:
    engine = db.get_engine()
    with engine.connect() as connection:
        env = next((env for env, url in DATABASE_URLS.items() if engine.url.database in url), None)
        if not env:
            return []
        query = f"SELECT * FROM {env}.{table_name}"
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
                        
                        metadata = MetaData()
                        table = Table(table_name, metadata, autoload_with=engine, schema=env)
                        
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

def get_table_schema(db: Session, table_name: str) -> list[dict]:
    """Get the schema information for a specific table"""
    engine = db.get_engine()
    inspector = inspect(engine)
    env = next((env for env, url in DATABASE_URLS.items() if engine.url.database in url), None)
    if not env:
        return []
    columns = inspector.get_columns(table_name, schema=env)
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
        schema = os.environ.get("DB_SCHEMA", settings.DB_SCHEMA)

    if schema not in DATABASE_URLS:
        print(f"Schema '{schema}' not found in DATABASE_URLS. Cannot seed database.")
        return

    db_url = DATABASE_URLS[schema]
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        db.commit()

        # Set the search path to the correct schema
        db.execute(text(f"SET search_path TO {schema}, public"))
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
                    {'username': 'sara_d', 'email': 'sara.d@example.com', 'full_name': 'Sara Davis', 'password_hash': pwd_context.hash('pass123'), 'role': 'user'},
                    {'username': 'mike_b', 'email': 'mike.b@example.com', 'full_name': 'Mike Brown', 'password_hash': pwd_context.hash('pass123'), 'role': 'user'},
                    {'username': 'alice_dev', 'email': 'alice.dev@example.com', 'full_name': 'Alice Dev', 'password_hash': pwd_context.hash('alice123'), 'role': 'user'},
                    {'username': 'bob_dev', 'email': 'bob.dev@example.com', 'full_name': 'Bob Dev', 'password_hash': pwd_context.hash('bob123'), 'role': 'user'},
                    {'username': 'carol_dev', 'email': 'carol.dev@example.com', 'full_name': 'Carol Dev', 'password_hash': pwd_context.hash('carol123'), 'role': 'user'},
                    {'username': 'dave_dev', 'email': 'dave.dev@example.com', 'full_name': 'Dave Dev', 'password_hash': pwd_context.hash('dave123'), 'role': 'user'},
                    {'username': 'eve_dev', 'email': 'eve.dev@example.com', 'full_name': 'Eve Dev', 'password_hash': pwd_context.hash('eve123'), 'role': 'user'},
                    {'username': 'frank_dev', 'email': 'frank.dev@example.com', 'full_name': 'Frank Dev', 'password_hash': pwd_context.hash('frank123'), 'role': 'user'},
                    {'username': 'grace_dev', 'email': 'grace.dev@example.com', 'full_name': 'Grace Dev', 'password_hash': pwd_context.hash('grace123'), 'role': 'user'},
                    {'username': 'heidi_dev', 'email': 'heidi.dev@example.com', 'full_name': 'Heidi Dev', 'password_hash': pwd_context.hash('heidi123'), 'role': 'user'},
                    {'username': 'ivan_dev', 'email': 'ivan.dev@example.com', 'full_name': 'Ivan Dev', 'password_hash': pwd_context.hash('ivan123'), 'role': 'user'},
                    {'username': 'judy_dev', 'email': 'judy.dev@example.com', 'full_name': 'Judy Dev', 'password_hash': pwd_context.hash('judy123'), 'role': 'user'},
                    {'username': 'mallory_dev', 'email': 'mallory.dev@example.com', 'full_name': 'Mallory Dev', 'password_hash': pwd_context.hash('mallory123'), 'role': 'user'},
                    {'username': 'oscar_dev', 'email': 'oscar.dev@example.com', 'full_name': 'Oscar Dev', 'password_hash': pwd_context.hash('oscar123'), 'role': 'user'},
                    {'username': 'peggy_dev', 'email': 'peggy.dev@example.com', 'full_name': 'Peggy Dev', 'password_hash': pwd_context.hash('peggy123'), 'role': 'user'},
                    {'username': 'trent_dev', 'email': 'trent.dev@example.com', 'full_name': 'Trent Dev', 'password_hash': pwd_context.hash('trent123'), 'role': 'user'},
                    {'username': 'victor_dev', 'email': 'victor.dev@example.com', 'full_name': 'Victor Dev', 'password_hash': pwd_context.hash('victor123'), 'role': 'user'},
                ],
                "products": [
                    {'name': 'Laptop', 'description': 'A high-performance laptop for developers.', 'price': 1200.50, 'stock_quantity': 15, 'category': 'Electronics'},
                    {'name': 'Coffee Mug', 'description': 'A mug to hold your favorite beverage.', 'price': 15.00, 'stock_quantity': 150, 'category': 'Kitchenware'},
                    {'name': 'Desk Chair', 'description': 'An ergonomic chair for long hours of coding.', 'price': 350.75, 'stock_quantity': 30, 'category': 'Furniture'},
                    {'name': 'Wireless Mouse', 'description': 'A comfortable and responsive wireless mouse.', 'price': 45.00, 'stock_quantity': 200, 'category': 'Peripherals'},
                    {'name': 'Monitor', 'description': 'A 27-inch 4K monitor with great color accuracy.', 'price': 650.00, 'stock_quantity': 50, 'category': 'Electronics'},
                    {'name': 'Notebook', 'description': 'A classic notebook for all your thoughts.', 'price': 9.99, 'stock_quantity': 500, 'category': 'Stationery'},
                    {'name': 'Webcam', 'description': 'A 1080p webcam for clear video calls.', 'price': 89.50, 'stock_quantity': 75, 'category': 'Peripherals'},
                    {'name': 'Standing Desk', 'description': 'Adjustable standing desk for ergonomic work.', 'price': 499.99, 'stock_quantity': 20, 'category': 'Furniture'},
                    {'name': 'Mechanical Keyboard', 'description': 'A tactile mechanical keyboard.', 'price': 120.00, 'stock_quantity': 60, 'category': 'Peripherals'},
                    {'name': 'USB-C Hub', 'description': 'Multi-port USB-C hub for all your devices.', 'price': 39.99, 'stock_quantity': 100, 'category': 'Peripherals'},
                    {'name': 'Desk Lamp', 'description': 'LED desk lamp with adjustable brightness.', 'price': 29.99, 'stock_quantity': 80, 'category': 'Lighting'},
                    {'name': 'Bluetooth Speaker', 'description': 'Portable Bluetooth speaker.', 'price': 59.99, 'stock_quantity': 40, 'category': 'Audio'},
                    {'name': 'External SSD', 'description': 'Fast external SSD for backups.', 'price': 199.99, 'stock_quantity': 25, 'category': 'Storage'},
                    {'name': 'Smartphone Stand', 'description': 'Adjustable stand for smartphones.', 'price': 14.99, 'stock_quantity': 120, 'category': 'Accessories'},
                    {'name': 'Whiteboard', 'description': 'Magnetic whiteboard for brainstorming.', 'price': 79.99, 'stock_quantity': 10, 'category': 'Office'},
                    {'name': 'Noise Cancelling Headphones', 'description': 'Block out distractions with these headphones.', 'price': 299.99, 'stock_quantity': 35, 'category': 'Audio'},
                    {'name': 'HDMI Cable', 'description': 'High-speed HDMI cable.', 'price': 12.99, 'stock_quantity': 200, 'category': 'Accessories'},
                    {'name': 'Portable Projector', 'description': 'Mini projector for presentations.', 'price': 349.99, 'stock_quantity': 8, 'category': 'Electronics'},
                    {'name': 'Ergonomic Mouse Pad', 'description': 'Mouse pad with wrist support.', 'price': 19.99, 'stock_quantity': 90, 'category': 'Accessories'},
                    {'name': 'Desk Organizer', 'description': 'Keep your desk tidy.', 'price': 24.99, 'stock_quantity': 70, 'category': 'Office'},
                ]
            },
            "test": {
                "users": [
                    {'username': 'admin_test', 'email': 'admin.test@example.com', 'full_name': 'Test Admin', 'password_hash': pwd_context.hash('admin123'), 'role': 'admin'},
                    {'username': 'user_test', 'email': 'user.test@example.com', 'full_name': 'Test User', 'password_hash': pwd_context.hash('user123'), 'role': 'user'},
                    {'username': 'guest_test', 'email': 'guest.test@example.com', 'full_name': 'Test Guest', 'password_hash': pwd_context.hash('guest123'), 'role': 'guest'},
                    {'username': 'alice_test', 'email': 'alice.test@example.com', 'full_name': 'Alice Test', 'password_hash': pwd_context.hash('alice123'), 'role': 'user'},
                    {'username': 'bob_test', 'email': 'bob.test@example.com', 'full_name': 'Bob Test', 'password_hash': pwd_context.hash('bob123'), 'role': 'user'},
                    {'username': 'carol_test', 'email': 'carol.test@example.com', 'full_name': 'Carol Test', 'password_hash': pwd_context.hash('carol123'), 'role': 'user'},
                    {'username': 'dave_test', 'email': 'dave.test@example.com', 'full_name': 'Dave Test', 'password_hash': pwd_context.hash('dave123'), 'role': 'user'},
                    {'username': 'eve_test', 'email': 'eve.test@example.com', 'full_name': 'Eve Test', 'password_hash': pwd_context.hash('eve123'), 'role': 'user'},
                    {'username': 'frank_test', 'email': 'frank.test@example.com', 'full_name': 'Frank Test', 'password_hash': pwd_context.hash('frank123'), 'role': 'user'},
                    {'username': 'grace_test', 'email': 'grace.test@example.com', 'full_name': 'Grace Test', 'password_hash': pwd_context.hash('grace123'), 'role': 'user'},
                    {'username': 'heidi_test', 'email': 'heidi.test@example.com', 'full_name': 'Heidi Test', 'password_hash': pwd_context.hash('heidi123'), 'role': 'user'},
                    {'username': 'ivan_test', 'email': 'ivan.test@example.com', 'full_name': 'Ivan Test', 'password_hash': pwd_context.hash('ivan123'), 'role': 'user'},
                    {'username': 'judy_test', 'email': 'judy.test@example.com', 'full_name': 'Judy Test', 'password_hash': pwd_context.hash('judy123'), 'role': 'user'},
                    {'username': 'mallory_test', 'email': 'mallory.test@example.com', 'full_name': 'Mallory Test', 'password_hash': pwd_context.hash('mallory123'), 'role': 'user'},
                    {'username': 'oscar_test', 'email': 'oscar.test@example.com', 'full_name': 'Oscar Test', 'password_hash': pwd_context.hash('oscar123'), 'role': 'user'},
                    {'username': 'peggy_test', 'email': 'peggy.test@example.com', 'full_name': 'Peggy Test', 'password_hash': pwd_context.hash('peggy123'), 'role': 'user'},
                    {'username': 'trent_test', 'email': 'trent.test@example.com', 'full_name': 'Trent Test', 'password_hash': pwd_context.hash('trent123'), 'role': 'user'},
                    {'username': 'victor_test', 'email': 'victor.test@example.com', 'full_name': 'Victor Test', 'password_hash': pwd_context.hash('victor123'), 'role': 'user'},
                    {'username': 'wendy_test', 'email': 'wendy.test@example.com', 'full_name': 'Wendy Test', 'password_hash': pwd_context.hash('wendy123'), 'role': 'user'},
                    {'username': 'zara_test', 'email': 'zara.test@example.com', 'full_name': 'Zara Test', 'password_hash': pwd_context.hash('zara123'), 'role': 'user'},
                ],
                "products": [
                    {'name': 'Test Laptop', 'description': 'A test laptop.', 'price': 1100.00, 'stock_quantity': 10, 'category': 'Electronics'},
                    {'name': 'Test Mug', 'description': 'A test mug.', 'price': 10.00, 'stock_quantity': 100, 'category': 'Kitchenware'},
                    {'name': 'Test Chair', 'description': 'A test chair.', 'price': 300.00, 'stock_quantity': 20, 'category': 'Furniture'},
                    {'name': 'Test Mouse', 'description': 'A test mouse.', 'price': 40.00, 'stock_quantity': 150, 'category': 'Peripherals'},
                    {'name': 'Test Monitor', 'description': 'A test monitor.', 'price': 600.00, 'stock_quantity': 40, 'category': 'Electronics'},
                    {'name': 'Test Notebook', 'description': 'A test notebook.', 'price': 8.99, 'stock_quantity': 400, 'category': 'Stationery'},
                    {'name': 'Test Webcam', 'description': 'A test webcam.', 'price': 80.00, 'stock_quantity': 60, 'category': 'Peripherals'},
                    {'name': 'Test Desk', 'description': 'A test standing desk.', 'price': 450.00, 'stock_quantity': 15, 'category': 'Furniture'},
                    {'name': 'Test Keyboard', 'description': 'A test keyboard.', 'price': 100.00, 'stock_quantity': 50, 'category': 'Peripherals'},
                    {'name': 'Test Hub', 'description': 'A test USB-C hub.', 'price': 35.00, 'stock_quantity': 90, 'category': 'Peripherals'},
                    {'name': 'Test Lamp', 'description': 'A test desk lamp.', 'price': 25.00, 'stock_quantity': 70, 'category': 'Lighting'},
                    {'name': 'Test Speaker', 'description': 'A test speaker.', 'price': 50.00, 'stock_quantity': 30, 'category': 'Audio'},
                    {'name': 'Test SSD', 'description': 'A test SSD.', 'price': 180.00, 'stock_quantity': 20, 'category': 'Storage'},
                    {'name': 'Test Stand', 'description': 'A test phone stand.', 'price': 12.99, 'stock_quantity': 100, 'category': 'Accessories'},
                    {'name': 'Test Whiteboard', 'description': 'A test whiteboard.', 'price': 70.00, 'stock_quantity': 8, 'category': 'Office'},
                    {'name': 'Test Headphones', 'description': 'A test headphones.', 'price': 250.00, 'stock_quantity': 25, 'category': 'Audio'},
                    {'name': 'Test HDMI', 'description': 'A test HDMI cable.', 'price': 10.99, 'stock_quantity': 150, 'category': 'Accessories'},
                    {'name': 'Test Projector', 'description': 'A test projector.', 'price': 300.00, 'stock_quantity': 6, 'category': 'Electronics'},
                    {'name': 'Test Mouse Pad', 'description': 'A test mouse pad.', 'price': 15.99, 'stock_quantity': 80, 'category': 'Accessories'},
                    {'name': 'Test Organizer', 'description': 'A test desk organizer.', 'price': 20.00, 'stock_quantity': 60, 'category': 'Office'},
                ]
            },
            "prod": {
                "users": [
                    {'username': 'admin_prod', 'email': 'admin.prod@example.com', 'full_name': 'Prod Admin', 'password_hash': pwd_context.hash('admin123'), 'role': 'admin'},
                    {'username': 'user_prod', 'email': 'user.prod@example.com', 'full_name': 'Prod User', 'password_hash': pwd_context.hash('user123'), 'role': 'user'},
                    {'username': 'guest_prod', 'email': 'guest.prod@example.com', 'full_name': 'Prod Guest', 'password_hash': pwd_context.hash('guest123'), 'role': 'guest'},
                    {'username': 'alice_prod', 'email': 'alice.prod@example.com', 'full_name': 'Alice Prod', 'password_hash': pwd_context.hash('alice123'), 'role': 'user'},
                    {'username': 'bob_prod', 'email': 'bob.prod@example.com', 'full_name': 'Bob Prod', 'password_hash': pwd_context.hash('bob123'), 'role': 'user'},
                    {'username': 'carol_prod', 'email': 'carol.prod@example.com', 'full_name': 'Carol Prod', 'password_hash': pwd_context.hash('carol123'), 'role': 'user'},
                    {'username': 'dave_prod', 'email': 'dave.prod@example.com', 'full_name': 'Dave Prod', 'password_hash': pwd_context.hash('dave123'), 'role': 'user'},
                    {'username': 'eve_prod', 'email': 'eve.prod@example.com', 'full_name': 'Eve Prod', 'password_hash': pwd_context.hash('eve123'), 'role': 'user'},
                    {'username': 'frank_prod', 'email': 'frank.prod@example.com', 'full_name': 'Frank Prod', 'password_hash': pwd_context.hash('frank123'), 'role': 'user'},
                    {'username': 'grace_prod', 'email': 'grace.prod@example.com', 'full_name': 'Grace Prod', 'password_hash': pwd_context.hash('grace123'), 'role': 'user'},
                    {'username': 'heidi_prod', 'email': 'heidi.prod@example.com', 'full_name': 'Heidi Prod', 'password_hash': pwd_context.hash('heidi123'), 'role': 'user'},
                    {'username': 'ivan_prod', 'email': 'ivan.prod@example.com', 'full_name': 'Ivan Prod', 'password_hash': pwd_context.hash('ivan123'), 'role': 'user'},
                    {'username': 'judy_prod', 'email': 'judy.prod@example.com', 'full_name': 'Judy Prod', 'password_hash': pwd_context.hash('judy123'), 'role': 'user'},
                    {'username': 'mallory_prod', 'email': 'mallory.prod@example.com', 'full_name': 'Mallory Prod', 'password_hash': pwd_context.hash('mallory123'), 'role': 'user'},
                    {'username': 'oscar_prod', 'email': 'oscar.prod@example.com', 'full_name': 'Oscar Prod', 'password_hash': pwd_context.hash('oscar123'), 'role': 'user'},
                    {'username': 'peggy_prod', 'email': 'peggy.prod@example.com', 'full_name': 'Peggy Prod', 'password_hash': pwd_context.hash('peggy123'), 'role': 'user'},
                    {'username': 'trent_prod', 'email': 'trent.prod@example.com', 'full_name': 'Trent Prod', 'password_hash': pwd_context.hash('trent123'), 'role': 'user'},
                    {'username': 'victor_prod', 'email': 'victor.prod@example.com', 'full_name': 'Victor Prod', 'password_hash': pwd_context.hash('victor123'), 'role': 'user'},
                    {'username': 'wendy_prod', 'email': 'wendy.prod@example.com', 'full_name': 'Wendy Prod', 'password_hash': pwd_context.hash('wendy123'), 'role': 'user'},
                    {'username': 'zara_prod', 'email': 'zara.prod@example.com', 'full_name': 'Zara Prod', 'password_hash': pwd_context.hash('zara123'), 'role': 'user'},
                ],
                "products": [
                    {'name': 'Prod Laptop', 'description': 'A production laptop.', 'price': 1300.00, 'stock_quantity': 12, 'category': 'Electronics'},
                    {'name': 'Prod Mug', 'description': 'A production mug.', 'price': 18.00, 'stock_quantity': 120, 'category': 'Kitchenware'},
                    {'name': 'Prod Chair', 'description': 'A production chair.', 'price': 400.00, 'stock_quantity': 25, 'category': 'Furniture'},
                    {'name': 'Prod Mouse', 'description': 'A production mouse.', 'price': 55.00, 'stock_quantity': 180, 'category': 'Peripherals'},
                    {'name': 'Prod Monitor', 'description': 'A production monitor.', 'price': 700.00, 'stock_quantity': 60, 'category': 'Electronics'},
                    {'name': 'Prod Notebook', 'description': 'A production notebook.', 'price': 11.99, 'stock_quantity': 600, 'category': 'Stationery'},
                    {'name': 'Prod Webcam', 'description': 'A production webcam.', 'price': 95.00, 'stock_quantity': 90, 'category': 'Peripherals'},
                    {'name': 'Prod Desk', 'description': 'A production standing desk.', 'price': 550.00, 'stock_quantity': 30, 'category': 'Furniture'},
                    {'name': 'Prod Keyboard', 'description': 'A production keyboard.', 'price': 140.00, 'stock_quantity': 80, 'category': 'Peripherals'},
                    {'name': 'Prod Hub', 'description': 'A production USB-C hub.', 'price': 45.00, 'stock_quantity': 110, 'category': 'Peripherals'},
                    {'name': 'Prod Lamp', 'description': 'A production desk lamp.', 'price': 35.00, 'stock_quantity': 90, 'category': 'Lighting'},
                    {'name': 'Prod Speaker', 'description': 'A production speaker.', 'price': 70.00, 'stock_quantity': 50, 'category': 'Audio'},
                    {'name': 'Prod SSD', 'description': 'A production SSD.', 'price': 220.00, 'stock_quantity': 30, 'category': 'Storage'},
                    {'name': 'Prod Stand', 'description': 'A production phone stand.', 'price': 16.99, 'stock_quantity': 130, 'category': 'Accessories'},
                    {'name': 'Prod Whiteboard', 'description': 'A production whiteboard.', 'price': 90.00, 'stock_quantity': 12, 'category': 'Office'},
                    {'name': 'Prod Headphones', 'description': 'A production headphones.', 'price': 320.00, 'stock_quantity': 45, 'category': 'Audio'},
                    {'name': 'Prod HDMI', 'description': 'A production HDMI cable.', 'price': 15.99, 'stock_quantity': 220, 'category': 'Accessories'},
                    {'name': 'Prod Projector', 'description': 'A production projector.', 'price': 400.00, 'stock_quantity': 10, 'category': 'Electronics'},
                    {'name': 'Prod Mouse Pad', 'description': 'A production mouse pad.', 'price': 22.99, 'stock_quantity': 100, 'category': 'Accessories'},
                    {'name': 'Prod Organizer', 'description': 'A production desk organizer.', 'price': 28.00, 'stock_quantity': 80, 'category': 'Office'},
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

def get_record_by_id(db: Session, table_name: str, record_id: int) -> Optional[dict]:
    """Fetches a single record from a table by its primary key."""
    if record_id is None:
        return None
    
    engine = db.get_engine()
    with engine.connect() as connection:
        metadata = MetaData()
        # Use the configured schema directly
        schema = settings.DB_SCHEMA
        table = Table(table_name, metadata, autoload_with=engine, schema=schema)
        
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
        original_record = get_record_by_id(db, change.table_name, change.record_id)
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
    print(f"🔄 Approving change {change_id} by admin user {admin_user_id}")
    
    change = db.query(models.PendingChange).filter(
        models.PendingChange.id == change_id,
        models.PendingChange.status == models.ChangeStatus.PENDING
    ).first()
    
    if not change:
        print(f"❌ Change {change_id} not found or not pending")
        raise ValueError(f"Pending change with id {change_id} not found")

    print(f"📝 Change details: table={change.table_name}, record_id={change.record_id}")
    print(f"📝 New values: {change.new_values}")

    try:
        # Get the state of the record *before* applying the change
        print("🔍 Getting before state...")
        before_state = get_record_by_id(db, change.table_name, change.record_id)
        print(f"📊 Before state: {before_state}")

        # Step 1: Apply the change to the target table
        print("✏️ Applying change to table...")
        _apply_change_to_table(db, change)
        print("✅ Change applied successfully")

        # Step 2: Take a snapshot of the entire table after the change
        print("📸 Creating table snapshot...")
        _create_table_snapshot(db, change.table_name, change.id)
        print("✅ Table snapshot created successfully")

        # Step 3: Create an audit log entry
        print("📝 Creating audit log entry...")
        # Serialize datetime objects to make them JSON serializable
        serialized_before_state = _make_record_serializable(before_state)
        serialized_after_state = _make_record_serializable(change.new_values)
        
        audit_log_entry = models.AuditLog(
            pending_change_id=change.id,
            table_name=change.table_name,
            record_id=str(change.record_id) if change.record_id else None,
            before_state=serialized_before_state,
            after_state=serialized_after_state,
            approved_by_id=admin_user_id,
        )
        db.add(audit_log_entry)
        print("📝 Audit log entry created")
        
        # Step 4: Update the change status to approved
        print("🔄 Updating change status to APPROVED...")
        change.status = models.ChangeStatus.APPROVED
        
        print("💾 Committing transaction...")
        db.commit()
        print("✅ Transaction committed successfully")
        
        return change
    except Exception as e:
        print(f"❌ Error in approve_change: {str(e)}")
        print(f"❌ Exception type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
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
    # Load table from the configured schema
    engine = db.get_engine()
    table = Table(table_name, metadata, autoload_with=engine, schema=settings.DB_SCHEMA)

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
    """Applies a pending change to its target table."""
    engine = db.get_engine()
    metadata = MetaData()
    
    # Use the configured schema directly instead of trying to derive from URL
    schema = settings.DB_SCHEMA
    
    # Load table from the configured schema
    table = Table(change.table_name, metadata, autoload_with=engine, schema=schema)

    if change.record_id is not None and change.new_values:
        # This is an update
        stmt = table.update().where(table.c.id == change.record_id).values(**change.new_values)
        db.execute(stmt)
    elif change.record_id is None and change.new_values:
        # This is an insert
        stmt = table.insert().values(**change.new_values)
        result = db.execute(stmt)
        # Update the change record with the new ID
        change.record_id = result.inserted_primary_key[0]
    elif change.record_id is not None and not change.new_values:
        # This is a delete
        stmt = table.delete().where(table.c.id == change.record_id)
        db.execute(stmt)
    
    # Don't commit here - let the calling function handle the transaction

def _create_table_snapshot(db: Session, table_name: str, change_request_id: int):
    """Creates a snapshot of a table's data and stores it."""
    try:
        print(f"📸 Creating snapshot for table: {table_name}")
        
        # Get all data from the table
        engine = db.get_engine()
        metadata = MetaData()
        
        # Use the configured schema directly instead of trying to derive from URL
        schema = settings.DB_SCHEMA

        print(f"🔧 Loading table metadata for schema: {schema}")
        table = Table(table_name, metadata, autoload_with=engine, schema=schema)
        print(f"🔧 Table loaded successfully, columns: {[c.name for c in table.columns]}")
        
        with engine.connect() as connection:
            result = connection.execute(table.select())
            data = [dict(row) for row in result.mappings()]
            print(f"📊 Found {len(data)} records to snapshot.")

        # Serialize data to JSON
        snapshot_data = json.dumps(data, default=str)

        # Create the snapshot record
        snapshot = models.Snapshot(
            table_name=table_name,
            snapshot_data=snapshot_data,
            change_request_id=change_request_id
        )
        db.add(snapshot)
        # Don't commit here - let the calling function handle the transaction
        print(f"✅ Snapshot for table {table_name} created with ID {snapshot.id}")

    except Exception as e:
        print(f"❌ Error creating snapshot for table {table_name}: {e}")
        db.rollback()
        # Optionally re-raise the exception if you want the calling function to handle it
        raise

def _get_table_data_with_session(db: Session, table_name: str, limit: int = 20, offset: int = 0) -> list[dict]:
    """
    An alternative implementation to get table data that uses an existing session
    instead of creating a new one.
    """
    engine = db.get_engine()
    metadata = MetaData()
    # Use the configured schema directly
    schema = settings.DB_SCHEMA
    table = Table(table_name, metadata, autoload_with=engine, schema=schema)
    
    query = table.select().limit(limit).offset(offset)
    result = db.execute(query)
    rows = [dict(row._mapping) for row in result]
    return rows

def get_snapshots_for_table(db: Session, table_name: str):
    """Get all snapshots for a specific table, ordered by creation date (newest first)"""
    snapshots = db.query(models.Snapshot).filter(
        models.Snapshot.table_name == table_name
    ).order_by(models.Snapshot.created_at.desc()).all()
    
    return [{
        "id": snapshot.id,
        "change_request_id": snapshot.change_request_id,
        "table_name": snapshot.table_name,
        "created_at": snapshot.created_at.isoformat(),
        "record_count": len(snapshot.snapshot_data) if snapshot.snapshot_data else 0
    } for snapshot in snapshots]

def get_snapshot_data(db: Session, snapshot_id: int):
    """Get the full data for a specific snapshot"""
    snapshot = db.query(models.Snapshot).filter(models.Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise ValueError(f"Snapshot with id {snapshot_id} not found")
    
    return {
        "id": snapshot.id,
        "change_request_id": snapshot.change_request_id,
        "table_name": snapshot.table_name,
        "created_at": snapshot.created_at.isoformat(),
        "snapshot_data": snapshot.snapshot_data
    }

