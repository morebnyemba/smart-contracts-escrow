from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from wallets.models import UserWallet


class JWTAuthenticationTestCase(TestCase):
    """Test suite for JWT authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.user_url = reverse('auth-user')
        self.refresh_url = reverse('token-refresh')
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test user registration creates user and returns JWT tokens"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        
        # Check user was created
        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        
        # Check wallet was created
        wallet = UserWallet.objects.get(user=user)
        self.assertIsNotNone(wallet)
    
    def test_user_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        data = self.valid_user_data.copy()
        data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create first user
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Try to create another user with same username
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login returns JWT tokens"""
        # Register user first
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        # Register user first
        self.client.post(self.register_url, self.valid_user_data, format='json')
        
        # Try to login with wrong password
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_current_user(self):
        """Test getting current user details with JWT authentication"""
        # Register and get tokens
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        access_token = response.data['tokens']['access']
        
        # Get current user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.user_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertIn('is_seller', response.data)
        self.assertFalse(response.data['is_seller'])
    
    def test_get_current_user_without_authentication(self):
        """Test getting current user fails without authentication"""
        response = self.client.get(self.user_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test refreshing JWT access token"""
        # Register and get tokens
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        refresh_token = response.data['tokens']['refresh']
        
        # Refresh token
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_is_seller_property(self):
        """Test is_seller property returns True when user has seller profile"""
        from users.models import SellerProfile
        
        # Register user
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        user = CustomUser.objects.get(username='testuser')
        
        # Initially should be False
        self.assertFalse(user.is_seller)
        
        # Create seller profile
        SellerProfile.objects.create(user=user)
        
        # Now should be True
        user.refresh_from_db()
        self.assertTrue(user.is_seller)
