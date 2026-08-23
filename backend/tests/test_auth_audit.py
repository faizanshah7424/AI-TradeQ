import pytest
from app.models.audit_log import AuthAuditLog
from app.services.audit_service import audit_service

def test_audit_log_redacts_sensitive_keys(db_session, test_user):
    audit_entry = audit_service.log_event(
        db=db_session,
        event_type="LOGIN_SUCCESS",
        status="SUCCESS",
        user_id=test_user.id,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        details={
            "email": test_user.email,
            "password": "SuperSecretPassword!",
            "refresh_token": "secret_token_value",
            "safe_metadata": "allowed_data",
        },
    )

    assert audit_entry.id is not None
    assert audit_entry.event_type == "LOGIN_SUCCESS"
    assert "SuperSecretPassword!" not in audit_entry.details
    assert "secret_token_value" not in audit_entry.details
    assert "[REDACTED]" in audit_entry.details
    assert "allowed_data" in audit_entry.details
