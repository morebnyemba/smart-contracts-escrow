from django.contrib import admin
from .models import CustomUser, ServiceCategory, SellerProfile

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_type', 'verification_status', 'public_seller_id']
    list_filter = ['account_type', 'verification_status']
    search_fields = ['user__username', 'user__email', 'company_name']
    filter_horizontal = ['skills']

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']
