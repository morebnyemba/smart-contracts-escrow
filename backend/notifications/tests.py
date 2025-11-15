from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, call
from decimal import Decimal

from transactions.models import EscrowTransaction, Milestone
from transactions.signals import milestone_approved, transaction_funded, revision_requested
from wallets.models import UserWallet

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
