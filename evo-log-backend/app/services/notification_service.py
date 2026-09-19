"""
Notification service - handles multi-channel notifications
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.user import User


class NotificationService:
    """Service for multi-channel notifications"""
    
    @staticmethod
    def send_email_notification(user_id: int, subject: str, message: str, db: Session) -> bool:
        """Send email notification to user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            return False
        
        # In a real implementation, this would integrate with an email service
        # For now, we'll just log the notification
        print(f"Email sent to {user.email}: {subject} - {message}")
        return True
    
    @staticmethod
    def send_sms_notification(user_id: int, message: str, db: Session) -> bool:
        """Send SMS notification to user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.phone:
            return False
        
        # In a real implementation, this would integrate with an SMS service
        print(f"SMS sent to {user.phone}: {message}")
        return True
    
    @staticmethod
    def send_bulk_notification(user_ids: List[int], subject: str, message: str, db: Session) -> int:
        """Send notification to multiple users"""
        success_count = 0
        for user_id in user_ids:
            if NotificationService.send_email_notification(user_id, subject, message, db):
                success_count += 1
        return success_count
    
    @staticmethod
    def send_role_based_notification(role_name: str, subject: str, message: str, db: Session) -> int:
        """Send notification to all users with a specific role"""
        from app.models.user import user_roles, Role
        
        users_with_role = db.query(User).join(user_roles).join(Role).filter(
            Role.name == role_name
        ).all()
        
        success_count = 0
        for user in users_with_role:
            if NotificationService.send_email_notification(user.id, subject, message, db):
                success_count += 1
        return success_count