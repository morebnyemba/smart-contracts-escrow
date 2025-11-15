from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import SellerProfile, ServiceCategory

User = get_user_model()


class UserAuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/auth/register/'
        self.login_url = '/api/users/auth/login/'
        self.user_url = '/api/users/auth/user/'

    def test_user_registration(self):
        """Test user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'different123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_current_user(self):
        """Test getting current authenticated user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication"""
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SellerOnboardingTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.create_url = '/api/users/seller/profile/create/'
        self.profile_url = '/api/users/seller/profile/'

    def test_create_seller_profile(self):
        """Test creating a seller profile"""
        self.client.force_authenticate(user=self.user)
        data = {
            'account_type': 'INDIVIDUAL',
            'skill_ids': [self.category.id]
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['account_type'], 'INDIVIDUAL')
        self.assertTrue(SellerProfile.objects.filter(user=self.user).exists())

    def test_create_seller_profile_unauthorized(self):
        """Test creating seller profile without authentication"""
        data = {
            'account_type': 'INDIVIDUAL'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_seller_profile(self):
        """Test retrieving seller profile"""
        seller_profile = SellerProfile.objects.create(
            user=self.user,
            account_type='INDIVIDUAL'
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_type'], 'INDIVIDUAL')

    def test_update_seller_profile(self):
        """Test updating seller profile"""
        seller_profile = SellerProfile.objects.create(
            user=self.user,
            account_type='INDIVIDUAL'
        )
        self.client.force_authenticate(user=self.user)
        data = {
            'account_type': 'COMPANY',
            'company_name': 'Test Company'
        }
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_type'], 'COMPANY')
        self.assertEqual(response.data['company_name'], 'Test Company')
