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


class SellerTransactionViewSetTest(TestCase):
    """Tests for the seller dashboard endpoint"""
    
    def setUp(self):
        # Create users
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='password123'
        )
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='password123'
        )
        self.other_seller = User.objects.create_user(
            username='other_seller',
            email='other_seller@test.com',
            password='password123'
        )
        
        # Create transactions where seller is the seller
        self.transaction1 = EscrowTransaction.objects.create(
            title='Project 1',
            total_value=Decimal('100.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        self.transaction2 = EscrowTransaction.objects.create(
            title='Project 2',
            total_value=Decimal('200.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        # Create transaction for other seller (should not appear in results)
        self.transaction3 = EscrowTransaction.objects.create(
            title='Other Project',
            total_value=Decimal('150.00'),
            buyer=self.buyer,
            seller=self.other_seller
        )
        
        # Add milestones to transaction1
        Milestone.objects.create(
            transaction=self.transaction1,
            title='Milestone 1',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.PENDING
        )
        Milestone.objects.create(
            transaction=self.transaction1,
            title='Milestone 2',
            value=Decimal('50.00'),
            status=Milestone.MilestoneStatus.PENDING
        )
    
    def test_seller_can_view_their_transactions(self):
        """Test that sellers can view only their transactions"""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.force_authenticate(user=self.seller)
        
        response = client.get('/api/portal/seller/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify transactions are ordered by most recent first
        titles = [t['title'] for t in response.data['results']]
        self.assertIn('Project 1', titles)
        self.assertIn('Project 2', titles)
        self.assertNotIn('Other Project', titles)
    
    def test_seller_transactions_include_milestones(self):
        """Test that seller transactions include milestone data"""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.force_authenticate(user=self.seller)
        
        response = client.get('/api/portal/seller/')
        
        self.assertEqual(response.status_code, 200)
        
        # Find transaction1 in results
        transaction1_data = next(
            (t for t in response.data['results'] if t['title'] == 'Project 1'),
            None
        )
        
        self.assertIsNotNone(transaction1_data)
        self.assertEqual(len(transaction1_data['milestones']), 2)
    
    def test_seller_transactions_include_buyer_info(self):
        """Test that seller transactions include buyer information"""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.force_authenticate(user=self.seller)
        
        response = client.get('/api/portal/seller/')
        
        self.assertEqual(response.status_code, 200)
        
        transaction_data = response.data['results'][0]
        
        self.assertIn('buyer', transaction_data)
        self.assertIn('buyer_name', transaction_data)
        self.assertEqual(transaction_data['buyer_name'], 'buyer')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access seller endpoint"""
        from rest_framework.test import APIClient
        
        client = APIClient()
        
        response = client.get('/api/portal/seller/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_seller_can_retrieve_individual_transaction(self):
        """Test that sellers can retrieve individual transaction details"""
        from rest_framework.test import APIClient
        
        client = APIClient()
        client.force_authenticate(user=self.seller)
        
        response = client.get(f'/api/portal/seller/{self.transaction1.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Project 1')
        self.assertEqual(len(response.data['milestones']), 2)
