from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from transactions.models import EscrowTransaction, Milestone, Review
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


class ReviewAPITest(TestCase):
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
        
        # Create a completed transaction
        self.transaction = EscrowTransaction.objects.create(
            title='Test Project',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.COMPLETED
        )

    def test_buyer_can_leave_review(self):
        """Test that buyer can leave a review"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'rating': 5,
            'comment': 'Great work! Very satisfied.'
        }
        
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great work! Very satisfied.')
        self.assertEqual(response.data['reviewer']['id'], self.buyer.id)
        
        # Check transaction status changed to CLOSED
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, EscrowTransaction.TransactionStatus.CLOSED)

    def test_seller_can_leave_review(self):
        """Test that seller can leave a review"""
        self.client.force_authenticate(user=self.seller)
        
        data = {
            'rating': 4,
            'comment': 'Good buyer, prompt payment.'
        }
        
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['reviewer']['id'], self.seller.id)

    def test_review_without_comment(self):
        """Test that review can be left without a comment"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'rating': 3
        }
        
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 3)
        self.assertEqual(response.data['comment'], '')

    def test_cannot_review_twice(self):
        """Test that a user cannot review the same transaction twice"""
        self.client.force_authenticate(user=self.buyer)
        
        data = {
            'rating': 5,
            'comment': 'First review'
        }
        
        # Leave first review
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to leave second review
        data['comment'] = 'Second review'
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already left a review', response.data['error'])

    def test_invalid_rating(self):
        """Test that invalid ratings are rejected"""
        self.client.force_authenticate(user=self.buyer)
        
        # Test rating too low
        data = {'rating': 0}
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test rating too high
        data = {'rating': 6}
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_buyer_or_seller_can_review(self):
        """Test that only buyer or seller can review a transaction"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='password123'
        )
        self.client.force_authenticate(user=other_user)
        
        data = {'rating': 5}
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        # Returns 404 because the transaction is not in the user's queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_review_incomplete_transaction(self):
        """Test that reviews can only be left for completed transactions"""
        # Change transaction to IN_ESCROW status
        self.transaction.status = EscrowTransaction.TransactionStatus.IN_ESCROW
        self.transaction.save()
        
        self.client.force_authenticate(user=self.buyer)
        
        data = {'rating': 5}
        response = self.client.post(
            f'/api/transactions/{self.transaction.id}/leave_review/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('completed transactions', response.data['error'])
