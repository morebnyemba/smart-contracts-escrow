"""
Tests for scheduled Celery tasks.
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from transactions.models import EscrowTransaction, Milestone
from backend.scheduled_tasks import (
    send_daily_transaction_summary,
    cleanup_old_pending_transactions,
    check_overdue_milestones
)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class DailyTransactionSummaryTest(TestCase):
    """Test daily transaction summary task."""
    
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123'
        )
    
    def test_send_daily_summary_with_active_transactions(self):
        """Test sending summary when user has active transactions."""
        # Create active transaction
        EscrowTransaction.objects.create(
            title='Active Transaction',
            total_value=1000.00,
            buyer=self.user,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        mail.outbox = []
        
        result = send_daily_transaction_summary()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['summaries_sent'], 0)
        self.assertGreater(len(mail.outbox), 0)
    
    def test_send_daily_summary_no_active_transactions(self):
        """Test sending summary when no active transactions exist."""
        mail.outbox = []
        
        result = send_daily_transaction_summary()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summaries_sent'], 0)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_send_daily_summary_excludes_completed_transactions(self):
        """Test that completed transactions are not included in summary."""
        # Create completed transaction
        EscrowTransaction.objects.create(
            title='Completed Transaction',
            total_value=1000.00,
            buyer=self.user,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.COMPLETED
        )
        
        mail.outbox = []
        
        result = send_daily_transaction_summary()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summaries_sent'], 0)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CleanupOldPendingTransactionsTest(TestCase):
    """Test cleanup of old pending transactions."""
    
    def setUp(self):
        """Set up test data."""
        self.buyer = CustomUser.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='testpass123'
        )
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123'
        )
    
    def test_cleanup_sends_reminder_for_old_pending(self):
        """Test that reminders are sent for old pending transactions."""
        # Create old pending transaction
        old_transaction = EscrowTransaction.objects.create(
            title='Old Pending',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        # Set created_at to 8 days ago
        old_transaction.created_at = timezone.now() - timedelta(days=8)
        old_transaction.save(update_fields=['created_at'])
        
        mail.outbox = []
        
        result = cleanup_old_pending_transactions()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['reminders_sent'], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.buyer.email, mail.outbox[0].to)
        self.assertIn('Reminder', mail.outbox[0].subject)
    
    def test_cleanup_ignores_recent_pending(self):
        """Test that recent pending transactions are not affected."""
        # Create recent pending transaction
        EscrowTransaction.objects.create(
            title='Recent Pending',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        mail.outbox = []
        
        result = cleanup_old_pending_transactions()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['reminders_sent'], 0)
    
    def test_cleanup_ignores_non_pending_transactions(self):
        """Test that non-pending transactions are ignored."""
        # Create old non-pending transaction
        old_transaction = EscrowTransaction.objects.create(
            title='Old In Escrow',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        old_transaction.created_at = timezone.now() - timedelta(days=10)
        old_transaction.save(update_fields=['created_at'])
        
        mail.outbox = []
        
        result = cleanup_old_pending_transactions()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['reminders_sent'], 0)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CheckOverdueMilestonesTest(TestCase):
    """Test checking for overdue milestones."""
    
    def setUp(self):
        """Set up test data."""
        self.buyer = CustomUser.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='testpass123'
        )
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123'
        )
        self.transaction = EscrowTransaction.objects.create(
            title='Test Transaction',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        # Set transaction created date to 20 days ago
        self.transaction.created_at = timezone.now() - timedelta(days=20)
        self.transaction.save(update_fields=['created_at'])
    
    def test_check_overdue_milestones_sends_notification(self):
        """Test that notifications are sent for overdue milestones."""
        # Create overdue milestone
        milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Overdue Milestone',
            description='Test',
            value=500.00,
            status=Milestone.MilestoneStatus.PENDING
        )
        
        mail.outbox = []
        
        result = check_overdue_milestones()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['notifications_sent'], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.seller.email, mail.outbox[0].to)
        self.assertIn('Overdue', mail.outbox[0].subject)
    
    def test_check_overdue_milestones_ignores_recent(self):
        """Test that recent milestones are not flagged as overdue."""
        # Create recent transaction
        recent_transaction = EscrowTransaction.objects.create(
            title='Recent Transaction',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        milestone = Milestone.objects.create(
            transaction=recent_transaction,
            title='Recent Milestone',
            description='Test',
            value=500.00,
            status=Milestone.MilestoneStatus.PENDING
        )
        
        mail.outbox = []
        
        result = check_overdue_milestones()
        
        self.assertTrue(result['success'])
        # Should not include the recent milestone
        self.assertEqual(result['notifications_sent'], 0)
    
    def test_check_overdue_milestones_ignores_non_pending(self):
        """Test that non-pending milestones are ignored."""
        # Create completed milestone
        milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Completed Milestone',
            description='Test',
            value=500.00,
            status=Milestone.MilestoneStatus.COMPLETED
        )
        
        mail.outbox = []
        
        result = check_overdue_milestones()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['notifications_sent'], 0)
