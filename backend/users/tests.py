from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser, SellerProfile, ServiceCategory
from wallets.models import UserWallet
import uuid


class SellerProfileLookupAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data for seller profile lookup tests."""
        # Create a user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        
        # Create service categories
        self.category1 = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.category2 = ServiceCategory.objects.create(
            name='Mobile Apps',
            slug='mobile-apps'
        )
        
        # Create a seller profile
        self.seller_profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        self.seller_profile.skills.add(self.category1, self.category2)
        
        # Store the public_seller_id for testing
        self.public_seller_id = self.seller_profile.public_seller_id

    def test_lookup_seller_by_public_id_success(self):
        """Test successful lookup of seller by public_seller_id."""
        url = reverse('seller-lookup', kwargs={'public_seller_id': self.public_seller_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['public_seller_id'], str(self.public_seller_id))
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['account_type'], 'INDIVIDUAL')
        self.assertEqual(response.data['verification_status'], 'VERIFIED')
        self.assertEqual(len(response.data['skills']), 2)
        
    def test_lookup_seller_with_company_profile(self):
        """Test lookup of seller with company account type."""
        # Create another user with company profile
        company_user = CustomUser.objects.create_user(
            username='companyuser',
            email='company@example.com',
            password='testpassword123'
        )
        company_profile = SellerProfile.objects.create(
            user=company_user,
            account_type=SellerProfile.AccountType.COMPANY,
            company_name='Test Company LLC',
            verification_status=SellerProfile.VerificationStatus.PENDING
        )
        
        url = reverse('seller-lookup', kwargs={'public_seller_id': company_profile.public_seller_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_type'], 'COMPANY')
        self.assertEqual(response.data['company_name'], 'Test Company LLC')
        self.assertEqual(response.data['verification_status'], 'PENDING')

    def test_lookup_seller_not_found(self):
        """Test lookup with non-existent public_seller_id returns 404."""
        non_existent_id = uuid.uuid4()
        url = reverse('seller-lookup', kwargs={'public_seller_id': non_existent_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lookup_seller_with_no_skills(self):
        """Test lookup of seller with no skills assigned."""
        # Create a seller with no skills
        user_no_skills = CustomUser.objects.create_user(
            username='noskillusers',
            email='noskills@example.com',
            password='testpassword123'
        )
        profile_no_skills = SellerProfile.objects.create(
            user=user_no_skills,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            verification_status=SellerProfile.VerificationStatus.UNVERIFIED
        )
        
        url = reverse('seller-lookup', kwargs={'public_seller_id': profile_no_skills.public_seller_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['skills']), 0)


class UserRegistrationAPITestCase(APITestCase):
    def test_register_user_success(self):
        """Test successful user registration."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User registered successfully')
        
        # Verify user was created
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())
        user = CustomUser.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Verify password is hashed
        self.assertTrue(user.check_password('securepassword123'))
        
        # Verify wallet was created
        self.assertTrue(UserWallet.objects.filter(user=user).exists())
        wallet = UserWallet.objects.get(user=user)
        self.assertEqual(wallet.balance, 0.00)
    
    def test_register_user_missing_username(self):
        """Test registration fails with missing username."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_register_user_missing_email(self):
        """Test registration fails with missing email."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_register_user_missing_password(self):
        """Test registration fails with missing password."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_register_user_duplicate_username(self):
        """Test registration fails with duplicate username."""
        # Create existing user
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        url = reverse('register')
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email."""
        # Create existing user
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_register_endpoint_public(self):
        """Test that registration endpoint doesn't require authentication."""
        url = reverse('register')
        data = {
            'username': 'publicuser',
            'email': 'public@example.com',
            'password': 'securepassword123'
        }
        # Make request without authentication
        response = self.client.post(url, data, format='json')
        
        # Should succeed without authentication
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
