# Celery Setup and Usage Guide

This guide explains how to use Celery and Celery Beat for asynchronous task processing in the Smart Contracts Escrow Platform.

## Overview

Celery is integrated to handle long-running tasks asynchronously, including:
- Email notifications
- Transaction status updates
- File uploads processing
- Scheduled periodic tasks (via Celery Beat)

## Prerequisites

- Redis server (or another message broker)
- Python packages: `celery`, `redis`, `django-celery-beat`

All required packages are included in `requirements.txt`.

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and start Redis:**
   
   On Ubuntu/Debian:
   ```bash
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```
   
   On macOS:
   ```bash
   brew install redis
   brew services start redis
   ```
   
   Using Docker:
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

3. **Run migrations for Celery Beat:**
   ```bash
   python manage.py migrate
   ```

## Configuration

### Environment Variables

Configure Celery broker and result backend using environment variables:

```bash
export CELERY_BROKER_URL='redis://localhost:6379/0'
export CELERY_RESULT_BACKEND='redis://localhost:6379/0'
```

Or add them to your `.env` file:
```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Settings

Celery configuration is located in `backend/settings.py`:
- `CELERY_BROKER_URL`: Message broker URL (default: redis://localhost:6379/0)
- `CELERY_RESULT_BACKEND`: Result backend URL (default: redis://localhost:6379/0)
- `CELERY_TASK_SERIALIZER`: Task serialization format (json)
- `CELERY_TASK_TIME_LIMIT`: Maximum task execution time (30 minutes)

## Running Celery

### Start Celery Worker

Run a Celery worker to process async tasks:

```bash
cd backend
celery -A backend worker --loglevel=info
```

For development with auto-reload:
```bash
celery -A backend worker --loglevel=info --pool=solo
```

### Start Celery Beat (Scheduler)

Run Celery Beat to execute scheduled tasks:

```bash
celery -A backend beat --loglevel=info
```

### Combined Worker and Beat

For development, you can run both in one command:

```bash
celery -A backend worker --beat --loglevel=info
```

### Production Deployment

For production, run worker and beat as separate processes with proper process management (e.g., systemd, supervisord, or Docker).

Example systemd service files:

**`/etc/systemd/system/celery.service`:**
```ini
[Unit]
Description=Celery Worker Service
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
ExecStart=/path/to/venv/bin/celery -A backend worker --loglevel=info --detach
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/celerybeat.service`:**
```ini
[Unit]
Description=Celery Beat Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
ExecStart=/path/to/venv/bin/celery -A backend beat --loglevel=info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Available Tasks

### Email Notification Tasks (`users/tasks.py`)

#### `send_email_notification`
Send an email notification asynchronously.

**Usage:**
```python
from users.tasks import send_email_notification

# Call immediately
send_email_notification(
    subject='Welcome!',
    message='Thank you for registering.',
    recipient_list=['user@example.com']
)

# Call asynchronously (recommended)
send_email_notification.delay(
    subject='Welcome!',
    message='Thank you for registering.',
    recipient_list=['user@example.com']
)
```

#### `send_transaction_notification`
Send notifications related to escrow transactions.

**Usage:**
```python
from users.tasks import send_transaction_notification

send_transaction_notification.delay(
    transaction_id=123,
    notification_type='funded'  # 'created', 'funded', 'completed', etc.
)
```

#### `send_verification_notification`
Send seller verification status notification.

**Usage:**
```python
from users.tasks import send_verification_notification

send_verification_notification.delay(
    user_id=456,
    verification_status='VERIFIED'  # 'VERIFIED', 'REJECTED', 'PENDING'
)
```

### Scheduled Tasks (`backend/scheduled_tasks.py`)

These tasks run automatically according to the schedule defined in `backend/celery.py`:

#### `send_daily_transaction_summary`
Sends daily transaction summaries to users with active transactions.
- **Schedule:** Daily at 8:00 AM

#### `cleanup_old_pending_transactions`
Sends reminders for transactions pending funding for more than 7 days.
- **Schedule:** Daily at 2:00 AM

#### `check_overdue_milestones`
Checks for milestones pending for more than 14 days and notifies sellers.
- **Schedule:** Every Monday at 10:00 AM

## Integrating Tasks into Your Code

### Example: Sending notification when transaction is created

In your views or serializers:

```python
from users.tasks import send_transaction_notification

class TransactionViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        transaction = serializer.save()
        
        # Send notification asynchronously
        send_transaction_notification.delay(
            transaction_id=transaction.id,
            notification_type='created'
        )
```

### Example: Custom task with retry logic

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_file_upload(self, file_path):
    try:
        # Process the file
        result = process_large_file(file_path)
        return {'success': True, 'result': result}
    except Exception as exc:
        logger.error(f"File processing failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

## Managing Scheduled Tasks via Django Admin

Django Celery Beat provides an admin interface to manage periodic tasks:

1. Access Django admin: `http://localhost:8000/admin/`
2. Navigate to "Periodic Tasks" under "Django Celery Beat"
3. You can:
   - Add new periodic tasks
   - Edit existing schedules
   - Enable/disable tasks
   - View task execution history

## Monitoring and Debugging

### View Task Status

```python
from celery.result import AsyncResult

# Get task result
task_id = 'task-id-here'
result = AsyncResult(task_id)

print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### Celery Flower (Web-based Monitoring)

Install and run Flower for a web UI:

```bash
pip install flower
celery -A backend flower
```

Access at: `http://localhost:5555`

### View Worker Logs

When running workers, logs are output to the console. For production, redirect to files:

```bash
celery -A backend worker --loglevel=info --logfile=/var/log/celery/worker.log
```

## Testing

Tests are configured to run tasks synchronously using `CELERY_TASK_ALWAYS_EAGER=True`.

Run Celery-related tests:

```bash
python manage.py test users.test_tasks backend.test_scheduled_tasks
```

## Common Issues and Solutions

### Issue: Tasks not executing

**Solution:** Ensure Redis is running and the worker is started:
```bash
redis-cli ping  # Should return PONG
celery -A backend worker --loglevel=info
```

### Issue: ImportError when starting worker

**Solution:** Ensure you're in the correct directory and virtual environment:
```bash
cd backend
source venv/bin/activate  # or your virtualenv
celery -A backend worker --loglevel=info
```

### Issue: Tasks timing out

**Solution:** Increase task time limit in `settings.py`:
```python
CELERY_TASK_TIME_LIMIT = 60 * 60  # 1 hour
```

### Issue: Scheduled tasks not running

**Solution:** Ensure Celery Beat is running alongside the worker:
```bash
# Terminal 1
celery -A backend worker --loglevel=info

# Terminal 2
celery -A backend beat --loglevel=info
```

## Best Practices

1. **Use `.delay()` for async execution:**
   ```python
   # Good
   send_email_notification.delay(...)
   
   # Bad (runs synchronously)
   send_email_notification(...)
   ```

2. **Handle exceptions in tasks:**
   ```python
   @shared_task
   def my_task():
       try:
           # Task logic
           pass
       except Exception as exc:
           logger.error(f"Task failed: {exc}")
           raise
   ```

3. **Set appropriate timeouts:**
   ```python
   @shared_task(time_limit=300)  # 5 minutes
   def long_running_task():
       pass
   ```

4. **Use task routing for different queues:**
   ```python
   @shared_task(queue='high_priority')
   def urgent_task():
       pass
   ```

5. **Monitor task failures:**
   - Use Flower or logging to track failed tasks
   - Implement proper error handling and retry logic

## Further Reading

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Celery Beat Documentation](https://django-celery-beat.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
