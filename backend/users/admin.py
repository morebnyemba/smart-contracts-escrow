from django.contrib import admin
from django.utils import timezone
from .models import CustomUser, ServiceCategory, SellerProfile
from .tasks import send_verification_notification

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_type', 'verification_status', 'verified_at', 'public_seller_id']
    list_filter = ['account_type', 'verification_status']
    search_fields = ['user__username', 'user__email', 'company_name']
    filter_horizontal = ['skills']
    actions = ['approve_sellers', 'reject_sellers']
    readonly_fields = ['public_seller_id', 'created_at', 'updated_at', 'verified_at']
    
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
    
    @admin.action(description='Approve selected sellers')
    def approve_sellers(self, request, queryset):
        """Approve selected seller profiles and send notifications."""
        count = 0
        failed_notifications = 0
        for seller_profile in queryset:
            seller_profile.verification_status = SellerProfile.VerificationStatus.VERIFIED
            seller_profile.verified_at = timezone.now()
            seller_profile.save()
            
            # Send notification to the seller
            try:
                send_verification_notification.delay(
                    user_id=seller_profile.user.id,
                    verification_status='VERIFIED'
                )
            except Exception as e:
                failed_notifications += 1
            count += 1
        
        if failed_notifications > 0:
            self.message_user(
                request,
                f'{count} seller profile(s) have been approved, but {failed_notifications} notification(s) failed to send.',
                level='warning'
            )
        else:
            self.message_user(
                request,
                f'{count} seller profile(s) have been approved and notifications sent.'
            )
    
    @admin.action(description='Reject selected sellers')
    def reject_sellers(self, request, queryset):
        """Reject selected seller profiles and send notifications."""
        count = 0
        failed_notifications = 0
        for seller_profile in queryset:
            seller_profile.verification_status = SellerProfile.VerificationStatus.REJECTED
            seller_profile.verified_at = None
            seller_profile.save()
            
            # Send notification to the seller
            try:
                send_verification_notification.delay(
                    user_id=seller_profile.user.id,
                    verification_status='REJECTED'
                )
            except Exception as e:
                failed_notifications += 1
            count += 1
        
        if failed_notifications > 0:
            self.message_user(
                request,
                f'{count} seller profile(s) have been rejected, but {failed_notifications} notification(s) failed to send.',
                level='warning'
            )
        else:
            self.message_user(
                request,
                f'{count} seller profile(s) have been rejected and notifications sent.'
            )

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']
