from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Model to store user notifications for transaction events.
    """
    class NotificationType(models.TextChoices):
        TRANSACTION_ACCEPTED = 'TRANSACTION_ACCEPTED', 'Transaction Accepted'
        ESCROW_FUNDED = 'ESCROW_FUNDED', 'Escrow Funded'
        WORK_SUBMITTED = 'WORK_SUBMITTED', 'Work Submitted'
        MILESTONE_APPROVED = 'MILESTONE_APPROVED', 'Milestone Approved'
        REVISION_REQUESTED = 'REVISION_REQUESTED', 'Revision Requested'
        TRANSACTION_COMPLETED = 'TRANSACTION_COMPLETED', 'Transaction Completed'
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices
    )
    message = models.TextField()
    transaction = models.ForeignKey(
        'transactions.EscrowTransaction',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    milestone = models.ForeignKey(
        'transactions.Milestone',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username} at {self.created_at}"
