import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, Boolean, Numeric, Text
from sqlalchemy.sql import func
from .database import Base



class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'dev'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)




class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'schema': 'dev'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category = Column(String(50))


class ChangeStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class PendingChange(Base):
    __tablename__ = "pending_changes"
    __table_args__ = {'schema': 'dev'}

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
    __table_args__ = {'schema': 'dev'}

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    change_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_log'
    __table_args__ = {'schema': 'dev'}

    id = Column(Integer, primary_key=True, index=True)
    pending_change_id = Column(Integer, nullable=False)
    table_name = Column(String, nullable=False)
    record_id = Column(String, nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=False)
    approved_by_id = Column(Integer, nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
