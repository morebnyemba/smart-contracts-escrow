from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from wallets.models import UserWallet, EscrowWallet, PaymentTransaction
from transactions.models import EscrowTransaction

@api_view(['POST'])
def payment_webhook(request):
    """
    Webhook to process payment and move funds from user wallet to escrow wallet.
    
    Expected payload:
    {
        "transaction_id": int,
        "user_id": int,
        "amount": decimal
    }
    """
    transaction_id = request.data.get('transaction_id')
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')
    
    # Validate required fields
    if not all([transaction_id, user_id, amount]):
        return Response(
            {"error": "Missing required fields: transaction_id, user_id, amount"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response(
                {"error": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError, ArithmeticError):
        return Response(
            {"error": "Invalid amount format"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use database transaction to ensure atomicity
    try:
        with transaction.atomic():
            # Get or create user wallet
            try:
                user_wallet = UserWallet.objects.select_for_update().get(user_id=user_id)
            except UserWallet.DoesNotExist:
                return Response(
                    {"error": f"User wallet not found for user {user_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get escrow transaction
            try:
                escrow_transaction = EscrowTransaction.objects.select_for_update().get(id=transaction_id)
            except EscrowTransaction.DoesNotExist:
                return Response(
                    {"error": f"Escrow transaction {transaction_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate amount matches transaction value
            if amount != escrow_transaction.total_value:
                return Response(
                    {"error": f"Amount {amount} does not match transaction value {escrow_transaction.total_value}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user has sufficient balance
            if user_wallet.balance < amount:
                return Response(
                    {"error": f"Insufficient balance. Required: {amount}, Available: {user_wallet.balance}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create escrow wallet (platform escrow wallet)
            escrow_wallet, _ = EscrowWallet.objects.get_or_create(
                id=1,
                defaults={'balance': Decimal('0.00')}
            )
            
            # Create payment transaction record
            payment_txn = PaymentTransaction.objects.create(
                escrow_transaction=escrow_transaction,
                user_wallet=user_wallet,
                escrow_wallet=escrow_wallet,
                amount=amount,
                status=PaymentTransaction.PaymentStatus.PENDING
            )
            
            # Deduct from user wallet
            user_wallet.balance -= amount
            user_wallet.save()
            
            # Add to escrow wallet
            escrow_wallet.balance += amount
            escrow_wallet.save()
            
            # Update payment transaction status
            payment_txn.status = PaymentTransaction.PaymentStatus.COMPLETED
            payment_txn.completed_at = timezone.now()
            payment_txn.save()
            
            # Update escrow transaction status
            escrow_transaction.status = EscrowTransaction.TransactionStatus.IN_ESCROW
            escrow_transaction.save()
            
            return Response({
                "success": True,
                "message": "Payment processed successfully",
                "payment_transaction_id": payment_txn.id,
                "escrow_transaction_status": escrow_transaction.status,
                "user_wallet_balance": float(user_wallet.balance),
                "escrow_wallet_balance": float(escrow_wallet.balance)
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {"error": f"Payment processing failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
