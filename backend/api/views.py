from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404

from transactions.models import EscrowTransaction, Milestone
from wallets.models import UserWallet
from .serializers import (
    EscrowTransactionSerializer,
    EscrowTransactionCreateSerializer,
    MilestoneSerializer,
    UserWalletSerializer
)


class EscrowTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing escrow transactions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Return transactions where user is buyer or seller
        return EscrowTransaction.objects.filter(
            buyer=user
        ) | EscrowTransaction.objects.filter(
            seller=user
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EscrowTransactionCreateSerializer
        return EscrowTransactionSerializer
    
    @action(detail=True, methods=['post'])
    def fund(self, request, pk=None):
        """
        Fund a transaction by transferring funds from buyer's wallet to escrow.
        """
        transaction_obj = self.get_object()
        
        # Validate buyer
        if transaction_obj.buyer != request.user:
            return Response(
                {'error': 'Only the buyer can fund this transaction.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate transaction status
        if transaction_obj.status != EscrowTransaction.TransactionStatus.PENDING_FUNDING:
            return Response(
                {'error': f'Transaction cannot be funded in {transaction_obj.status} status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create buyer's wallet
        buyer_wallet, created = UserWallet.objects.get_or_create(
            user=transaction_obj.buyer,
            defaults={'balance': 0}
        )
        
        # Check if buyer has sufficient funds
        if buyer_wallet.balance < transaction_obj.total_value:
            return Response(
                {'error': 'Insufficient funds in wallet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform the funding transaction
        with db_transaction.atomic():
            # Deduct from buyer's wallet
            buyer_wallet.balance -= transaction_obj.total_value
            buyer_wallet.save()
            
            # Update transaction status
            transaction_obj.status = EscrowTransaction.TransactionStatus.IN_ESCROW
            transaction_obj.save()
        
        serializer = self.get_serializer(transaction_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MilestoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for milestone operations.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Return milestones from transactions where user is buyer or seller
        return Milestone.objects.filter(
            transaction__buyer=user
        ) | Milestone.objects.filter(
            transaction__seller=user
        )
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Seller submits work for a milestone.
        """
        milestone = self.get_object()
        transaction_obj = milestone.transaction
        
        # Validate seller
        if transaction_obj.seller != request.user:
            return Response(
                {'error': 'Only the seller can submit work for this milestone.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate milestone status
        if milestone.status not in [
            Milestone.MilestoneStatus.PENDING,
            Milestone.MilestoneStatus.REVISION_REQUESTED
        ]:
            return Response(
                {'error': f'Milestone cannot be submitted in {milestone.status} status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get submission details from request
        submission_details = request.data.get('submission_details', '')
        
        # Update milestone
        milestone.status = Milestone.MilestoneStatus.AWAITING_REVIEW
        milestone.submission_details = submission_details
        milestone.save()
        
        serializer = self.get_serializer(milestone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Buyer approves milestone and releases payment to seller.
        """
        milestone = self.get_object()
        transaction_obj = milestone.transaction
        
        # Validate buyer
        if transaction_obj.buyer != request.user:
            return Response(
                {'error': 'Only the buyer can approve this milestone.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate milestone status
        if milestone.status != Milestone.MilestoneStatus.AWAITING_REVIEW:
            return Response(
                {'error': f'Milestone cannot be approved in {milestone.status} status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create seller's wallet
        seller_wallet, created = UserWallet.objects.get_or_create(
            user=transaction_obj.seller,
            defaults={'balance': 0}
        )
        
        # Perform the payment release
        with db_transaction.atomic():
            # Add to seller's wallet (released from escrow)
            seller_wallet.balance += milestone.value
            seller_wallet.save()
            
            # Update milestone status
            milestone.status = Milestone.MilestoneStatus.COMPLETED
            milestone.save()
            
            # Check if all milestones are completed
            all_completed = all(
                m.status == Milestone.MilestoneStatus.COMPLETED
                for m in transaction_obj.milestones.all()
            )
            
            if all_completed:
                transaction_obj.status = EscrowTransaction.TransactionStatus.COMPLETED
                transaction_obj.save()
        
        serializer = self.get_serializer(milestone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        """
        Buyer requests revision for a milestone.
        """
        milestone = self.get_object()
        transaction_obj = milestone.transaction
        
        # Validate buyer
        if transaction_obj.buyer != request.user:
            return Response(
                {'error': 'Only the buyer can request revisions for this milestone.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate milestone status
        if milestone.status != Milestone.MilestoneStatus.AWAITING_REVIEW:
            return Response(
                {'error': f'Revisions cannot be requested in {milestone.status} status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update milestone status
        milestone.status = Milestone.MilestoneStatus.REVISION_REQUESTED
        milestone.save()
        
        serializer = self.get_serializer(milestone)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user wallet.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserWalletSerializer
    
    def get_queryset(self):
        # Only return current user's wallet
        return UserWallet.objects.filter(user=self.request.user)
