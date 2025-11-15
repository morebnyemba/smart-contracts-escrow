from django.test import TestCase
from django.db import IntegrityError
from .models import ServiceCategory, CustomUser, SellerProfile

class ServiceCategoryModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.category = ServiceCategory.objects.create(
            name="Web Development",
            slug="web-development"
        )

    def test_service_category_creation(self):
        """Test that a ServiceCategory can be created"""
        self.assertIsInstance(self.category, ServiceCategory)
        self.assertEqual(self.category.name, "Web Development")
        self.assertEqual(self.category.slug, "web-development")

    def test_service_category_str_representation(self):
        """Test the string representation of ServiceCategory"""
        self.assertEqual(str(self.category), "Web Development")

    def test_service_category_unique_name(self):
        """Test that ServiceCategory name must be unique"""
        with self.assertRaises(IntegrityError):
            ServiceCategory.objects.create(
                name="Web Development",
                slug="web-development-2"
            )

    def test_service_category_unique_slug(self):
        """Test that ServiceCategory slug must be unique"""
        with self.assertRaises(IntegrityError):
            ServiceCategory.objects.create(
                name="Web Development 2",
                slug="web-development"
            )

    def test_service_category_ordering(self):
        """Test that ServiceCategories are ordered by name"""
        ServiceCategory.objects.create(name="Graphic Design", slug="graphic-design")
        ServiceCategory.objects.create(name="App Development", slug="app-development")
        
        categories = ServiceCategory.objects.all()
        self.assertEqual(categories[0].name, "App Development")
        self.assertEqual(categories[1].name, "Graphic Design")
        self.assertEqual(categories[2].name, "Web Development")

    def test_service_category_verbose_names(self):
        """Test the verbose names are correct"""
        self.assertEqual(ServiceCategory._meta.verbose_name, "Service Category")
        self.assertEqual(ServiceCategory._meta.verbose_name_plural, "Service Categories")

    def test_service_category_relationship_with_seller_profile(self):
        """Test that ServiceCategory can be linked to SellerProfile"""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        seller_profile = SellerProfile.objects.create(
            user=user,
            account_type=SellerProfile.AccountType.INDIVIDUAL
        )
        
        # Add service category to seller's skills
        seller_profile.skills.add(self.category)
        
        # Test the relationship
        self.assertIn(self.category, seller_profile.skills.all())
        self.assertIn(seller_profile, self.category.sellers.all())

    def test_multiple_categories_for_seller(self):
        """Test that a seller can have multiple service categories"""
        user = CustomUser.objects.create_user(
            username="multiuser",
            email="multi@example.com",
            password="testpass123"
        )
        seller_profile = SellerProfile.objects.create(
            user=user,
            account_type=SellerProfile.AccountType.INDIVIDUAL
        )
        
        category2 = ServiceCategory.objects.create(
            name="Mobile Development",
            slug="mobile-development"
        )
        
        seller_profile.skills.add(self.category, category2)
        
        self.assertEqual(seller_profile.skills.count(), 2)
        self.assertIn(self.category, seller_profile.skills.all())
        self.assertIn(category2, seller_profile.skills.all())
