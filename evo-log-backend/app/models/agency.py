"""
Agency model for multi-tenant support
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Agency(Base):
    """Agency model for managing different branches/locations"""
    __tablename__ = "agencies"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    city = Column(String(50))
    country = Column(String(50), default="Cameroun")
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_headquarters = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="agency")
    organization = relationship("Organization", back_populates="agencies")