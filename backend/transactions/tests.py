from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import EscrowTransaction, Milestone

User = get_user_model()


class EscrowTransactionModelTest(TestCase):
    def setUp(self):
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

    def test_create_transaction(self):
        """Test creating an escrow transaction"""
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller
        )
        self.assertEqual(transaction.title, 'Test Project')
        self.assertEqual(transaction.total_value, Decimal('100.00'))
        self.assertEqual(transaction.status, EscrowTransaction.TransactionStatus.PENDING_FUNDING)
        self.assertEqual(transaction.buyer, self.buyer)
        self.assertEqual(transaction.seller, self.seller)

    def test_transaction_status_choices(self):
        """Test that all transaction status choices are valid"""
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller
        )
        
        # Test updating to different statuses
        for status_value, status_label in EscrowTransaction.TransactionStatus.choices:
            transaction.status = status_value
            transaction.save()
            self.assertEqual(transaction.status, status_value)


class MilestoneModelTest(TestCase):
    def setUp(self):
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

    def test_create_milestone(self):
        """Test creating a milestone"""
        milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            description='First milestone',
            value=Decimal('50.00')
        )
        self.assertEqual(milestone.title, 'Milestone 1')
        self.assertEqual(milestone.value, Decimal('50.00'))
        self.assertEqual(milestone.status, Milestone.MilestoneStatus.PENDING)
        self.assertEqual(milestone.transaction, self.transaction)

    def test_milestone_status_choices(self):
        """Test that all milestone status choices are valid"""
        milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('50.00')
        )
        
        # Test updating to different statuses
        for status_value, status_label in Milestone.MilestoneStatus.choices:
            milestone.status = status_value
            milestone.save()
            self.assertEqual(milestone.status, status_value)

    def test_transaction_milestones_relationship(self):
        """Test the relationship between transaction and milestones"""
        Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('30.00')
        )
        Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 2',
            value=Decimal('70.00')
        )
        
        self.assertEqual(self.transaction.milestones.count(), 2)
        total_milestone_value = sum(m.value for m in self.transaction.milestones.all())
        self.assertEqual(total_milestone_value, Decimal('100.00'))
