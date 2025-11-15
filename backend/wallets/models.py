from django.db import models
from django.conf import settings
from decimal import Decimal

class UserWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

class EscrowWallet(models.Model):
    """Platform escrow wallet that holds funds during transactions"""
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentTransaction(models.Model):
    """Tracks payments from user wallets to escrow"""
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    escrow_transaction = models.ForeignKey('transactions.EscrowTransaction', on_delete=models.CASCADE, related_name='payment_transactions')
    user_wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name='payment_transactions')
    escrow_wallet = models.ForeignKey(EscrowWallet, on_delete=models.CASCADE, related_name='payment_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)