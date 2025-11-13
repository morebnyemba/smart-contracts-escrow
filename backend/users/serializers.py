from rest_framework import serializers
from .models import SellerProfile, ServiceCategory


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
            'public_seller_id',
            'username',
            'account_type',
            'company_name',
            'verification_status',
            'skills',
        ]
        read_only_fields = ['public_seller_id', 'username']
