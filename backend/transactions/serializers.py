from rest_framework import serializers
from .models import EscrowTransaction, Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    """Serializer for milestone details in transactions."""
    
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'description', 'value', 'status', 'submission_details']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction details including milestones."""
    milestones = MilestoneSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = EscrowTransaction
        fields = [
            'id',
            'title',
            'total_value',
            'buyer',
            'buyer_name',
            'seller',
            'seller_name',
            'status',
            'created_at',
            'milestones',
        ]
        read_only_fields = ['id', 'created_at', 'buyer', 'buyer_name', 'seller_name']
