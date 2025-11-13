from rest_framework import serializers
from transactions.models import EscrowTransaction, Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    """Serializer for Milestone model"""
    
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'description', 'value', 'status', 'submission_details']


class EscrowTransactionSerializer(serializers.ModelSerializer):
    """Serializer for EscrowTransaction model with nested milestones"""
    milestones = MilestoneSerializer(many=True, read_only=True)
    buyer_name = serializers.SerializerMethodField()
    seller_name = serializers.SerializerMethodField()
    
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
            'milestones'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_buyer_name(self, obj):
        """Get buyer's full name or username"""
        if obj.buyer:
            return obj.buyer.get_full_name() or obj.buyer.username
        return None
    
    def get_seller_name(self, obj):
        """Get seller's full name or username"""
        if obj.seller:
            return obj.seller.get_full_name() or obj.seller.username
        return None
