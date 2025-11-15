from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from transactions.models import EscrowTransaction, Milestone
from wallets.models import UserWallet

User = get_user_model()


class TransactionAPITest(TestCase):
    def setUp(self):
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
        
        # Create wallet for buyer with sufficient funds
        self.buyer_wallet = UserWallet.objects.create(
            user=self.buyer,
            balance=Decimal('1000.00')
        )

    def test_create_transaction(self):
        """Test creating a transaction via API"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'title': 'New Project',
            'seller': self.seller.id,
            'milestones': [
                {'title': 'Milestone 1', 'description': 'First milestone', 'value': '50.00'},
                {'title': 'Milestone 2', 'description': 'Second milestone', 'value': '50.00'},
            ]
        }
        
        response = self.client.post('/api/transactions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Project')
        self.assertEqual(response.data['total_value'], '100.00')
        self.assertEqual(response.data['status'], 'PENDING_FUNDING')
        self.assertEqual(len(response.data['milestones']), 2)

    def test_create_transaction_without_milestones(self):
        """Test that creating a transaction without milestones fails"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'title': 'New Project',
            'seller': self.seller.id,
            'milestones': []
        }
        
        response = self.client.post('/api/transactions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_transactions(self):
        """Test listing transactions for authenticated user"""
        self.client.force_authenticate(user=self.buyer)
        
        # Create a transaction
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller
        )
        
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_fund_transaction(self):
        """Test funding a transaction"""
        self.client.force_authenticate(user=self.buyer)
        
        # Create a transaction
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/fund/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'IN_ESCROW')
        
        # Check buyer wallet balance was deducted
        self.buyer_wallet.refresh_from_db()
        self.assertEqual(self.buyer_wallet.balance, Decimal('900.00'))

    def test_fund_transaction_insufficient_funds(self):
        """Test funding a transaction with insufficient funds"""
        self.client.force_authenticate(user=self.buyer)
        
        # Set buyer wallet to low balance
        self.buyer_wallet.balance = Decimal('50.00')
        self.buyer_wallet.save()
        
        # Create a transaction that costs more
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/fund/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient funds', response.data['error'])

    def test_only_buyer_can_fund(self):
        """Test that only the buyer can fund a transaction"""
        self.client.force_authenticate(user=self.seller)
        
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/fund/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_accept_transaction(self):
        """Test seller accepting a transaction"""
        self.client.force_authenticate(user=self.seller)
        
        # Create a transaction in PENDING_FUNDING status
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'AWAITING_PAYMENT')
        
        # Verify status changed in database
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, EscrowTransaction.TransactionStatus.AWAITING_PAYMENT)
    
    def test_only_seller_can_accept(self):
        """Test that only the seller can accept a transaction"""
        self.client.force_authenticate(user=self.buyer)
        
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only the seller', response.data['error'])
    
    def test_accept_transaction_invalid_status(self):
        """Test that transaction can only be accepted in PENDING_FUNDING status"""
        self.client.force_authenticate(user=self.seller)
        
        # Create a transaction in IN_ESCROW status
        transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        response = self.client.post(f'/api/transactions/{transaction.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot be accepted', response.data['error'])


class MilestoneAPITest(TestCase):
    def setUp(self):
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
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        self.milestone = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 1',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.PENDING
        )
        
        # Create seller wallet
        self.seller_wallet = UserWallet.objects.create(
            user=self.seller,
            balance=Decimal('0.00')
        )

    def test_submit_milestone(self):
        """Test seller submitting work for a milestone"""
        self.client.force_authenticate(user=self.seller)
        
        data = {'submission_details': 'Work completed and submitted'}
        response = self.client.post(
            f'/api/milestones/{self.milestone.id}/submit/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'AWAITING_REVIEW')
        self.assertEqual(response.data['submission_details'], 'Work completed and submitted')

    def test_only_seller_can_submit(self):
        """Test that only the seller can submit work"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {'submission_details': 'Work completed'}
        response = self.client.post(
            f'/api/milestones/{self.milestone.id}/submit/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_milestone(self):
        """Test buyer approving a milestone"""
        self.client.force_authenticate(user=self.buyer)
        
        # Set milestone to awaiting review
        self.milestone.status = Milestone.MilestoneStatus.AWAITING_REVIEW
        self.milestone.save()
        
        response = self.client.post(f'/api/milestones/{self.milestone.id}/approve/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'COMPLETED')
        
        # Check seller wallet received payment
        self.seller_wallet.refresh_from_db()
        self.assertEqual(self.seller_wallet.balance, Decimal('50.00'))

    def test_only_buyer_can_approve(self):
        """Test that only the buyer can approve a milestone"""
        self.client.force_authenticate(user=self.seller)
        
        self.milestone.status = Milestone.MilestoneStatus.AWAITING_REVIEW
        self.milestone.save()
        
        response = self.client.post(f'/api/milestones/{self.milestone.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_revision(self):
        """Test buyer requesting revision"""
        self.client.force_authenticate(user=self.buyer)
        
        # Set milestone to awaiting review
        self.milestone.status = Milestone.MilestoneStatus.AWAITING_REVIEW
        self.milestone.save()
        
        response = self.client.post(f'/api/milestones/{self.milestone.id}/request_revision/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'REVISION_REQUESTED')

    def test_complete_all_milestones_completes_transaction(self):
        """Test that completing all milestones marks transaction as completed"""
        self.client.force_authenticate(user=self.buyer)
        
        # Create another milestone
        milestone2 = Milestone.objects.create(
            transaction=self.transaction,
            title='Milestone 2',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.AWAITING_REVIEW
        )
        
        # Set first milestone to awaiting review and approve it
        self.milestone.status = Milestone.MilestoneStatus.AWAITING_REVIEW
        self.milestone.save()
        self.client.post(f'/api/milestones/{self.milestone.id}/approve/')
        
        # Approve second milestone
        self.client.post(f'/api/milestones/{milestone2.id}/approve/')
        
        # Check transaction is completed
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, EscrowTransaction.TransactionStatus.COMPLETED)


class WalletAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )
        self.wallet = UserWallet.objects.create(
            user=self.user,
            balance=Decimal('500.00')
        )

    def test_view_wallet(self):
        """Test viewing user's wallet"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/wallets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(Decimal(response.data['results'][0]['balance']), Decimal('500.00'))

    def test_cannot_view_other_user_wallet(self):
        """Test that users can only view their own wallet"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='password123'
        )
        other_wallet = UserWallet.objects.create(
            user=other_user,
            balance=Decimal('1000.00')
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/wallets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        # Should only see own wallet
        self.assertEqual(response.data['results'][0]['user']['id'], self.user.id)
