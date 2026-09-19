"""
Audit model for tracking system operations
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """Audit log model for tracking API requests and system operations"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10))
    url = Column(String(500))
    status_code = Column(Integer)
    client_host = Column(String(50))
    user_agent = Column(String(500))
    process_time = Column(Numeric)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    # user = relationship("User", back_populates="audit_logs")