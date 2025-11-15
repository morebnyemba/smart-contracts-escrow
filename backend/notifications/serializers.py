from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    transaction_title = serializers.CharField(source='transaction.title', read_only=True, allow_null=True)
    milestone_title = serializers.CharField(source='milestone.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'recipient_username',
            'notification_type',
            'message',
            'transaction',
            'transaction_title',
            'milestone',
            'milestone_title',
            'is_read',
            'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'created_at']
