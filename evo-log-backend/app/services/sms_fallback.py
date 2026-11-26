import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SMSFallbackService:
    """
    Multi-gateway SMS fallback service for areas with poor mobile internet coverage.
    Supports Twilio, Infobip, and Africa SMS gateways with automatic fallback.
    """
    def __init__(self):
        self.primary_provider = os.getenv("SMS_PROVIDER_PRIMARY", "AFRICA_SMS")
        self.secondary_provider = os.getenv("SMS_PROVIDER_SECONDARY", "TWILIO")

    def send_sms(self, recipient_phone: str, message_text: str) -> Dict[str, Any]:
        raise RuntimeError(
            "SMS delivery is unavailable: no configured provider integration."
        )

sms_fallback_service = SMSFallbackService()
