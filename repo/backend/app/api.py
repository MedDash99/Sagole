# app/api.py
# API router for all endpoints related to authentication, data changes, and table management
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from fastapi.security import OAuth2PasswordRequestForm
from . import auth, models
from datetime import timedelta
from typing import Optional

# Import the new schema and the get_db dependency
from . import db_manager, schemas

router = APIRouter()

# Dependency functions for user authentication and role validation
get_current_user = auth.create_get_current_user(db_manager.get_db)
get_current_active_user = lambda current_user: auth.get_current_active_user(current_user)
get_current_admin_user = lambda current_user: auth.get_current_admin_user(current_user)

# --- Endpoints ---

@router.post("/{env}/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_manager.get_db)):
    # Handle user login and return an access token if credentials are valid
    print(f"Login attempt - Username: {form_data.username}")
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    print(f"User found: {user is not None}")
    
    if user:
        print(f"User role: {user.role}, is_active: {user.is_active}")
        password_valid = auth.verify_password(form_data.password, user.password_hash)
        print(f"Password verification: {password_valid}")
    
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        print("Login failed - Invalid credentials")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("Login successful - Generating token")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


@router.post("/{env}/changes", status_code=201)
def submit_change_for_approval(
    change_request: schemas.ChangeRequest, 
    db: Session = Depends(db_manager.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Receives an edit from the frontend and submits it for approval
    by creating a record in the pending_changes table.
    """
    try:
        active_user = get_current_active_user(current_user)
        return db_manager.create_change_request(
            db=db, 
            change_data=change_request, 
            user=active_user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit change: {str(e)}")

@router.get("/{env}/tables/{table_name}/schema")
def get_table_schema(table_name: str, db: Session = Depends(db_manager.get_db)):
    """
    Get the schema information for a specific table
    """
    try:
        schema = db_manager.get_table_schema(db=db, table_name=table_name)
        return {"table": table_name, "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{env}/changes")
def get_pending_changes(
    db: Session = Depends(db_manager.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all pending changes for approval
    """
    try:
        admin_user = get_current_admin_user(current_user)
        changes = db_manager.get_pending_changes(db=db)
        return {"changes": changes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{env}/changes/{change_id}/approve")
def approve_change(
    change_id: int, 
    db: Session = Depends(db_manager.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Approve a pending change
    """
    try:
        admin_user = get_current_admin_user(current_user)
        result = db_manager.approve_change(db=db, change_id=change_id, admin_user_id=admin_user.id)
        return {"message": "Change approved successfully", "change_id": change_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{env}/changes/{change_id}/reject")
def reject_change(
    change_id: int, 
    db: Session = Depends(db_manager.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Reject a pending change
    """
    try:
        admin_user = get_current_admin_user(current_user)
        result = db_manager.reject_change(db=db, change_id=change_id, admin_user_id=admin_user.id)
        return {"message": "Change rejected successfully", "change_id": change_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{env}/tables/{table_name}/{record_id}", status_code=204)
def delete_record_from_table(
    table_name: str, 
    record_id: int, 
    db: Session = Depends(db_manager.get_db)
):
    """Deletes a record from a table."""
    try:
        db_manager.delete_record(db=db, table_name=table_name, record_id=record_id)
        return {"message": "Record deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{env}/seed")
def seed_db(env: str):
    # Seed the database for a specific environment
    try:
        result = db_manager.seed_database(schema=env)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{env}/tables")
def list_tables(db: Session = Depends(db_manager.get_db)):
    # List all table names in the current environment
    try:
        tables = db_manager.get_all_table_names(db=db)
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{env}/tables/{table_name}")
def get_data_from_table(
    table_name: str, 
    limit: int = 20, 
    offset: int = 0,
    filters: Optional[str] = None,
    db: Session = Depends(db_manager.get_db)
):
    # Fetch data from a specific table, with optional pagination and filtering
    try:
        if table_name not in db_manager.get_all_table_names(db=db):
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
            
        data = db_manager.get_table_data(
            db=db,
            table_name=table_name, 
            limit=limit, 
            offset=offset,
            filters_json=filters
        )
        return {"table": table_name, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{env}/tables/{table_name}/snapshots")
def get_table_snapshots(
    table_name: str,
    db: Session = Depends(db_manager.get_db)
):
    """Get all snapshots for a specific table"""
    try:
        snapshots = db_manager.get_snapshots_for_table(db=db, table_name=table_name)
        return {"table": table_name, "snapshots": snapshots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{env}/snapshots/{snapshot_id}")
def get_snapshot(
    snapshot_id: int,
    db: Session = Depends(db_manager.get_db)
):
    # Retrieve the full data for a specific snapshot
    try:
        snapshot_data = db_manager.get_snapshot_data(db=db, snapshot_id=snapshot_id)
        return snapshot_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
