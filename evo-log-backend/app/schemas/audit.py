"""
Audit schemas for tracking system operations
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    client_host: Optional[str] = None
    user_agent: Optional[str] = None
    process_time: Optional[float] = None
    timestamp: datetime
    user_id: Optional[int] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True