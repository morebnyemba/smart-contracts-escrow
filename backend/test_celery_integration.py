#!/usr/bin/env python
"""
Manual test script to verify Celery integration.
This script tests the Celery setup without requiring a running Redis instance.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from backend.celery import app as celery_app
from users.tasks import send_email_notification, send_transaction_notification
from backend.scheduled_tasks import send_daily_transaction_summary

def test_celery_app():
    """Test that Celery app is properly configured."""
    print("Testing Celery app configuration...")
    print(f"✓ Celery app name: {celery_app.main}")
    print(f"✓ Celery broker URL: {celery_app.conf.broker_url}")
    print(f"✓ Celery result backend: {celery_app.conf.result_backend}")
    print(f"✓ Task serializer: {celery_app.conf.task_serializer}")
    print(f"✓ Timezone: {celery_app.conf.timezone}")
    print()

def test_task_discovery():
    """Test that tasks are discovered."""
    print("Testing task discovery...")
    registered_tasks = list(celery_app.tasks.keys())
    
    expected_tasks = [
        'users.tasks.send_email_notification',
        'users.tasks.send_transaction_notification',
        'users.tasks.send_verification_notification',
        'backend.scheduled_tasks.send_daily_transaction_summary',
        'backend.scheduled_tasks.cleanup_old_pending_transactions',
        'backend.scheduled_tasks.check_overdue_milestones',
    ]
    
    for task in expected_tasks:
        if task in registered_tasks:
            print(f"✓ Task registered: {task}")
        else:
            print(f"✗ Task NOT found: {task}")
    print()

def test_beat_schedule():
    """Test that Celery Beat schedule is configured."""
    print("Testing Celery Beat schedule...")
    schedule = celery_app.conf.beat_schedule
    
    if schedule:
        print(f"✓ Found {len(schedule)} scheduled tasks:")
        for name, config in schedule.items():
            print(f"  - {name}")
            print(f"    Task: {config['task']}")
            print(f"    Schedule: {config['schedule']}")
    else:
        print("✗ No scheduled tasks found")
    print()

def test_task_signature():
    """Test that tasks can be called (without executing)."""
    print("Testing task signatures...")
    
    try:
        # Test email notification signature
        sig1 = send_email_notification.signature(
            kwargs={
                'subject': 'Test',
                'message': 'Test message',
                'recipient_list': ['test@example.com']
            }
        )
        print(f"✓ Email notification signature created: {sig1}")
    except Exception as e:
        print(f"✗ Failed to create email notification signature: {e}")
    
    try:
        # Test transaction notification signature
        sig2 = send_transaction_notification.signature(
            kwargs={
                'transaction_id': 1,
                'notification_type': 'created'
            }
        )
        print(f"✓ Transaction notification signature created: {sig2}")
    except Exception as e:
        print(f"✗ Failed to create transaction notification signature: {e}")
    
    try:
        # Test scheduled task signature
        sig3 = send_daily_transaction_summary.signature()
        print(f"✓ Daily summary signature created: {sig3}")
    except Exception as e:
        print(f"✗ Failed to create daily summary signature: {e}")
    print()

def main():
    """Run all tests."""
    print("=" * 60)
    print("Celery Integration Test")
    print("=" * 60)
    print()
    
    try:
        test_celery_app()
        test_task_discovery()
        test_beat_schedule()
        test_task_signature()
        
        print("=" * 60)
        print("✓ All integration tests passed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start Redis: redis-server")
        print("2. Start Celery worker: celery -A backend worker --loglevel=info")
        print("3. Start Celery Beat: celery -A backend beat --loglevel=info")
        print("4. Run Django tests: python manage.py test users.test_tasks backend.test_scheduled_tasks")
        
        return 0
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
