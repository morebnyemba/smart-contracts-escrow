from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import EscrowTransaction
from .serializers import EscrowTransactionSerializer


class MyTransactionsView(generics.ListAPIView):
    """
    API endpoint for Buyer Portal to retrieve all transactions
    where the authenticated user is the buyer.
    """
    serializer_class = EscrowTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns transactions where the current user is the buyer,
        ordered by creation date (newest first).
        """
        return EscrowTransaction.objects.filter(
            buyer=self.request.user
        ).select_related('buyer', 'seller').prefetch_related('milestones').order_by('-created_at')
