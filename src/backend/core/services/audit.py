"""Audit trail helpers (SRS NFR-10: traceable approvals and releases)."""
import logging

from ..models import AuditLog

logger = logging.getLogger(__name__)


def log_action(actor, action, entity_type='', entity_id='', **details):
    """Record a traceable entry. Never raises — auditing must not break a request."""
    try:
        actor_name = ''
        if actor is not None:
            actor_name = actor.get_full_name() or actor.username
        entry = AuditLog.objects.create(
            actor=actor if getattr(actor, 'pk', None) else None,
            actor_name=actor_name,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id not in (None, '') else '',
            details=details,
        )
        logger.info('audit: %s', entry)
        return entry
    except Exception:  # pragma: no cover - auditing is best effort
        logger.exception('failed to write audit log for %s', action)
        return None
