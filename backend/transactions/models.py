from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class EscrowTransaction(models.Model):
    class TransactionStatus(models.TextChoices):
        PENDING_FUNDING = 'PENDING_FUNDING', 'Pending Funding'
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', 'Awaiting Payment'
        IN_ESCROW = 'IN_ESCROW', 'In Escrow'
        WORK_IN_PROGRESS = 'WORK_IN_PROGRESS', 'Work in Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        DISPUTED = 'DISPUTED', 'Disputed'
        CLOSED = 'CLOSED', 'Closed'

    title = models.CharField(max_length=255)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='buying_transactions')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='selling_transactions')
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING_FUNDING)
    created_at = models.DateTimeField(auto_now_add=True)

class Milestone(models.Model):
    class MilestoneStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        AWAITING_REVIEW = 'AWAITING_REVIEW', 'Awaiting Review'
        REVISION_REQUESTED = 'REVISION_REQUESTED', 'Revision Requested'
        COMPLETED = 'COMPLETED', 'Completed'
        DISPUTED = 'DISPUTED', 'Disputed'
        
    transaction = models.ForeignKey(EscrowTransaction, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=MilestoneStatus.choices, default=MilestoneStatus.PENDING)
    submission_details = models.TextField(blank=True)

class Review(models.Model):
    transaction = models.ForeignKey(EscrowTransaction, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviews_given')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['transaction', 'reviewer']