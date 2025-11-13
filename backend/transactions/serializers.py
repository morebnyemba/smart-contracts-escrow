from rest_framework import serializers
from .models import EscrowTransaction, Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'description', 'value', 'status', 'submission_details']


class EscrowTransactionSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = EscrowTransaction
        fields = [
            'id', 
            'title', 
            'total_value', 
            'buyer', 
            'buyer_username',
            'seller', 
            'seller_username',
            'status', 
            'created_at',
            'milestones'
        ]
        read_only_fields = ['id', 'created_at']
