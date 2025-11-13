from rest_framework import serializers
from .models import SellerProfile, ServiceCategory, CustomUser


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug']


class SellerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    skills = ServiceCategorySerializer(many=True, read_only=True)
    
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
