from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# Import the new schema and the get_db dependency
from . import db_manager, schemas
from .main import get_db

router = APIRouter()

# --- Add the new endpoint below ---

@router.post("/changes", status_code=201)
def submit_change_for_approval(
    change_request: schemas.ChangeRequest, 
    db: Session = Depends(get_db)
):
    """
    Receives an edit from the frontend and submits it for approval
    by creating a record in the pending_changes table.
    """
    try:
        return db_manager.create_change_request(db=db, change_data=change_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit change: {str(e)}")


# --- Keep the other endpoints as they are ---

@router.post("/seed")
def seed_db():
    # ... (this function stays the same)
    try:
        result = db_manager.seed_database()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
def list_tables():
    # ... (this function stays the same)
    try:
        tables = db_manager.get_all_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}")
def get_data_from_table(table_name: str, limit: int = 20, offset: int = 0):
    # ... (this function stays the same)
    try:
        if table_name not in db_manager.get_all_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
            
        data = db_manager.get_table_data(table_name=table_name, limit=limit, offset=offset)
        return {"table": table_name, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
