from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SellerProfile, ServiceCategory


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'public_seller_id', 'account_type', 'verification_status']
    list_filter = ['account_type', 'verification_status']
    search_fields = ['user__username', 'user__email', 'company_name']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
