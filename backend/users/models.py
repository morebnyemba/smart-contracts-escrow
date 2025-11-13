from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

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

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_profile')
    public_seller_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, default=AccountType.INDIVIDUAL)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.UNVERIFIED)
    skills = models.ManyToManyField(ServiceCategory, related_name='sellers', blank=True)