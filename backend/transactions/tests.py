from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EscrowTransaction, Milestone

User = get_user_model()


class MyTransactionsViewTestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller1',
            email='seller@example.com',
            password='testpass123'
        )
        self.other_buyer = User.objects.create_user(
            username='buyer2',
            email='buyer2@example.com',
            password='testpass123'
        )
        
        # Create test transactions
        self.transaction1 = EscrowTransaction.objects.create(
            title='Test Transaction 1',
            total_value=1000.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        self.transaction2 = EscrowTransaction.objects.create(
            title='Test Transaction 2',
            total_value=500.00,
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        # Create a transaction for another buyer (should not appear)
        self.other_transaction = EscrowTransaction.objects.create(
            title='Other Buyer Transaction',
            total_value=750.00,
            buyer=self.other_buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.COMPLETED
        )
        
        # Create milestones for transaction1
        self.milestone1 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Milestone 1',
            description='First milestone',
            value=500.00,
            status=Milestone.MilestoneStatus.COMPLETED
        )
        
        self.milestone2 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Milestone 2',
            description='Second milestone',
            value=500.00,
            status=Milestone.MilestoneStatus.PENDING
        )
        
        self.url = reverse('my-transactions')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the endpoint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_authenticated_buyer_can_access(self):
        """Test that authenticated buyer can access their transactions"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_returns_only_buyer_transactions(self):
        """Test that endpoint returns only transactions where user is buyer"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check that the correct transactions are returned
        transaction_ids = [t['id'] for t in response.data]
        self.assertIn(self.transaction1.id, transaction_ids)
        self.assertIn(self.transaction2.id, transaction_ids)
        self.assertNotIn(self.other_transaction.id, transaction_ids)
    
    def test_transactions_include_milestones(self):
        """Test that transactions include related milestones"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find transaction1 in the response
        transaction1_data = next(
            (t for t in response.data if t['id'] == self.transaction1.id),
            None
        )
        
        self.assertIsNotNone(transaction1_data)
        self.assertIn('milestones', transaction1_data)
        self.assertEqual(len(transaction1_data['milestones']), 2)
        
        # Verify milestone details
        milestone_titles = [m['title'] for m in transaction1_data['milestones']]
        self.assertIn('Milestone 1', milestone_titles)
        self.assertIn('Milestone 2', milestone_titles)
    
    def test_transactions_ordered_by_created_at(self):
        """Test that transactions are ordered by creation date (newest first)"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Since transaction2 was created after transaction1, it should come first
        self.assertEqual(response.data[0]['id'], self.transaction2.id)
        self.assertEqual(response.data[1]['id'], self.transaction1.id)
    
    def test_response_includes_all_expected_fields(self):
        """Test that response includes all expected fields"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction_data = response.data[0]
        
        expected_fields = [
            'id', 'title', 'total_value', 'buyer', 'buyer_username',
            'seller', 'seller_username', 'status', 'created_at', 'milestones'
        ]
        
        for field in expected_fields:
            self.assertIn(field, transaction_data)
    
    def test_empty_list_for_buyer_with_no_transactions(self):
        """Test that buyers with no transactions get an empty list"""
        new_buyer = User.objects.create_user(
            username='newbuyer',
            email='newbuyer@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=new_buyer)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
