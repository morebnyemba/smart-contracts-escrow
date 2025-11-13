from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ServiceCategory, SellerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_type', 'verification_status', 'created_at', 'is_verified']
    list_filter = ['account_type', 'verification_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name']
    readonly_fields = ['public_seller_id', 'created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'public_seller_id')
        }),
        ('Profile Details', {
            'fields': ('account_type', 'company_name', 'bio', 'profile_picture', 'skills')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_document', 'verification_notes', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ['skills']
