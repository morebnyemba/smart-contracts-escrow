from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import CustomUser, ServiceCategory, SellerProfile
import uuid


User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests for CustomUser model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        """Test that a user can be created with email"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str_method(self):
        """Test the string representation of user"""
        self.assertEqual(str(self.user), 'testuser')

    def test_email_uniqueness(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='testpass123'
            )


class ServiceCategoryModelTest(TestCase):
    """Tests for ServiceCategory model"""

    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )

    def test_category_creation(self):
        """Test that a service category can be created"""
        self.assertEqual(self.category.name, 'Web Development')
        self.assertEqual(self.category.slug, 'web-development')

    def test_category_str_method(self):
        """Test the string representation of category"""
        self.assertEqual(str(self.category), 'Web Development')

    def test_category_ordering(self):
        """Test that categories are ordered by name"""
        ServiceCategory.objects.create(name='App Development', slug='app-development')
        ServiceCategory.objects.create(name='Design', slug='design')
        categories = ServiceCategory.objects.all()
        self.assertEqual(categories[0].name, 'App Development')
        self.assertEqual(categories[1].name, 'Design')
        self.assertEqual(categories[2].name, 'Web Development')


class SellerProfileModelTest(TestCase):
    """Tests for SellerProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='selleruser',
            email='seller@example.com',
            password='sellerpass123'
        )
        self.category1 = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.category2 = ServiceCategory.objects.create(
            name='Design',
            slug='design'
        )

    def test_seller_profile_creation_individual(self):
        """Test creating an individual seller profile"""
        profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.INDIVIDUAL,
            bio='Experienced web developer'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.account_type, SellerProfile.AccountType.INDIVIDUAL)
        self.assertEqual(profile.bio, 'Experienced web developer')
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.UNVERIFIED)

    def test_seller_profile_creation_company(self):
        """Test creating a company seller profile"""
        profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.COMPANY,
            company_name='Tech Solutions Inc',
            bio='Leading tech company'
        )
        self.assertEqual(profile.account_type, SellerProfile.AccountType.COMPANY)
        self.assertEqual(profile.company_name, 'Tech Solutions Inc')

    def test_public_seller_id_is_uuid(self):
        """Test that public_seller_id is a valid UUID"""
        profile = SellerProfile.objects.create(user=self.user)
        self.assertIsInstance(profile.public_seller_id, uuid.UUID)

    def test_public_seller_id_is_unique(self):
        """Test that public_seller_id is unique for each profile"""
        user2 = User.objects.create_user(
            username='selleruser2',
            email='seller2@example.com',
            password='sellerpass123'
        )
        profile1 = SellerProfile.objects.create(user=self.user)
        profile2 = SellerProfile.objects.create(user=user2)
        self.assertNotEqual(profile1.public_seller_id, profile2.public_seller_id)

    def test_seller_profile_str_with_company_name(self):
        """Test string representation with company name"""
        profile = SellerProfile.objects.create(
            user=self.user,
            company_name='Tech Solutions Inc'
        )
        self.assertEqual(str(profile), 'Tech Solutions Inc (selleruser)')

    def test_seller_profile_str_without_company_name(self):
        """Test string representation without company name"""
        profile = SellerProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "selleruser's Seller Profile")

    def test_is_verified_method_true(self):
        """Test is_verified method returns True for verified profiles"""
        profile = SellerProfile.objects.create(
            user=self.user,
            verification_status=SellerProfile.VerificationStatus.VERIFIED
        )
        self.assertTrue(profile.is_verified())

    def test_is_verified_method_false(self):
        """Test is_verified method returns False for unverified profiles"""
        profile = SellerProfile.objects.create(
            user=self.user,
            verification_status=SellerProfile.VerificationStatus.UNVERIFIED
        )
        self.assertFalse(profile.is_verified())

    def test_verification_status_choices(self):
        """Test all verification status choices"""
        profile = SellerProfile.objects.create(user=self.user)
        
        # Test UNVERIFIED (default)
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.UNVERIFIED)
        
        # Test PENDING
        profile.verification_status = SellerProfile.VerificationStatus.PENDING
        profile.save()
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.PENDING)
        
        # Test VERIFIED
        profile.verification_status = SellerProfile.VerificationStatus.VERIFIED
        profile.verified_at = timezone.now()
        profile.save()
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.VERIFIED)
        self.assertIsNotNone(profile.verified_at)
        
        # Test REJECTED
        profile.verification_status = SellerProfile.VerificationStatus.REJECTED
        profile.verification_notes = 'Invalid documents'
        profile.save()
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.REJECTED)
        self.assertEqual(profile.verification_notes, 'Invalid documents')

    def test_skills_many_to_many(self):
        """Test that seller can have multiple skills"""
        profile = SellerProfile.objects.create(user=self.user)
        profile.skills.add(self.category1, self.category2)
        
        self.assertEqual(profile.skills.count(), 2)
        self.assertIn(self.category1, profile.skills.all())
        self.assertIn(self.category2, profile.skills.all())

    def test_one_to_one_relationship_with_user(self):
        """Test that a user can only have one seller profile"""
        SellerProfile.objects.create(user=self.user)
        
        with self.assertRaises(Exception):
            SellerProfile.objects.create(user=self.user)

    def test_timestamps_are_auto_set(self):
        """Test that created_at and updated_at are automatically set"""
        profile = SellerProfile.objects.create(user=self.user)
        
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        
        # Test that updated_at changes on update
        original_updated_at = profile.updated_at
        profile.bio = 'Updated bio'
        profile.save()
        
        self.assertGreater(profile.updated_at, original_updated_at)

    def test_seller_profile_ordering(self):
        """Test that profiles are ordered by created_at descending"""
        user2 = User.objects.create_user(
            username='selleruser2',
            email='seller2@example.com',
            password='pass123'
        )
        user3 = User.objects.create_user(
            username='selleruser3',
            email='seller3@example.com',
            password='pass123'
        )
        
        profile1 = SellerProfile.objects.create(user=self.user)
        profile2 = SellerProfile.objects.create(user=user2)
        profile3 = SellerProfile.objects.create(user=user3)
        
        profiles = SellerProfile.objects.all()
        # Most recently created should be first
        self.assertEqual(profiles[0].id, profile3.id)
        self.assertEqual(profiles[1].id, profile2.id)
        self.assertEqual(profiles[2].id, profile1.id)
