from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, call
from decimal import Decimal

from transactions.models import EscrowTransaction, Milestone
from transactions.signals import milestone_approved, transaction_funded, revision_requested, work_submitted
from wallets.models import UserWallet
from .models import Notification

User = get_user_model()


class SignalTests(TestCase):
    """Tests for Django signals in the notifications app."""
    
    def setUp(self):
        """Set up test data."""
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='password123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='password123'
        )
        
        self.transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        self.milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.AWAITING_REVIEW
        )
    
    @patch('notifications.receivers.send_milestone_approved_notification')
    def test_milestone_approved_signal(self, mock_notification):
        """Test that milestone_approved signal triggers notification."""
        # Send the signal
        milestone_approved.send(
            sender=self.__class__,
            milestone=self.milestone,
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Assert notification was called with correct parameters
        mock_notification.assert_called_once_with(
            milestone_id=self.milestone.id,
            buyer_id=self.buyer.id,
            seller_id=self.seller.id
        )
    
    @patch('notifications.receivers.send_transaction_funded_notification')
    def test_transaction_funded_signal(self, mock_notification):
        """Test that transaction_funded signal triggers notification."""
        # Send the signal
        transaction_funded.send(
            sender=self.__class__,
            transaction=self.transaction,
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Assert notification was called with correct parameters
        mock_notification.assert_called_once_with(
            transaction_id=self.transaction.id,
            buyer_id=self.buyer.id,
            seller_id=self.seller.id
        )
    
    @patch('notifications.receivers.send_revision_requested_notification')
    def test_revision_requested_signal(self, mock_notification):
        """Test that revision_requested signal triggers notification."""
        # Send the signal
        revision_requested.send(
            sender=self.__class__,
            milestone=self.milestone,
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Assert notification was called with correct parameters
        mock_notification.assert_called_once_with(
            milestone_id=self.milestone.id,
            buyer_id=self.buyer.id,
            seller_id=self.seller.id
        )
    
    @patch('notifications.receivers.send_work_submitted_notification')
    def test_work_submitted_signal(self, mock_notification):
        """Test that work_submitted signal triggers notification."""
        # Send the signal
        work_submitted.send(
            sender=self.__class__,
            milestone=self.milestone,
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Assert notification was called with correct parameters
        mock_notification.assert_called_once_with(
            milestone_id=self.milestone.id,
            buyer_id=self.buyer.id,
            seller_id=self.seller.id
        )
    
    @patch('notifications.receivers.send_milestone_approved_notification')
    def test_multiple_signals(self, mock_notification):
        """Test that multiple signals can be sent and handled correctly."""
        # Create another milestone
        milestone2 = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 2',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.AWAITING_REVIEW
        )
        
        # Send signals for both milestones
        milestone_approved.send(
            sender=self.__class__,
            milestone=self.milestone,
            buyer=self.buyer,
            seller=self.seller
        )
        
        milestone_approved.send(
            sender=self.__class__,
            milestone=milestone2,
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Assert notification was called twice with correct parameters
        self.assertEqual(mock_notification.call_count, 2)
        mock_notification.assert_has_calls([
            call(
                milestone_id=self.milestone.id,
                buyer_id=self.buyer.id,
                seller_id=self.seller.id
            ),
            call(
                milestone_id=milestone2.id,
                buyer_id=self.buyer.id,
                seller_id=self.seller.id
            )
        ])


class NotificationModelTests(TestCase):
    """Tests for Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='password123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='password123'
        )
        
        self.transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller
        )
        
        self.milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('50.00')
        )
    
    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.seller,
            notification_type=Notification.NotificationType.ESCROW_FUNDED,
            message='Test notification',
            transaction=self.transaction
        )
        
        self.assertEqual(notification.recipient, self.seller)
        self.assertEqual(notification.notification_type, Notification.NotificationType.ESCROW_FUNDED)
        self.assertEqual(notification.message, 'Test notification')
        self.assertEqual(notification.transaction, self.transaction)
        self.assertFalse(notification.is_read)
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at descending."""
        notif1 = Notification.objects.create(
            recipient=self.seller,
            notification_type=Notification.NotificationType.ESCROW_FUNDED,
            message='First notification'
        )
        notif2 = Notification.objects.create(
            recipient=self.seller,
            notification_type=Notification.NotificationType.MILESTONE_APPROVED,
            message='Second notification'
        )
        
        notifications = Notification.objects.filter(recipient=self.seller)
        self.assertEqual(notifications[0], notif2)
        self.assertEqual(notifications[1], notif1)


class NotificationAPITests(TestCase):
    """Tests for Notification API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='password123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='password123'
        )
        
        self.transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller
        )
        
        self.milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('50.00')
        )
        
        # Create some notifications
        self.notif1 = Notification.objects.create(
            recipient=self.seller,
            notification_type=Notification.NotificationType.ESCROW_FUNDED,
            message='Transaction funded',
            transaction=self.transaction
        )
        self.notif2 = Notification.objects.create(
            recipient=self.seller,
            notification_type=Notification.NotificationType.MILESTONE_APPROVED,
            message='Milestone approved',
            transaction=self.transaction,
            milestone=self.milestone
        )
    
    def test_list_notifications(self):
        """Test listing notifications for authenticated user."""
        self.client.force_authenticate(user=self.seller)
        
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_notifications_filtered_by_user(self):
        """Test that users only see their own notifications."""
        self.client.force_authenticate(user=self.buyer)
        
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        self.client.force_authenticate(user=self.seller)
        
        response = self.client.post(f'/api/notifications/{self.notif1.id}/mark_as_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
    
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read."""
        self.client.force_authenticate(user=self.seller)
        
        response = self.client.post('/api/notifications/mark_all_as_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '2 notifications marked as read.')
        
        self.notif1.refresh_from_db()
        self.notif2.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
        self.assertTrue(self.notif2.is_read)
    
    def test_unread_count(self):
        """Test getting unread notification count."""
        self.client.force_authenticate(user=self.seller)
        
        response = self.client.get('/api/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Mark one as read
        self.notif1.is_read = True
        self.notif1.save()
        
        response = self.client.get('/api/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
