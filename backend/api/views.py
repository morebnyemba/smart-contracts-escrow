from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404
import logging

from transactions.models import EscrowTransaction, Milestone, Review
from wallets.models import UserWallet
from .serializers import (
    EscrowTransactionSerializer,
    EscrowTransactionCreateSerializer,
    MilestoneSerializer,
    UserWalletSerializer,
    ReviewSerializer
)

logger = logging.getLogger(__name__)


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
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serialization after creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Use the read serializer for the response
        output_serializer = EscrowTransactionSerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
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
            
            # Send signal for transaction funded
            transaction_funded.send(
                sender=self.__class__,
                transaction=transaction_obj,
                buyer=transaction_obj.buyer,
                seller=transaction_obj.seller
            )
        
        serializer = self.get_serializer(transaction_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def leave_review(self, request, pk=None):
        """
        Leave a review for a transaction.
        Both buyer and seller can leave reviews.
        """
        transaction_obj = self.get_object()
        
        # Validate that user is buyer or seller
        if transaction_obj.buyer != request.user and transaction_obj.seller != request.user:
            return Response(
                {'error': 'Only the buyer or seller can leave a review for this transaction.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user has already reviewed
        existing_review = Review.objects.filter(
            transaction=transaction_obj,
            reviewer=request.user
        ).first()
        
        if existing_review:
            return Response(
                {'error': 'You have already left a review for this transaction.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate transaction status - must be COMPLETED or CLOSED
        if transaction_obj.status not in [
            EscrowTransaction.TransactionStatus.COMPLETED,
            EscrowTransaction.TransactionStatus.CLOSED
        ]:
            return Response(
                {'error': 'Reviews can only be left for completed transactions.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the review
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                transaction=transaction_obj,
                reviewer=request.user
            )
            
            # Update transaction status to CLOSED after review is submitted
            transaction_obj.status = EscrowTransaction.TransactionStatus.CLOSED
            transaction_obj.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            
            # Send signal for milestone approved
            milestone_approved.send(
                sender=self.__class__,
                milestone=milestone,
                buyer=transaction_obj.buyer,
                seller=transaction_obj.seller
            )
        
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
        
        # Send signal for revision requested
        revision_requested.send(
            sender=self.__class__,
            milestone=milestone,
            buyer=transaction_obj.buyer,
            seller=transaction_obj.seller
        )
        
        serializer = self.get_serializer(milestone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        """
        Buyer opens a dispute for a milestone.
        """
        milestone = self.get_object()
        transaction_obj = milestone.transaction
        
        # Validate buyer
        if transaction_obj.buyer != request.user:
            return Response(
                {'error': 'Only the buyer can open a dispute for this milestone.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate milestone status - can't dispute an already completed or disputed milestone
        if milestone.status == Milestone.MilestoneStatus.COMPLETED:
            return Response(
                {'error': 'Cannot dispute a completed milestone.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if milestone.status == Milestone.MilestoneStatus.DISPUTED:
            return Response(
                {'error': 'This milestone is already disputed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update milestone and transaction status
        with db_transaction.atomic():
            milestone.status = Milestone.MilestoneStatus.DISPUTED
            milestone.save()
            
            transaction_obj.status = EscrowTransaction.TransactionStatus.DISPUTED
            transaction_obj.save()
            
            # Notify admin - using logging for now, can be replaced with proper notification system
            logger.warning(
                f'DISPUTE OPENED: Transaction {transaction_obj.id} - Milestone {milestone.id}. '
                f'Buyer: {transaction_obj.buyer.username} (ID: {transaction_obj.buyer.id}), '
                f'Seller: {transaction_obj.seller.username} (ID: {transaction_obj.seller.id}). '
                f'Admin mediation required.'
            )
        
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
