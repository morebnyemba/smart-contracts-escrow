from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import CustomUser, SellerProfile, ServiceCategory
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


class SellerOnboardingAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data for seller onboarding tests."""
        # Create a user
        self.user = CustomUser.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpassword123'
        )
        
        # Create service categories
        self.category1 = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.category2 = ServiceCategory.objects.create(
            name='Design',
            slug='design'
        )
    
    def test_create_seller_profile_without_authentication(self):
        """Test that unauthenticated users cannot create seller profile"""
        url = reverse('seller-onboarding')
        data = {
            'account_type': 'INDIVIDUAL',
            'bio': 'Test bio',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_seller_profile_minimal(self):
        """Test creating a seller profile with minimal data"""
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        data = {
            'account_type': 'INDIVIDUAL',
            'bio': 'I am a web developer with 5 years of experience.',
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['account_type'], 'INDIVIDUAL')
        self.assertEqual(response.data['bio'], 'I am a web developer with 5 years of experience.')
        self.assertEqual(response.data['verification_status'], 'UNVERIFIED')
        
        # Verify profile was created in database
        seller_profile = SellerProfile.objects.get(user=self.user)
        self.assertEqual(seller_profile.account_type, 'INDIVIDUAL')
        self.assertEqual(seller_profile.verification_status, SellerProfile.VerificationStatus.UNVERIFIED)
    
    def test_create_seller_profile_with_skills(self):
        """Test creating a seller profile with skills"""
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        data = {
            'account_type': 'INDIVIDUAL',
            'bio': 'Designer and developer',
            'skill_ids': [self.category1.id, self.category2.id]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['skills']), 2)
        
        # Verify skills were added
        seller_profile = SellerProfile.objects.get(user=self.user)
        self.assertEqual(seller_profile.skills.count(), 2)
    
    def test_create_seller_profile_company(self):
        """Test creating a company seller profile"""
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        data = {
            'account_type': 'COMPANY',
            'company_name': 'Test Company LLC',
            'bio': 'We provide professional web services',
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['account_type'], 'COMPANY')
        self.assertEqual(response.data['company_name'], 'Test Company LLC')
    
    def test_create_seller_profile_with_verification_document(self):
        """Test creating a seller profile with verification document sets status to PENDING"""
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        # Create a simple test file
        verification_doc = SimpleUploadedFile(
            "verification.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'account_type': 'INDIVIDUAL',
            'bio': 'Test bio',
            'verification_document': verification_doc,
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['verification_status'], 'PENDING')
        
        # Verify in database
        seller_profile = SellerProfile.objects.get(user=self.user)
        self.assertEqual(seller_profile.verification_status, SellerProfile.VerificationStatus.PENDING)
        self.assertIsNotNone(seller_profile.verification_document)
    
    def test_update_existing_seller_profile(self):
        """Test updating an existing seller profile"""
        # Create initial seller profile
        seller_profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            bio='Original bio',
            verification_status=SellerProfile.VerificationStatus.UNVERIFIED
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        data = {
            'bio': 'Updated bio with more information',
            'account_type': 'COMPANY',
            'company_name': 'New Company',
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio with more information')
        self.assertEqual(response.data['company_name'], 'New Company')
        
        # Verify update in database
        seller_profile.refresh_from_db()
        self.assertEqual(seller_profile.bio, 'Updated bio with more information')
        self.assertEqual(seller_profile.company_name, 'New Company')
    
    def test_update_verification_document_sets_pending(self):
        """Test that updating verification document sets status to PENDING"""
        # Create initial seller profile
        seller_profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            bio='Original bio',
            verification_status=SellerProfile.VerificationStatus.UNVERIFIED
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('seller-onboarding')
        
        verification_doc = SimpleUploadedFile(
            "new_verification.pdf",
            b"new_file_content",
            content_type="application/pdf"
        )
        
        data = {
            'verification_document': verification_doc,
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['verification_status'], 'PENDING')
        
        # Verify in database
        seller_profile.refresh_from_db()
        self.assertEqual(seller_profile.verification_status, SellerProfile.VerificationStatus.PENDING)
