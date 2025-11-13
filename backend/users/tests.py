from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from .models import SellerProfile, ServiceCategory

User = get_user_model()


class CustomUserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a user with email and username"""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_email_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='duplicate@example.com',
            password='pass123'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='duplicate@example.com',
                password='pass123'
            )

    def test_user_str_representation(self):
        """Test the string representation of the user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.assertEqual(str(user), 'testuser')


class SellerProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='pass123'
        )

    def test_create_seller_profile(self):
        """Test creating a seller profile"""
        profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.INDIVIDUAL
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.account_type, SellerProfile.AccountType.INDIVIDUAL)
        self.assertEqual(profile.verification_status, SellerProfile.VerificationStatus.UNVERIFIED)
        self.assertIsNotNone(profile.public_seller_id)

    def test_seller_profile_company(self):
        """Test creating a company seller profile"""
        profile = SellerProfile.objects.create(
            user=self.user,
            account_type=SellerProfile.AccountType.COMPANY,
            company_name='Test Company LLC'
        )
        self.assertEqual(profile.account_type, SellerProfile.AccountType.COMPANY)
        self.assertEqual(profile.company_name, 'Test Company LLC')

    def test_seller_profile_one_to_one_relationship(self):
        """Test that one user can only have one seller profile"""
        SellerProfile.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            SellerProfile.objects.create(user=self.user)


class ServiceCategoryModelTests(TestCase):
    def test_create_service_category(self):
        """Test creating a service category"""
        category = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        self.assertEqual(category.name, 'Web Development')
        self.assertEqual(category.slug, 'web-development')

    def test_service_category_unique_name(self):
        """Test that service category name must be unique"""
        ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        with self.assertRaises(IntegrityError):
            ServiceCategory.objects.create(
                name='Web Development',
                slug='web-dev'
            )

    def test_service_category_many_to_many_with_seller(self):
        """Test many-to-many relationship between service category and seller"""
        user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='pass123'
        )
        profile = SellerProfile.objects.create(user=user)
        
        category1 = ServiceCategory.objects.create(
            name='Web Development',
            slug='web-development'
        )
        category2 = ServiceCategory.objects.create(
            name='Mobile Development',
            slug='mobile-development'
        )
        
        profile.skills.add(category1, category2)
        self.assertEqual(profile.skills.count(), 2)
        self.assertIn(category1, profile.skills.all())
        self.assertIn(category2, profile.skills.all())
