# Backend

## Setup

1.  **Install Dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    Create a `.env` file in this directory (or use `.env.dev`, `.env.test`, etc.) and add the following environment variables:

    ```env
    # Database connection URLs for each environment
    DEV_DATABASE_URL=postgresql://sagole_user:password@localhost/dev_db
    TEST_DATABASE_URL=postgresql://sagole_user:password@localhost/test_db
    PROD_DATABASE_URL=postgresql://sagole_user:password@localhost/prod_db

    # Security
    SECRET_KEY=your_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    APP_ENV=dev  # or test, prod, etc.
    ```

3.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

    The server will be running on `http://localhost:8000` by default.

## Features

- FastAPI-based REST API for database admin and auditing
- Multi-environment support (dev, test, prod, etc.)
- JWT authentication with admin/user roles
- Change request and approval workflow
- Immutable, point-in-time table snapshots for audit and rollback
- Table browsing, filtering, and editing
- Git-style diff for change requests
- CORS enabled for local frontend development

## Unimplemented Features

- Data compression for large snapshots
- Incremental (delta) snapshots
- Automatic retention/cleanup policies for old snapshots
- UI tools for restoring data from snapshots
- Integration with external backup systems
- User management endpoints (beyond basic admin/user roles)
- Advanced audit logging and reporting
- Ability to open JSON changes in a separate window or fullscreen for easier reading

See [`SNAPSHOT_FUNCTIONALITY.md`](SNAPSHOT_FUNCTIONALITY.md) for more details on the snapshot and audit system. 