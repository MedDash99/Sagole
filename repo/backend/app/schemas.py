from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import enum

class ChangeStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Schema for the request body of the /changes endpoint
class ChangeRequest(BaseModel):
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[dict[str, Any]] = None
    new_values: dict[str, Any]

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        orm_mode = True

# PendingChange Schemas
class PendingChangeBase(BaseModel):
    table_name: str
    record_id: Optional[int] = None
    new_values: dict[str, Any]

class PendingChangeCreate(PendingChangeBase):
    submitted_by: str

class PendingChange(PendingChangeBase):
    id: int
    old_values: Optional[dict[str, Any]] = None
    status: ChangeStatus
    submitted_at: datetime
    submitted_by: str

    class Config:
        orm_mode = True

# Snapshot Schemas
class SnapshotBase(BaseModel):
    table_name: str
    record_id: int
    data: dict[str, Any]
    change_id: int

class SnapshotCreate(SnapshotBase):
    pass

class Snapshot(SnapshotBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 