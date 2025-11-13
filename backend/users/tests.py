from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test user registration endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        # Ensure password is not returned
        self.assertNotIn('password', response.data['user'])

    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(username='testuser', email='first@example.com', password='TestPass123!')
        data = {
            'username': 'testuser',
            'email': 'second@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(username='firstuser', email='test@example.com', password='TestPass123!')
        data = {
            'username': 'seconduser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationTestCase(APITestCase):
    """Test JWT token authentication"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token-obtain-pair')
        self.refresh_url = reverse('token-refresh')
        self.profile_url = reverse('user-profile')
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_login_success(self):
        """Test successful login returns access and refresh tokens"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh endpoint"""
        # First login to get tokens
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Use refresh token to get new access token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token"""
        # Login to get access token
        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']

        # Access protected endpoint with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token fails"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token fails"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
