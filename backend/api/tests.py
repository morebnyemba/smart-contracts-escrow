from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser, SellerProfile, ServiceCategory


class SellerSearchAPITest(TestCase):
    """Test suite for the seller search API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create service categories
        self.web_dev = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.mobile_dev = ServiceCategory.objects.create(
            name='Mobile Development',
            slug='mobile-development'
        )
        self.design = ServiceCategory.objects.create(
            name='Graphic Design',
            slug='graphic-design'
        )
        
        # Create users and seller profiles
        # Verified seller with web development skill
        self.user1 = CustomUser.objects.create_user(
            username='webdev1',
            email='webdev1@example.com',
            password='testpass123'
        )
        self.seller1 = SellerProfile.objects.create(
            user=self.user1,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        self.seller1.skills.add(self.web_dev)
        
        # Verified seller with multiple skills
        self.user2 = CustomUser.objects.create_user(
            username='fullstack1',
            email='fullstack1@example.com',
            password='testpass123'
        )
        self.seller2 = SellerProfile.objects.create(
            user=self.user2,
            account_type=SellerProfile.AccountType.COMPANY,
            company_name='Tech Solutions Inc',
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        self.seller2.skills.add(self.web_dev, self.mobile_dev)
        
        # Unverified seller with web development skill (should not appear in results)
        self.user3 = CustomUser.objects.create_user(
            username='unverified1',
            email='unverified1@example.com',
            password='testpass123'
        )
        self.seller3 = SellerProfile.objects.create(
            user=self.user3,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.UNVERIFIED
        )
        self.seller3.skills.add(self.web_dev)
        
        # Pending verification seller with design skill
        self.user4 = CustomUser.objects.create_user(
            username='pending1',
            email='pending1@example.com',
            password='testpass123'
        )
        self.seller4 = SellerProfile.objects.create(
            user=self.user4,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.PENDING
        )
        self.seller4.skills.add(self.design)
        
        # Verified seller with only design skill
        self.user5 = CustomUser.objects.create_user(
            username='designer1',
            email='designer1@example.com',
            password='testpass123'
        )
        self.seller5 = SellerProfile.objects.create(
            user=self.user5,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        self.seller5.skills.add(self.design)
        
        self.search_url = reverse('api:seller-search')
    
    def test_search_sellers_by_skill_success(self):
        """Test successful search for sellers with a specific skill"""
        response = self.client.get(self.search_url, {'skill': 'web-development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 verified sellers
        
        # Verify the returned sellers have the correct skill
        usernames = [seller['username'] for seller in response.data]
        self.assertIn('webdev1', usernames)
        self.assertIn('fullstack1', usernames)
        self.assertNotIn('unverified1', usernames)  # Unverified should not appear
    
    def test_search_sellers_only_returns_verified(self):
        """Test that only verified sellers are returned"""
        response = self.client.get(self.search_url, {'skill': 'web-development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for seller in response.data:
            self.assertEqual(seller['verification_status'], 'VERIFIED')
    
    def test_search_sellers_different_skill(self):
        """Test search for sellers with a different skill"""
        response = self.client.get(self.search_url, {'skill': 'graphic-design'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only 1 verified designer
        self.assertEqual(response.data[0]['username'], 'designer1')
    
    def test_search_sellers_no_skill_parameter(self):
        """Test that request without skill parameter returns error"""
        response = self.client.get(self.search_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('required', response.data['error'].lower())
    
    def test_search_sellers_nonexistent_skill(self):
        """Test search for a skill that doesn't exist"""
        response = self.client.get(self.search_url, {'skill': 'nonexistent-skill'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('not found', response.data['error'].lower())
    
    def test_search_sellers_no_matches(self):
        """Test search for skill with no verified sellers"""
        # Create a new skill with no verified sellers
        new_skill = ServiceCategory.objects.create(
            name='Data Science',
            slug='data-science'
        )
        
        response = self.client.get(self.search_url, {'skill': 'data-science'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_response_includes_all_required_fields(self):
        """Test that response includes all expected fields"""
        response = self.client.get(self.search_url, {'skill': 'web-development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        seller = response.data[0]
        required_fields = [
            'public_seller_id',
            'username',
            'account_type',
            'company_name',
            'verification_status',
            'skills'
        ]
        for field in required_fields:
            self.assertIn(field, seller)
    
    def test_skills_field_includes_details(self):
        """Test that skills field includes skill name and slug"""
        response = self.client.get(self.search_url, {'skill': 'web-development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        seller = response.data[0]
        self.assertIsInstance(seller['skills'], list)
        self.assertGreater(len(seller['skills']), 0)
        
        skill = seller['skills'][0]
        self.assertIn('name', skill)
        self.assertIn('slug', skill)
