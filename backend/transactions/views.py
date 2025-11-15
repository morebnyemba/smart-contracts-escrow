from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import EscrowTransaction
from .serializers import TransactionSerializer


class BuyerTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for buyers to view their transactions.
    
    Provides list and retrieve actions for transactions where the
    authenticated user is the buyer.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only transactions where the current user is the buyer.
        Orders by most recent first.
        """
        return EscrowTransaction.objects.filter(
            buyer=self.request.user
        ).prefetch_related('milestones').select_related('buyer', 'seller').order_by('-created_at')


class SellerTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for sellers to view their transactions.
    
    Provides list and retrieve actions for transactions where the
    authenticated user is the seller.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only transactions where the current user is the seller.
        Orders by most recent first.
        """
        return EscrowTransaction.objects.filter(
            seller=self.request.user
        ).prefetch_related('milestones').select_related('buyer', 'seller').order_by('-created_at')
