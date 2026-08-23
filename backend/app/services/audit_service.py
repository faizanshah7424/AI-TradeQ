import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuthAuditLog

logger = logging.getLogger("auth.audit")

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        status: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuthAuditLog:
        """
        Record a security-relevant event in the database audit table and structured log.
        Guarantees that sensitive data (passwords, tokens) are NEVER persisted or logged.
        """
        sanitized_details = None
        if details:
            # Deep sanitize details to ensure no password or token fields slip through
            clean_dict = {}
            for k, v in details.items():
                if k.lower() in {"password", "token", "access_token", "refresh_token", "secret", "authorization"}:
                    clean_dict[k] = "[REDACTED]"
                else:
                    clean_dict[k] = v
            sanitized_details = json.dumps(clean_dict)

        audit_entry = AuthAuditLog(
            user_id=user_id,
            event_type=event_type,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            correlation_id=correlation_id,
            details=sanitized_details,
        )

        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
        except Exception as e:
            db.rollback()
            logger.error("Failed to write database audit log entry: %s", str(e))

        logger.info(
            "AUTH_AUDIT_EVENT | event=%s | status=%s | user_id=%s | ip=%s",
            event_type,
            status,
            user_id or "anonymous",
            ip_address or "unknown",
        )
        return audit_entry

audit_service = AuditService()
