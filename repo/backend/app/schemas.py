from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
import enum

class ChangeStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Schema for the request body of the /changes endpoint
class ChangeRequest(BaseModel):
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[dict[str, Any]] = None
    new_values: dict[str, Any]

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None

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
    change_request_id: int
    table_name: str
    snapshot_data: list[dict[str, Any]]  # Complete table data as list of records

class SnapshotCreate(SnapshotBase):
    pass

class Snapshot(SnapshotBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# AuditLog Schemas
class AuditLogBase(BaseModel):
    pending_change_id: int
    table_name: str
    record_id: str
    before_state: Optional[dict[str, Any]] = None
    after_state: dict[str, Any]
    approved_by_id: int

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    approved_at: datetime

    class Config:
        orm_mode = True 