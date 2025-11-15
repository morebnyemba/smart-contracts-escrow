from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    
    @property
    def is_seller(self):
        """Check if user has a seller profile"""
        return hasattr(self, 'seller_profile')

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class SellerProfile(models.Model):
    class AccountType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        COMPANY = 'COMPANY', 'Company'
    
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = 'UNVERIFIED', 'Unverified'
        PENDING = 'PENDING', 'Pending Review'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    public_seller_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, default=AccountType.INDIVIDUAL)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Brief description of services and expertise")
    profile_picture = models.ImageField(upload_to='seller_profiles/', blank=True, null=True)
    
    # Verification fields
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.UNVERIFIED)
    verification_notes = models.TextField(blank=True, help_text="Admin notes about verification status")
    verified_at = models.DateTimeField(null=True, blank=True, help_text="Date when profile was verified")
    
    skills = models.ManyToManyField(ServiceCategory, related_name='sellers', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Seller Profile'
        verbose_name_plural = 'Seller Profiles'

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.user.username})"
        return f"{self.user.username}'s Seller Profile"
    
    def is_verified(self):
        """Check if the seller profile is verified"""
        return self.verification_status == self.VerificationStatus.VERIFIED