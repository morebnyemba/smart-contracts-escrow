"""
Scheduled Celery tasks for periodic operations.

This module contains tasks that are meant to be run on a schedule
using Celery Beat. These can include daily summaries, cleanup tasks,
reminder notifications, etc.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_daily_transaction_summary():
    """
    Send a daily summary of transactions to users.
    
    This task can be scheduled to run daily to provide users with
    a summary of their active transactions, pending actions, etc.
    
    Returns:
        dict: Summary of the operation
    """
    try:
        from transactions.models import EscrowTransaction
        from users.models import CustomUser
        
        # Get all users with active transactions
        active_statuses = [
            EscrowTransaction.TransactionStatus.IN_ESCROW,
            EscrowTransaction.TransactionStatus.WORK_IN_PROGRESS,
            EscrowTransaction.TransactionStatus.AWAITING_PAYMENT,
        ]
        
        users_with_transactions = CustomUser.objects.filter(
            buying_transactions__status__in=active_statuses
        ).distinct() | CustomUser.objects.filter(
            selling_transactions__status__in=active_statuses
        ).distinct()
        
        summaries_sent = 0
        for user in users_with_transactions:
            # Get user's active transactions
            buying = user.buying_transactions.filter(status__in=active_statuses).count()
            selling = user.selling_transactions.filter(status__in=active_statuses).count()
            
            if buying > 0 or selling > 0:
                # Import the email task here to avoid circular imports
                from users.tasks import send_email_notification
                
                message = f"""
Daily Transaction Summary

Active Transactions:
- Buying: {buying}
- Selling: {selling}

Please log in to view details and take any necessary actions.
                """
                
                if user.email:
                    send_email_notification.delay(
                        subject='Daily Transaction Summary',
                        message=message,
                        recipient_list=[user.email]
                    )
                    summaries_sent += 1
        
        logger.info(f"Daily summaries sent to {summaries_sent} users")
        return {'success': True, 'summaries_sent': summaries_sent}
        
    except Exception as exc:
        logger.error(f"Failed to send daily summaries: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def cleanup_old_pending_transactions():
    """
    Clean up or send reminders for old pending transactions.
    
    This task can be scheduled to run periodically to handle
    transactions that have been in PENDING_FUNDING status for too long.
    
    Returns:
        dict: Summary of the cleanup operation
    """
    try:
        from transactions.models import EscrowTransaction
        from users.tasks import send_email_notification
        
        # Find transactions pending for more than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        old_pending = EscrowTransaction.objects.filter(
            status=EscrowTransaction.TransactionStatus.PENDING_FUNDING,
            created_at__lt=cutoff_date
        )
        
        reminders_sent = 0
        for transaction in old_pending:
            if transaction.buyer and transaction.buyer.email:
                message = f"""
Reminder: Transaction Pending Funding

Your transaction "{transaction.title}" has been pending funding for over 7 days.

Please log in to complete the funding or cancel the transaction if no longer needed.
                """
                
                send_email_notification.delay(
                    subject=f'Reminder: Fund Transaction - {transaction.title}',
                    message=message,
                    recipient_list=[transaction.buyer.email]
                )
                reminders_sent += 1
        
        logger.info(f"Sent {reminders_sent} reminders for old pending transactions")
        return {'success': True, 'reminders_sent': reminders_sent}
        
    except Exception as exc:
        logger.error(f"Failed to cleanup old transactions: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task
def check_overdue_milestones():
    """
    Check for overdue milestones and send notifications.
    
    This task can be used to identify milestones that haven't been
    completed within expected timeframes and notify relevant parties.
    
    Returns:
        dict: Summary of overdue milestone checks
    """
    try:
        from transactions.models import Milestone
        from users.tasks import send_email_notification
        
        # Find milestones pending for more than 14 days
        cutoff_date = timezone.now() - timedelta(days=14)
        overdue_milestones = Milestone.objects.filter(
            status=Milestone.MilestoneStatus.PENDING,
            transaction__created_at__lt=cutoff_date
        ).select_related('transaction', 'transaction__seller', 'transaction__buyer')
        
        notifications_sent = 0
        for milestone in overdue_milestones:
            transaction = milestone.transaction
            if transaction.seller and transaction.seller.email:
                message = f"""
Overdue Milestone Notification

The milestone "{milestone.title}" for transaction "{transaction.title}" has been pending for over 14 days.

Please update the milestone status or contact the buyer if there are any issues.
                """
                
                send_email_notification.delay(
                    subject=f'Overdue Milestone: {milestone.title}',
                    message=message,
                    recipient_list=[transaction.seller.email]
                )
                notifications_sent += 1
        
        logger.info(f"Sent {notifications_sent} overdue milestone notifications")
        return {'success': True, 'notifications_sent': notifications_sent}
        
    except Exception as exc:
        logger.error(f"Failed to check overdue milestones: {exc}")
        return {'success': False, 'error': str(exc)}
