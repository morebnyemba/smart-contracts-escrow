from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import EscrowTransaction, Milestone

User = get_user_model()


class BuyerTransactionViewSetTest(TestCase):
    """Test suite for the buyer transactions API endpoint."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        
        # Create test users
        self.buyer = User.objects.create_user(
            username='buyer_user',
            email='buyer@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller_user',
            email='seller@example.com',
            password='testpass123'
        )
        self.other_buyer = User.objects.create_user(
            username='other_buyer',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create transactions for the buyer
        self.transaction1 = EscrowTransaction.objects.create(
            title='Website Development',
            total_value=Decimal('1000.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        self.transaction2 = EscrowTransaction.objects.create(
            title='Logo Design',
            total_value=Decimal('500.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.COMPLETED
        )
        
        # Create transaction for another buyer (should not be visible)
        self.other_transaction = EscrowTransaction.objects.create(
            title='App Development',
            total_value=Decimal('2000.00'),
            buyer=self.other_buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        # Create milestones for transaction1
        self.milestone1 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Initial Setup',
            description='Set up development environment',
            value=Decimal('300.00'),
            status=Milestone.MilestoneStatus.COMPLETED
        )
        
        self.milestone2 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Feature Development',
            description='Develop core features',
            value=Decimal('700.00'),
            status=Milestone.MilestoneStatus.PENDING
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the endpoint."""
        response = self.client.get('/api/buyer/my-transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_buyer_transactions(self):
        """Test that buyers can list only their own transactions."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/buyer/my-transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check transactions are ordered by most recent first
        self.assertEqual(response.data['results'][0]['title'], 'Logo Design')
        self.assertEqual(response.data['results'][1]['title'], 'Website Development')
    
    def test_buyer_only_sees_own_transactions(self):
        """Test that buyers cannot see other buyers' transactions."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get('/api/buyer/my-transactions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction_ids = [t['id'] for t in response.data['results']]
        
        self.assertIn(self.transaction1.id, transaction_ids)
        self.assertIn(self.transaction2.id, transaction_ids)
        self.assertNotIn(self.other_transaction.id, transaction_ids)
    
    def test_retrieve_transaction_detail(self):
        """Test retrieving details of a specific transaction."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(f'/api/buyer/my-transactions/{self.transaction1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Website Development')
        self.assertEqual(Decimal(response.data['total_value']), Decimal('1000.00'))
        self.assertEqual(response.data['status'], 'IN_ESCROW')
    
    def test_transaction_includes_milestones(self):
        """Test that transaction details include related milestones."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(f'/api/buyer/my-transactions/{self.transaction1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['milestones']), 2)
        
        milestone_titles = [m['title'] for m in response.data['milestones']]
        self.assertIn('Initial Setup', milestone_titles)
        self.assertIn('Feature Development', milestone_titles)
    
    def test_transaction_includes_user_names(self):
        """Test that transaction includes buyer and seller names."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(f'/api/buyer/my-transactions/{self.transaction1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['buyer_name'], 'buyer_user')
        self.assertEqual(response.data['seller_name'], 'seller_user')
    
    def test_buyer_cannot_access_others_transaction(self):
        """Test that buyers cannot retrieve other buyers' transactions."""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(f'/api/buyer/my-transactions/{self.other_transaction.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_readonly_viewset(self):
        """Test that the viewset is read-only (no POST, PUT, DELETE)."""
        self.client.force_authenticate(user=self.buyer)
        
        # Test POST
        response = self.client.post('/api/buyer/my-transactions/', {
            'title': 'New Transaction',
            'total_value': '1500.00'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test PUT
        response = self.client.put(f'/api/buyer/my-transactions/{self.transaction1.id}/', {
            'title': 'Updated Title',
            'total_value': '1500.00'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test DELETE
        response = self.client.delete(f'/api/buyer/my-transactions/{self.transaction1.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
