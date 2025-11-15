"""
Signal receivers for the notifications app.

These receivers listen for custom signals from the transactions app
and trigger appropriate notification actions.
"""
from django.dispatch import receiver
from transactions.signals import (
    milestone_approved,
    transaction_funded,
    revision_requested
)
from .tasks import (
    send_milestone_approved_notification,
    send_transaction_funded_notification,
    send_revision_requested_notification
)


@receiver(milestone_approved)
def handle_milestone_approved(sender, milestone, buyer, seller, **kwargs):
    """
    Handle the milestone_approved signal.
    
    Args:
        sender: The class that sent the signal
        milestone: The Milestone instance that was approved
        buyer: The User instance who approved the milestone
        seller: The User instance who receives payment
        **kwargs: Additional keyword arguments
    """
    # Trigger notification task
    # In production with Celery configured, use .delay() for async execution
    send_milestone_approved_notification(
        milestone_id=milestone.id,
        buyer_id=buyer.id,
        seller_id=seller.id
    )


@receiver(transaction_funded)
def handle_transaction_funded(sender, transaction, buyer, seller, **kwargs):
    """
    Handle the transaction_funded signal.
    
    Args:
        sender: The class that sent the signal
        transaction: The EscrowTransaction instance that was funded
        buyer: The User instance who funded the transaction
        seller: The User instance who will perform the work
        **kwargs: Additional keyword arguments
    """
    # Trigger notification task
    # In production with Celery configured, use .delay() for async execution
    send_transaction_funded_notification(
        transaction_id=transaction.id,
        buyer_id=buyer.id,
        seller_id=seller.id
    )


@receiver(revision_requested)
def handle_revision_requested(sender, milestone, buyer, seller, **kwargs):
    """
    Handle the revision_requested signal.
    
    Args:
        sender: The class that sent the signal
        milestone: The Milestone instance for which revision was requested
        buyer: The User instance who requested the revision
        seller: The User instance who needs to make revisions
        **kwargs: Additional keyword arguments
    """
    # Trigger notification task
    # In production with Celery configured, use .delay() for async execution
    send_revision_requested_notification(
        milestone_id=milestone.id,
        buyer_id=buyer.id,
        seller_id=seller.id
    )
