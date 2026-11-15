"""Celery background tasks.

The broker is configured with ``CELERY_TASK_ALWAYS_EAGER`` when no Redis
broker is reachable, so notifications still get delivered (synchronously) in a
local demo environment.
"""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='core.tasks.send_notification')
def send_notification_task(notification_id):
    """Deliver a stored notification through Firebase Cloud Messaging."""
    from .models import Notification
    from .services.notifications import push_to_broker

    notification = Notification.objects.filter(pk=notification_id).first()
    if notification is None:
        return False
    return push_to_broker(notification.broker, notification)


@shared_task(name='core.tasks.notify_new_project')
def notify_new_project_task(project_id):
    """Fan a new-project notification out to every broker."""
    from .models import Broker, Project
    from .services.notifications import notify_brokers

    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return 0
    brokers = Broker.objects.select_related('user').all()
    notify_brokers(
        brokers,
        title=f'New project launched: {project.name}',
        body=f'{project.location} — {project.total_plots} plots available.',
        kind='project',
        link=f'/projects/{project.pk}',
    )
    return brokers.count()


@shared_task(name='core.tasks.generate_demand_letter')
def generate_demand_letter_task(booking_id):
    """Create the demand letter PDF for an approved booking."""
    from .models import Booking
    from .services.documents import build_demand_letter_pdf, save_document

    booking = Booking.objects.select_related(
        'customer', 'plot', 'plot__project').filter(pk=booking_id).first()
    if booking is None:
        return None
    content, content_type = build_demand_letter_pdf(booking)
    doc = save_document(
        kind='demand_letter',
        title=f'Demand letter - {booking.plot.plot_number}',
        content=content,
        content_type=content_type,
        broker=booking.broker,
        booking=booking,
    )
    return doc.pk
