from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SellerProfile, ServiceCategory

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    is_seller = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_seller')
        read_only_fields = ('id', 'is_seller')

    def get_is_seller(self, obj):
        return hasattr(obj, 'seller_profile')


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'slug')


class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = ServiceCategorySerializer(many=True, read_only=True)
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = SellerProfile
        fields = (
            'id', 'user', 'public_seller_id', 'account_type', 'company_name',
            'verification_document', 'verification_status', 'skills', 'skill_ids'
        )
        read_only_fields = ('id', 'public_seller_id', 'verification_status', 'user')

    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        seller_profile = SellerProfile.objects.create(**validated_data)
        if skill_ids:
            seller_profile.skills.set(ServiceCategory.objects.filter(id__in=skill_ids))
        return seller_profile

    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('skill_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skill_ids is not None:
            instance.skills.set(ServiceCategory.objects.filter(id__in=skill_ids))
        return instance
