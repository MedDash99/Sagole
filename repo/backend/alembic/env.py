from logging.config import fileConfig

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- KEY CHANGES START HERE ---

# 1. Import your app's Base and all your models.
# This is how Alembic knows about the tables you want to create.
from app.database import Base
from app.models import User, Product, PendingChange, Snapshot

# 2. Set the target_metadata to your app's Base.
target_metadata = Base.metadata

# --- KEY CHANGES END HERE ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # For offline mode, we still need to get the URL from our app's settings
    from app.config import settings
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # --- KEY CHANGE IN THIS FUNCTION ---
    # 3. Import your app's database engine and use it directly.
    # This ensures Alembic uses the exact same connection as your app.
    from app.database import engine
    import os
    from sqlalchemy import text

    # Get schema from environment variable, default to 'dev'
    schema = os.environ.get("DB_SCHEMA", "dev")

    with engine.connect() as connection:
        # Create schema if it doesn't exist
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        
        # Set search path to this schema
        connection.execute(text(f"SET search_path TO {schema}"))

        # In the context, ensure Alembic knows about the schema
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            version_table_schema=schema,
            include_schemas=True # We are using schemas
        )
        
        # Also set the schema for the metadata object
        target_metadata.schema = schema

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
