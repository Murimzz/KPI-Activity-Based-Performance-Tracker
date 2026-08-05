"""Helpers for writing audit log entries."""

from audit.models import AuditLog


def log_action(
    *,
    action: str,
    model_name: str,
    object_id='',
    description='',
    user=None,
) -> AuditLog:
    """Create an audit log row. Safe to call from views/services later."""
    return AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id is not None else '',
        description=description or '',
    )
