# Celery Integration Examples

This document provides practical examples of how to integrate Celery tasks into your existing Django views, serializers, and signals.

## Example 1: Send Notification When Transaction is Created

### In your view or serializer:

```python
# transactions/views.py or transactions/serializers.py
from rest_framework import viewsets
from users.tasks import send_transaction_notification

class TransactionViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    def perform_create(self, serializer):
        # Create the transaction
        transaction = serializer.save()
        
        # Send notification asynchronously (non-blocking)
        send_transaction_notification.delay(
            transaction_id=transaction.id,
            notification_type='created'
        )
        
        return transaction
```

## Example 2: Send Notification When Seller Profile is Verified

### Using Django Signals:

```python
# users/signals.py (create this file)
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import SellerProfile
from users.tasks import send_verification_notification

@receiver(post_save, sender=SellerProfile)
def notify_verification_status_change(sender, instance, created, **kwargs):
    """Send notification when seller verification status changes."""
    if not created:  # Only on updates, not new profiles
        # Check if verification_status was changed
        if instance.tracker.has_changed('verification_status'):
            send_verification_notification.delay(
                user_id=instance.user.id,
                verification_status=instance.verification_status
            )
```

Then register the signal in `users/apps.py`:

```python
# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        import users.signals  # Import signals
```

## Example 3: Send Notification When Milestone is Approved

### In your milestone approval view:

```python
# api/views.py
from rest_framework.decorators import action
from rest_framework.response import Response
from users.tasks import send_transaction_notification

class MilestoneViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        milestone = self.get_object()
        
        # ... existing approval logic ...
        milestone.status = Milestone.MilestoneStatus.COMPLETED
        milestone.save()
        
        # Send notification asynchronously
        send_transaction_notification.delay(
            transaction_id=milestone.transaction.id,
            notification_type='milestone_approved'
        )
        
        return Response({'status': 'milestone approved'})
```

## Example 4: Send Welcome Email on User Registration

```python
# users/views.py or users/serializers.py
from rest_framework import generics
from users.tasks import send_email_notification

class UserRegistrationView(generics.CreateAPIView):
    # ... existing code ...
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Send welcome email asynchronously
        send_email_notification.delay(
            subject='Welcome to Smart Contracts Escrow',
            message=f'Hello {user.username},\n\nThank you for registering!',
            recipient_list=[user.email]
        )
        
        return user
```

## Example 5: Process File Upload Asynchronously

### Create a new task for file processing:

```python
# users/tasks.py (add this task)
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_verification_document(self, profile_id):
    """
    Process verification document asynchronously.
    This could include OCR, validation, or image optimization.
    """
    try:
        from users.models import SellerProfile
        
        profile = SellerProfile.objects.get(id=profile_id)
        
        # Process the document (example: resize image, extract text, etc.)
        # ... your processing logic here ...
        
        logger.info(f"Successfully processed document for profile {profile_id}")
        return {'success': True, 'profile_id': profile_id}
        
    except Exception as exc:
        logger.error(f"Failed to process document: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Use in your view:

```python
# users/views.py
from users.tasks import process_verification_document

class SellerProfileViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    def perform_update(self, serializer):
        profile = serializer.save()
        
        # If verification document was uploaded, process it asynchronously
        if 'verification_document' in serializer.validated_data:
            process_verification_document.delay(profile.id)
        
        return profile
```

## Example 6: Scheduled Task to Generate Reports

### Create the scheduled task:

```python
# backend/scheduled_tasks.py (add this task)
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def generate_weekly_report():
    """
    Generate a weekly report of platform activity.
    Scheduled to run every Monday at 9:00 AM.
    """
    from transactions.models import EscrowTransaction
    from users.tasks import send_email_notification
    
    # Calculate stats for last week
    last_week = timezone.now() - timedelta(days=7)
    
    new_transactions = EscrowTransaction.objects.filter(
        created_at__gte=last_week
    ).count()
    
    completed_transactions = EscrowTransaction.objects.filter(
        status=EscrowTransaction.TransactionStatus.COMPLETED,
        created_at__gte=last_week
    ).count()
    
    # Send report to admin
    report_message = f"""
Weekly Platform Report

New Transactions: {new_transactions}
Completed Transactions: {completed_transactions}

Generated at: {timezone.now()}
    """
    
    send_email_notification.delay(
        subject='Weekly Platform Report',
        message=report_message,
        recipient_list=['admin@example.com']
    )
    
    return {'new': new_transactions, 'completed': completed_transactions}
```

### Register in Celery Beat schedule:

```python
# backend/celery.py (add to beat_schedule)
app.conf.beat_schedule = {
    # ... existing schedules ...
    'generate-weekly-report': {
        'task': 'backend.scheduled_tasks.generate_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week='monday'),
    },
}
```

## Example 7: Chain Multiple Tasks

```python
# Example: Send multiple notifications in sequence
from celery import chain
from users.tasks import send_email_notification

# Chain tasks to run one after another
notification_chain = chain(
    send_email_notification.s(
        subject='Transaction Created',
        message='Your transaction has been created.',
        recipient_list=['buyer@example.com']
    ),
    send_email_notification.s(
        subject='New Transaction Alert',
        message='A new transaction has been assigned to you.',
        recipient_list=['seller@example.com']
    )
)

# Execute the chain
notification_chain.apply_async()
```

## Example 8: Group Parallel Tasks

```python
# Example: Send notifications to multiple users in parallel
from celery import group
from users.tasks import send_email_notification

# Send emails to multiple users in parallel
notification_group = group(
    send_email_notification.s(
        subject='Platform Update',
        message='New features available!',
        recipient_list=[user.email]
    )
    for user in active_users
)

# Execute all tasks in parallel
result = notification_group.apply_async()
```

## Example 9: Task with Countdown (Delayed Execution)

```python
# Example: Send reminder email 24 hours after transaction creation
from users.tasks import send_email_notification

# Send email after 24 hours (86400 seconds)
send_email_notification.apply_async(
    kwargs={
        'subject': 'Transaction Reminder',
        'message': 'Don\'t forget to fund your transaction!',
        'recipient_list': ['buyer@example.com']
    },
    countdown=86400  # 24 hours
)
```

## Example 10: Check Task Status

```python
# Example: Check if a task has completed
from celery.result import AsyncResult

def check_task_status(task_id):
    """Check the status of a Celery task."""
    result = AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return {'status': 'completed', 'result': result.result}
        else:
            return {'status': 'failed', 'error': str(result.info)}
    else:
        return {'status': 'pending'}
```

## Best Practices

1. **Always use `.delay()` or `.apply_async()`** to run tasks asynchronously
2. **Handle exceptions** in your tasks with try-except blocks
3. **Use retry logic** for tasks that might fail temporarily (network issues, etc.)
4. **Keep tasks focused** - one task should do one thing well
5. **Log task execution** for debugging and monitoring
6. **Test with eager mode** during development (tasks run synchronously)
7. **Monitor task failures** in production using Flower or logging
8. **Set appropriate timeouts** for long-running tasks
9. **Use task routing** to separate high-priority from low-priority tasks
10. **Document task parameters** clearly in docstrings

## Testing Tasks

```python
# Example test
from django.test import TestCase, override_settings

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class MyTaskTest(TestCase):
    def test_my_task(self):
        # Task runs synchronously in tests
        result = my_task.delay(param1='value')
        self.assertTrue(result['success'])
```

## Monitoring in Production

1. **Use Flower** for web-based monitoring:
   ```bash
   pip install flower
   celery -A backend flower
   ```
   Access at: http://localhost:5555

2. **Check worker status**:
   ```bash
   celery -A backend inspect active
   celery -A backend inspect stats
   ```

3. **View scheduled tasks**:
   ```bash
   celery -A backend inspect scheduled
   ```

## Troubleshooting

### Tasks not executing
- Check if Redis is running: `redis-cli ping`
- Check if worker is running: `ps aux | grep celery`
- Check worker logs for errors

### Tasks timeout
- Increase `CELERY_TASK_TIME_LIMIT` in settings.py
- Or set timeout per task: `@shared_task(time_limit=300)`

### Tasks fail silently
- Check worker logs
- Use `bind=True` and proper error handling in tasks
- Enable task result backend to store results

For more examples and advanced usage, see the [Celery documentation](https://docs.celeryproject.org/).
