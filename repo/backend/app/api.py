from fastapi import APIRouter, HTTPException
from . import db_manager

router = APIRouter()

@router.post("/seed")
def seed_db():
    """
    Seeds the database with initial mock data.
    This is typically a one-time operation.
    We use POST because it changes the state of the server.
    """
    try:
        result = db_manager.seed_database()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/tables")
def list_tables():
    """
    Returns a list of all table names in the public schema.
    """
    try:
        tables = db_manager.get_all_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}")
def get_data_from_table(table_name: str, limit: int = 20, offset: int = 0):
    """
    Gets data from a specific table.
    """
    try:
        if table_name not in db_manager.get_all_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
            
        data = db_manager.get_table_data(table_name=table_name, limit=limit, offset=offset)
        return {"table": table_name, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
