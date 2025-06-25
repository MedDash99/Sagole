# app/api.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from fastapi.security import OAuth2PasswordRequestForm
from . import auth, models
from datetime import timedelta
from typing import Optional

# Import the new schema and the get_db dependency
from . import db_manager, schemas
from .dependencies import get_db

router = APIRouter()

# --- Add the new endpoint below ---

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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


@router.post("/changes", status_code=201)
def submit_change_for_approval(
    change_request: schemas.ChangeRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Receives an edit from the frontend and submits it for approval
    by creating a record in the pending_changes table.
    """
    try:
        return db_manager.create_change_request(
            db=db, 
            change_data=change_request, 
            user=current_user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit change: {str(e)}")

@router.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str):
    """
    Get the schema information for a specific table
    """
    try:
        schema = db_manager.get_table_schema(table_name=table_name)
        return {"table": table_name, "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/changes")
def get_pending_changes(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Get all pending changes for approval
    """
    try:
        changes = db_manager.get_pending_changes(db=db)
        return {"changes": changes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/changes/{change_id}/approve")
def approve_change(
    change_id: int, 
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Approve a pending change
    """
    try:
        result = db_manager.approve_change(db=db, change_id=change_id, admin_user_id=admin_user.id)
        return {"message": "Change approved successfully", "change_id": change_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/changes/{change_id}/reject")
def reject_change(
    change_id: int, 
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_current_admin_user)
):
    """
    Reject a pending change
    """
    try:
        result = db_manager.reject_change(db=db, change_id=change_id, admin_user_id=admin_user.id)
        return {"message": "Change rejected successfully", "change_id": change_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tables/{table_name}/{record_id}", status_code=204)
def delete_record_from_table(
    table_name: str, 
    record_id: int, 
    db: Session = Depends(get_db)
):
    """Deletes a record from a table."""
    try:
        db_manager.delete_record(db=db, table_name=table_name, record_id=record_id)
        return {"message": "Record deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed")
def seed_db():
    try:
        result = db_manager.seed_database()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
def list_tables():
    try:
        tables = db_manager.get_all_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}")
def get_data_from_table(
    table_name: str, 
    limit: int = 20, 
    offset: int = 0,
    filters: Optional[str] = None
):
    try:
        if table_name not in db_manager.get_all_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
            
        data = db_manager.get_table_data(
            table_name=table_name, 
            limit=limit, 
            offset=offset,
            filters_json=filters
        )
        return {"table": table_name, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
