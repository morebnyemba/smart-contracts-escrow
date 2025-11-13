#!/usr/bin/env python
"""Script to create test data for seller discovery."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import CustomUser, SellerProfile, ServiceCategory

# Create service categories
categories_data = [
    {'name': 'Web Development', 'slug': 'web-development'},
    {'name': 'Mobile Development', 'slug': 'mobile-development'},
    {'name': 'Graphic Design', 'slug': 'graphic-design'},
    {'name': 'Content Writing', 'slug': 'content-writing'},
    {'name': 'SEO Services', 'slug': 'seo-services'},
]

categories = {}
for cat_data in categories_data:
    category, created = ServiceCategory.objects.get_or_create(**cat_data)
    categories[cat_data['slug']] = category
    print(f"{'Created' if created else 'Found'} category: {category.name}")

# Create test sellers
sellers_data = [
    {
        'username': 'john_dev',
        'email': 'john@example.com',
        'password': 'password123',
        'account_type': 'INDIVIDUAL',
        'verification_status': 'VERIFIED',
        'skills': ['web-development', 'mobile-development'],
    },
    {
        'username': 'jane_design',
        'email': 'jane@example.com',
        'password': 'password123',
        'account_type': 'INDIVIDUAL',
        'company_name': '',
        'verification_status': 'VERIFIED',
        'skills': ['graphic-design'],
    },
    {
        'username': 'acme_corp',
        'email': 'contact@acmecorp.com',
        'password': 'password123',
        'account_type': 'COMPANY',
        'company_name': 'ACME Corporation',
        'verification_status': 'VERIFIED',
        'skills': ['web-development', 'seo-services', 'content-writing'],
    },
    {
        'username': 'bob_writer',
        'email': 'bob@example.com',
        'password': 'password123',
        'account_type': 'INDIVIDUAL',
        'verification_status': 'PENDING',
        'skills': ['content-writing'],
    },
    {
        'username': 'charlie_seo',
        'email': 'charlie@example.com',
        'password': 'password123',
        'account_type': 'INDIVIDUAL',
        'verification_status': 'UNVERIFIED',
        'skills': ['seo-services'],
    },
]

for seller_data in sellers_data:
    skill_slugs = seller_data.pop('skills')
    account_type = seller_data.pop('account_type')
    company_name = seller_data.pop('company_name', '')
    verification_status = seller_data.pop('verification_status')
    
    # Create user
    user, created = CustomUser.objects.get_or_create(
        username=seller_data['username'],
        email=seller_data['email'],
        defaults={'password': seller_data['password']}
    )
    if created:
        user.set_password(seller_data['password'])
        user.save()
    
    # Create seller profile
    profile, created = SellerProfile.objects.get_or_create(
        user=user,
        defaults={
            'account_type': account_type,
            'company_name': company_name,
            'verification_status': verification_status,
        }
    )
    
    # Add skills
    for slug in skill_slugs:
        if slug in categories:
            profile.skills.add(categories[slug])
    
    print(f"{'Created' if created else 'Updated'} seller: {user.username} ({verification_status})")

print("\nTest data creation complete!")
