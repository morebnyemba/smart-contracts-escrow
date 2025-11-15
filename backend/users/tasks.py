"""
Celery tasks for user-related operations.

This module contains asynchronous tasks for user notifications,
email sending, and other long-running user operations.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, subject, message, recipient_list, from_email=None):
    """
    Send an email notification asynchronously.
    
    Args:
        subject (str): Email subject line
        message (str): Email body content
        recipient_list (list): List of recipient email addresses
        from_email (str, optional): Sender email address. 
                                   Defaults to settings.DEFAULT_FROM_EMAIL
    
    Returns:
        dict: Result with success status and details
    
    Example:
        send_email_notification.delay(
            subject='Welcome to Escrow Platform',
            message='Thank you for registering!',
            recipient_list=['user@example.com']
        )
    """
    try:
        if from_email is None:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Email sent successfully to {recipient_list}: {subject}")
        return {
            'success': True,
            'recipients': recipient_list,
            'subject': subject
        }
    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_transaction_notification(transaction_id, notification_type):
    """
    Send notifications related to escrow transactions.
    
    Args:
        transaction_id (int): ID of the escrow transaction
        notification_type (str): Type of notification (e.g., 'created', 'funded', 'completed')
    
    Returns:
        dict: Result with success status
    
    Example:
        send_transaction_notification.delay(
            transaction_id=123,
            notification_type='funded'
        )
    """
    try:
        from transactions.models import EscrowTransaction
        
        transaction = EscrowTransaction.objects.get(id=transaction_id)
        
        # Build notification message based on type
        notification_messages = {
            'created': f'New escrow transaction created: {transaction.title}',
            'funded': f'Transaction {transaction.title} has been funded',
            'completed': f'Transaction {transaction.title} has been completed',
            'milestone_submitted': f'Milestone submitted for transaction {transaction.title}',
            'milestone_approved': f'Milestone approved for transaction {transaction.title}',
        }
        
        message = notification_messages.get(
            notification_type,
            f'Update on transaction {transaction.title}'
        )
        
        # Determine recipients based on notification type
        recipients = []
        if transaction.buyer and transaction.buyer.email:
            recipients.append(transaction.buyer.email)
        if transaction.seller and transaction.seller.email:
            recipients.append(transaction.seller.email)
        
        if recipients:
            send_email_notification.delay(
                subject=f'Escrow Transaction Update: {transaction.title}',
                message=message,
                recipient_list=recipients
            )
        
        logger.info(f"Transaction notification sent: {notification_type} for transaction {transaction_id}")
        return {'success': True, 'notification_type': notification_type}
        
    except Exception as exc:
        logger.error(f"Failed to send transaction notification: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def send_verification_notification(user_id, verification_status):
    """
    Send seller verification status notification.
    
    Args:
        user_id (int): ID of the user
        verification_status (str): New verification status
    
    Returns:
        dict: Result with success status
    """
    try:
        from users.models import CustomUser, SellerProfile
        
        user = CustomUser.objects.get(id=user_id)
        
        status_messages = {
            'VERIFIED': 'Congratulations! Your seller profile has been verified.',
            'REJECTED': 'Your seller profile verification was not approved. Please check the notes and resubmit.',
            'PENDING': 'Your seller profile is under review. We will notify you once the verification is complete.',
        }
        
        message = status_messages.get(
            verification_status,
            f'Your seller verification status has been updated to: {verification_status}'
        )
        
        if user.email:
            send_email_notification.delay(
                subject='Seller Profile Verification Update',
                message=message,
                recipient_list=[user.email]
            )
        
        logger.info(f"Verification notification sent to user {user_id}: {verification_status}")
        return {'success': True, 'status': verification_status}
        
    except Exception as exc:
        logger.error(f"Failed to send verification notification: {exc}")
        return {'success': False, 'error': str(exc)}
