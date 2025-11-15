"""
Celery tasks for sending notifications.

These tasks handle the actual sending of notifications (e.g., emails)
asynchronously to avoid blocking the main request/response cycle.
"""
import logging
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


def create_notification(recipient_id, notification_type, message, transaction_id=None, milestone_id=None):
    """
    Helper function to create a notification record.
    
    Args:
        recipient_id: ID of the user who receives the notification
        notification_type: Type of notification (from Notification.NotificationType)
        message: Message text for the notification
        transaction_id: Optional ID of related transaction
        milestone_id: Optional ID of related milestone
    """
    try:
        from transactions.models import EscrowTransaction, Milestone
        
        notification = Notification.objects.create(
            recipient_id=recipient_id,
            notification_type=notification_type,
            message=message,
            transaction_id=transaction_id,
            milestone_id=milestone_id
        )
        logger.info(f"Created notification {notification.id} for user {recipient_id}")
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        return None


def send_milestone_approved_notification(milestone_id, buyer_id, seller_id):
    """
    Send notification when a milestone is approved.
    
    Args:
        milestone_id: ID of the approved milestone
        buyer_id: ID of the buyer who approved the milestone
        seller_id: ID of the seller who receives the notification
    """
    try:
        from transactions.models import Milestone
        milestone = Milestone.objects.get(id=milestone_id)
        transaction_id = milestone.transaction_id
        
        message = f"Your milestone '{milestone.title}' has been approved and payment released."
        create_notification(
            recipient_id=seller_id,
            notification_type=Notification.NotificationType.MILESTONE_APPROVED,
            message=message,
            transaction_id=transaction_id,
            milestone_id=milestone_id
        )
        
        logger.info(
            f"Milestone {milestone_id} approved notification created for seller {seller_id}"
        )
    except Exception as e:
        logger.error(f"Failed to send milestone approved notification: {e}")


def send_transaction_funded_notification(transaction_id, buyer_id, seller_id):
    """
    Send notification when a transaction is funded.
    
    Args:
        transaction_id: ID of the funded transaction
        buyer_id: ID of the buyer who funded the transaction
        seller_id: ID of the seller who receives the notification
    """
    try:
        from transactions.models import EscrowTransaction
        transaction = EscrowTransaction.objects.get(id=transaction_id)
        
        message = f"Transaction '{transaction.title}' has been funded. You can now start working on the milestones."
        create_notification(
            recipient_id=seller_id,
            notification_type=Notification.NotificationType.ESCROW_FUNDED,
            message=message,
            transaction_id=transaction_id
        )
        
        logger.info(
            f"Transaction {transaction_id} funded notification created for seller {seller_id}"
        )
    except Exception as e:
        logger.error(f"Failed to send transaction funded notification: {e}")


def send_revision_requested_notification(milestone_id, buyer_id, seller_id):
    """
    Send notification when revision is requested for a milestone.
    
    Args:
        milestone_id: ID of the milestone needing revision
        buyer_id: ID of the buyer who requested the revision
        seller_id: ID of the seller who receives the notification
    """
    try:
        from transactions.models import Milestone
        milestone = Milestone.objects.get(id=milestone_id)
        transaction_id = milestone.transaction_id
        
        message = f"Revision requested for milestone '{milestone.title}'. Please review the feedback and resubmit."
        create_notification(
            recipient_id=seller_id,
            notification_type=Notification.NotificationType.REVISION_REQUESTED,
            message=message,
            transaction_id=transaction_id,
            milestone_id=milestone_id
        )
        
        logger.info(
            f"Milestone {milestone_id} revision requested notification created for seller {seller_id}"
        )
    except Exception as e:
        logger.error(f"Failed to send revision requested notification: {e}")


def send_work_submitted_notification(milestone_id, buyer_id, seller_id):
    """
    Send notification when work is submitted for a milestone.
    
    Args:
        milestone_id: ID of the milestone with submitted work
        buyer_id: ID of the buyer who receives the notification
        seller_id: ID of the seller who submitted the work
    """
    try:
        from transactions.models import Milestone
        milestone = Milestone.objects.get(id=milestone_id)
        transaction_id = milestone.transaction_id
        
        message = f"Work has been submitted for milestone '{milestone.title}'. Please review and approve or request revisions."
        create_notification(
            recipient_id=buyer_id,
            notification_type=Notification.NotificationType.WORK_SUBMITTED,
            message=message,
            transaction_id=transaction_id,
            milestone_id=milestone_id
        )
        
        logger.info(
            f"Milestone {milestone_id} work submitted notification created for buyer {buyer_id}"
        )
    except Exception as e:
        logger.error(f"Failed to send work submitted notification: {e}")


# Placeholder for Celery task decorator
# In production, these functions would be decorated with @shared_task
# from celery import shared_task
# @shared_task
# def send_milestone_approved_notification(...):
#     ...
