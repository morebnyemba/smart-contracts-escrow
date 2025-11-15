from rest_framework import serializers
from transactions.models import EscrowTransaction, Milestone, Review
from wallets.models import UserWallet
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'transaction', 'title', 'description', 'value', 'status', 'submission_details']
        read_only_fields = ['id', 'transaction']

    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Milestone value must be positive.")
        return value


class MilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'value']

    def validate_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Milestone value must be positive.")
        return value


class EscrowTransactionSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = EscrowTransaction
        fields = ['id', 'title', 'total_value', 'buyer', 'seller', 'status', 'created_at', 'milestones']
        read_only_fields = ['id', 'buyer', 'total_value', 'status', 'created_at']


class EscrowTransactionCreateSerializer(serializers.ModelSerializer):
    milestones = MilestoneCreateSerializer(many=True)

    class Meta:
        model = EscrowTransaction
        fields = ['title', 'seller', 'milestones']

    def validate(self, data):
        milestones = data.get('milestones', [])
        if not milestones:
            raise serializers.ValidationError("At least one milestone is required.")
        
        total_value = sum(m['value'] for m in milestones)
        if total_value <= 0:
            raise serializers.ValidationError("Total transaction value must be positive.")
        
        return data

    def create(self, validated_data):
        milestones_data = validated_data.pop('milestones')
        
        # Calculate total value from milestones
        total_value = sum(m['value'] for m in milestones_data)
        validated_data['total_value'] = total_value
        
        # Set buyer as current user
        validated_data['buyer'] = self.context['request'].user
        
        # Create transaction
        transaction = EscrowTransaction.objects.create(**validated_data)
        
        # Create milestones
        for milestone_data in milestones_data:
            Milestone.objects.create(transaction=transaction, **milestone_data)
        
        return transaction


class UserWalletSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserWallet
        fields = ['id', 'user', 'balance']
        read_only_fields = ['id', 'user', 'balance']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'transaction', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'transaction', 'reviewer', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
