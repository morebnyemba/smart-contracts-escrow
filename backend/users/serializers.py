from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
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


class SellerOnboardingSerializer(serializers.ModelSerializer):
    """Serializer for seller onboarding - create and update seller profile"""
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill category IDs"
    )
    skills = ServiceCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = SellerProfile
        fields = [
            'id',
            'public_seller_id',
            'account_type',
            'company_name',
            'bio',
            'profile_picture',
            'verification_document',
            'verification_status',
            'skill_ids',
            'skills',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'public_seller_id', 'verification_status', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        # Set verification_status to PENDING if verification_document is provided
        if 'verification_document' in validated_data and validated_data['verification_document']:
            validated_data['verification_status'] = SellerProfile.VerificationStatus.PENDING
        
        seller_profile = SellerProfile.objects.create(**validated_data)
        
        if skill_ids:
            seller_profile.skills.set(skill_ids)
        
        return seller_profile
    
    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('skill_ids', None)
        
        # If verification_document is being updated, set status to PENDING
        if 'verification_document' in validated_data and validated_data['verification_document']:
            validated_data['verification_status'] = SellerProfile.VerificationStatus.PENDING
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_ids is not None:
            instance.skills.set(skill_ids)
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_seller']
        read_only_fields = ['id', 'is_seller']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Create wallet for new user
        UserWallet.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
