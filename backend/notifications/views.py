from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notifications.
    
    list: Get all notifications for the authenticated user
    retrieve: Get a specific notification
    mark_as_read: Mark a notification as read
    mark_all_as_read: Mark all notifications as read
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only notifications for the authenticated user.
        """
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('recipient', 'transaction', 'milestone')
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications for the authenticated user as read.
        """
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response(
            {'message': f'{updated_count} notifications marked as read.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get the count of unread notifications for the authenticated user.
        """
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'count': count}, status=status.HTTP_200_OK)
