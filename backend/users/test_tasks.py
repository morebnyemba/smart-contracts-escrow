"""
Tests for Celery tasks in the users app.
"""
from django.test import TestCase, override_settings
from django.core import mail
from unittest.mock import patch, MagicMock
from users.models import CustomUser, SellerProfile
from transactions.models import EscrowTransaction, Milestone
from users.tasks import (
    send_email_notification,
    send_transaction_notification,
    send_verification_notification
)


# Use eager mode for Celery in tests (tasks run synchronously)
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class EmailNotificationTaskTest(TestCase):
    """Test email notification tasks."""
    
    def setUp(self):
        """Set up test data."""
        self.test_email = 'test@example.com'
        
    def test_send_email_notification_success(self):
        """Test successful email sending."""
        # Clear the outbox
        mail.outbox = []
        
        # Call the task
        result = send_email_notification(
            subject='Test Subject',
            message='Test Message',
            recipient_list=[self.test_email]
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['recipients'], [self.test_email])
        self.assertEqual(result['subject'], 'Test Subject')
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        self.assertEqual(mail.outbox[0].body, 'Test Message')
        self.assertIn(self.test_email, mail.outbox[0].to)
    
    def test_send_email_notification_with_custom_from_email(self):
        """Test email sending with custom from_email."""
        mail.outbox = []
        
        custom_from = 'custom@example.com'
        send_email_notification(
            subject='Test',
            message='Body',
            recipient_list=[self.test_email],
            from_email=custom_from
        )
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, custom_from)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TransactionNotificationTaskTest(TestCase):
    """Test transaction notification tasks."""
    
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
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
    
    def test_send_transaction_notification_created(self):
        """Test sending notification for created transaction."""
        mail.outbox = []
        
        result = send_transaction_notification(
            transaction_id=self.transaction.id,
            notification_type='created'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['notification_type'], 'created')
        
        # Email should be sent to both buyer and seller
        self.assertEqual(len(mail.outbox), 1)
        recipients = mail.outbox[0].to
        self.assertEqual(len(recipients), 2)
        self.assertIn(self.buyer.email, recipients)
        self.assertIn(self.seller.email, recipients)
    
    def test_send_transaction_notification_funded(self):
        """Test sending notification for funded transaction."""
        mail.outbox = []
        
        result = send_transaction_notification(
            transaction_id=self.transaction.id,
            notification_type='funded'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('funded', mail.outbox[0].body)
    
    def test_send_transaction_notification_invalid_type(self):
        """Test sending notification with invalid notification type."""
        mail.outbox = []
        
        result = send_transaction_notification(
            transaction_id=self.transaction.id,
            notification_type='invalid_type'
        )
        
        # Should still succeed with default message
        self.assertTrue(result['success'])
        self.assertEqual(len(mail.outbox), 1)
    
    def test_send_transaction_notification_nonexistent_transaction(self):
        """Test sending notification for nonexistent transaction."""
        result = send_transaction_notification(
            transaction_id=99999,
            notification_type='created'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class VerificationNotificationTaskTest(TestCase):
    """Test seller verification notification tasks."""
    
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123'
        )
    
    def test_send_verification_notification_verified(self):
        """Test sending notification for verified status."""
        mail.outbox = []
        
        result = send_verification_notification(
            user_id=self.user.id,
            verification_status='VERIFIED'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'VERIFIED')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verified', mail.outbox[0].body.lower())
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
    
    def test_send_verification_notification_rejected(self):
        """Test sending notification for rejected status."""
        mail.outbox = []
        
        result = send_verification_notification(
            user_id=self.user.id,
            verification_status='REJECTED'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('not approved', mail.outbox[0].body)
    
    def test_send_verification_notification_pending(self):
        """Test sending notification for pending status."""
        mail.outbox = []
        
        result = send_verification_notification(
            user_id=self.user.id,
            verification_status='PENDING'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('under review', mail.outbox[0].body)
    
    def test_send_verification_notification_invalid_user(self):
        """Test sending notification for nonexistent user."""
        result = send_verification_notification(
            user_id=99999,
            verification_status='VERIFIED'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
