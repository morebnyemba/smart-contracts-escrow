from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import CustomUser
from transactions.models import EscrowTransaction, Milestone
from decimal import Decimal


class MyProjectsAPITestCase(APITestCase):
    """Test cases for the My Projects API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.seller = CustomUser.objects.create_user(
            username='seller1',
            email='seller1@example.com',
            password='testpass123'
        )
        self.buyer = CustomUser.objects.create_user(
            username='buyer1',
            email='buyer1@example.com',
            password='testpass123'
        )
        self.other_seller = CustomUser.objects.create_user(
            username='seller2',
            email='seller2@example.com',
            password='testpass123'
        )
        
        # Create test transactions for seller1
        self.transaction1 = EscrowTransaction.objects.create(
            title='Web Development Project',
            total_value=Decimal('1000.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.WORK_IN_PROGRESS
        )
        
        self.transaction2 = EscrowTransaction.objects.create(
            title='Mobile App Development',
            total_value=Decimal('2000.00'),
            buyer=self.buyer,
            seller=self.seller,
            status=EscrowTransaction.TransactionStatus.IN_ESCROW
        )
        
        # Create a transaction for other_seller
        self.other_transaction = EscrowTransaction.objects.create(
            title='Graphic Design',
            total_value=Decimal('500.00'),
            buyer=self.buyer,
            seller=self.other_seller,
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING
        )
        
        # Create milestones for transaction1
        self.milestone1 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Design Phase',
            description='Complete UI/UX design',
            value=Decimal('300.00'),
            status=Milestone.MilestoneStatus.COMPLETED
        )
        
        self.milestone2 = Milestone.objects.create(
            transaction=self.transaction1,
            title='Development Phase',
            description='Build the application',
            value=Decimal('700.00'),
            status=Milestone.MilestoneStatus.PENDING
        )
        
        self.client = APIClient()
        self.list_url = reverse('my-projects-list')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the endpoint"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_authenticated_seller_gets_only_own_projects(self):
        """Test that sellers only see their own projects"""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that only seller's transactions are returned
        transaction_ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.transaction1.id, transaction_ids)
        self.assertIn(self.transaction2.id, transaction_ids)
        self.assertNotIn(self.other_transaction.id, transaction_ids)
    
    def test_projects_ordered_by_created_date_desc(self):
        """Test that projects are ordered by creation date (newest first)"""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # transaction2 was created after transaction1, so it should be first
        self.assertEqual(results[0]['id'], self.transaction2.id)
        self.assertEqual(results[1]['id'], self.transaction1.id)
    
    def test_project_includes_milestones(self):
        """Test that project response includes nested milestones"""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find transaction1 in results
        transaction1_data = next(
            item for item in response.data['results'] 
            if item['id'] == self.transaction1.id
        )
        
        # Check milestones
        self.assertEqual(len(transaction1_data['milestones']), 2)
        milestone_titles = [m['title'] for m in transaction1_data['milestones']]
        self.assertIn('Design Phase', milestone_titles)
        self.assertIn('Development Phase', milestone_titles)
    
    def test_project_includes_buyer_and_seller_names(self):
        """Test that project response includes buyer and seller names"""
        self.client.force_authenticate(user=self.seller)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = response.data['results'][0]
        
        self.assertIn('buyer_name', project)
        self.assertIn('seller_name', project)
        self.assertEqual(project['seller_name'], 'seller1')
        self.assertEqual(project['buyer_name'], 'buyer1')
    
    def test_project_detail_view(self):
        """Test retrieving a single project detail"""
        self.client.force_authenticate(user=self.seller)
        detail_url = reverse('my-projects-detail', kwargs={'pk': self.transaction1.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction1.id)
        self.assertEqual(response.data['title'], 'Web Development Project')
        self.assertEqual(len(response.data['milestones']), 2)
    
    def test_seller_cannot_access_other_seller_project(self):
        """Test that seller cannot access another seller's project"""
        self.client.force_authenticate(user=self.seller)
        detail_url = reverse('my-projects-detail', kwargs={'pk': self.other_transaction.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_empty_projects_list(self):
        """Test that a seller with no projects gets an empty list"""
        new_seller = CustomUser.objects.create_user(
            username='newseller',
            email='newseller@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=new_seller)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_readonly_endpoint(self):
        """Test that the endpoint is read-only (no POST, PUT, DELETE)"""
        self.client.force_authenticate(user=self.seller)
        
        # Try POST
        post_response = self.client.post(self.list_url, {
            'title': 'New Project',
            'total_value': '500.00'
        })
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try PUT
        detail_url = reverse('my-projects-detail', kwargs={'pk': self.transaction1.id})
        put_response = self.client.put(detail_url, {
            'title': 'Updated Project'
        })
        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try DELETE
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
