import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from .database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    # In a real app, this password would be hashed
    password = Column(String, nullable=False)
    # 'admin' or 'regular_user'
    role = Column(String, default='regular_user', nullable=False)
    is_active = Column(Boolean, default=True)




class ChangeStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PendingChange(Base):
    __tablename__ = "pending_changes"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON, nullable=False)
    status = Column(Enum(ChangeStatus), default=ChangeStatus.PENDING, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_by = Column(String, nullable=False)

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    change_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
