from rest_framework import serializers
from .models import SellerProfile, ServiceCategory, CustomUser
from wallets.models import UserWallet


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'slug']


class SellerProfileSerializer(serializers.ModelSerializer):
    skills = ServiceCategorySerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SellerProfile
        fields = [
            'id',
            'public_seller_id',
            'username',
            'email',
            'account_type',
            'company_name',
            'verification_status',
            'skills',
        ]
        read_only_fields = ['public_seller_id', 'verification_status']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
    
    def validate_password(self, value):
        """Validate password using Django's password validators."""
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        return value
    
    def create(self, validated_data):
        # Create user with hashed password
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create associated wallet
        UserWallet.objects.create(user=user, balance=0.00)
        
        return user
