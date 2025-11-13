from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from transactions.models import EscrowTransaction
from .serializers import EscrowTransactionSerializer


class MyProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for sellers to view their projects.
    Returns all escrow transactions where the authenticated user is the seller.
    """
    serializer_class = EscrowTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter transactions where the authenticated user is the seller.
        Prefetch related milestones for efficient queries.
        """
        return EscrowTransaction.objects.filter(
            seller=self.request.user
        ).prefetch_related('milestones').order_by('-created_at')
