"""Notification creation and push delivery.

Delivery is pluggable: Firebase Cloud Messaging is used when credentials are
configured, otherwise the notification is stored in the database and the app
polls for it. Storing the row always happens so the feature works offline.
"""
import logging

from django.conf import settings

from ..models import Notification

logger = logging.getLogger(__name__)


def notify(broker, title, body='', kind=Notification.KIND_SYSTEM, link=''):
    """Create a notification for a broker and attempt a push delivery."""
    notification = Notification.objects.create(
        broker=broker, title=title, body=body, kind=kind, link=link
    )
    push_to_broker(broker, notification)
    return notification


def notify_brokers(brokers, title, body='', kind=Notification.KIND_SYSTEM, link=''):
    """Fan a notification out to many brokers (e.g. a new project launch)."""
    return [notify(b, title, body, kind, link) for b in brokers]


def push_to_broker(broker, notification):
    """Best-effort FCM push. Silently no-ops when FCM is not configured."""
    token = getattr(broker.user, 'fcm_token', '') or ''
    if not token or not getattr(settings, 'FCM_SERVER_KEY', ''):
        return False
    try:  # pragma: no cover - requires network credentials
        import requests

        response = requests.post(
            settings.FCM_ENDPOINT,
            headers={
                'Authorization': f"key={settings.FCM_SERVER_KEY}",
                'Content-Type': 'application/json',
            },
            json={
                'to': token,
                'notification': {
                    'title': notification.title,
                    'body': notification.body,
                },
                'data': {'url': notification.link or '/notifications'},
            },
            timeout=5,
        )
        return response.status_code == 200
    except Exception:
        logger.warning('FCM push failed for broker %s', broker)
        return False


def unread_count(broker):
    return broker.notifications.filter(read=False).count()
