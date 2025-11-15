from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser, SellerProfile, ServiceCategory


class SellerDiscoveryAPITest(APITestCase):
    """Test cases for Seller Discovery API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create service categories
        self.web_dev = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.design = ServiceCategory.objects.create(
            name='Graphic Design',
            slug='graphic-design'
        )
        
        # Create users and seller profiles
        self.user1 = CustomUser.objects.create_user(
            username='john_dev',
            email='john@example.com',
            password='password123'
        )
        self.seller1 = SellerProfile.objects.create(
            user=self.user1,
            account_type='INDIVIDUAL',
            verification_status='VERIFIED'
        )
        self.seller1.skills.add(self.web_dev)
        
        self.user2 = CustomUser.objects.create_user(
            username='jane_design',
            email='jane@example.com',
            password='password123'
        )
        self.seller2 = SellerProfile.objects.create(
            user=self.user2,
            account_type='INDIVIDUAL',
            verification_status='VERIFIED'
        )
        self.seller2.skills.add(self.design)
        
        self.user3 = CustomUser.objects.create_user(
            username='bob_pending',
            email='bob@example.com',
            password='password123'
        )
        self.seller3 = SellerProfile.objects.create(
            user=self.user3,
            account_type='INDIVIDUAL',
            verification_status='PENDING'
        )
    
    def test_list_all_sellers(self):
        """Test listing all sellers."""
        response = self.client.get('/api/sellers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
    
    def test_list_verified_sellers_only(self):
        """Test listing only verified sellers."""
        response = self.client.get('/api/sellers/verified/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        for seller in response.data['results']:
            self.assertEqual(seller['verification_status'], 'VERIFIED')
    
    def test_filter_by_verification_status(self):
        """Test filtering sellers by verification status."""
        response = self.client.get('/api/sellers/?verification_status=PENDING')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'bob_pending')
    
    def test_search_sellers_by_skill(self):
        """Test searching sellers by skill name."""
        response = self.client.get('/api/sellers/?search=Web Development')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
    
    def test_filter_by_skill_slug(self):
        """Test filtering sellers by skill slug."""
        response = self.client.get('/api/sellers/?skills=web-development')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'john_dev')
    
    def test_list_service_categories(self):
        """Test listing all service categories."""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_seller_profile_contains_required_fields(self):
        """Test that seller profile response contains all required fields."""
        response = self.client.get('/api/sellers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seller = response.data['results'][0]
        required_fields = [
            'id', 'public_seller_id', 'username', 'email',
            'account_type', 'company_name', 'verification_status', 'skills'
        ]
        for field in required_fields:
            self.assertIn(field, seller)
