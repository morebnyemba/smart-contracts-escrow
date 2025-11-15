"""
Celery configuration for the backend project.

This module configures Celery to work with Django and sets up
task discovery and scheduling capabilities.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')


# Celery Beat schedule configuration
# These tasks will run automatically according to the defined schedule
app.conf.beat_schedule = {
    'send-daily-transaction-summary': {
        'task': 'backend.scheduled_tasks.send_daily_transaction_summary',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8:00 AM
    },
    'cleanup-old-pending-transactions': {
        'task': 'backend.scheduled_tasks.cleanup_old_pending_transactions',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2:00 AM
    },
    'check-overdue-milestones': {
        'task': 'backend.scheduled_tasks.check_overdue_milestones',
        'schedule': crontab(hour=10, minute=0, day_of_week='monday'),  # Run every Monday at 10:00 AM
    },
}
