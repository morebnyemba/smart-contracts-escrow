# Notification System Documentation

## Overview

The notification system provides real-time notifications to users about important events in their transactions. Users receive notifications in their dashboard when key actions occur, such as when escrow is funded, work is submitted, milestones are approved, or revisions are requested.

## Architecture

### Backend Components

#### 1. Notification Model (`notifications/models.py`)

The `Notification` model stores notification records in the database:

```python
class Notification(models.Model):
    recipient = ForeignKey(User)
    notification_type = CharField(choices=NotificationType.choices)
    message = TextField()
    transaction = ForeignKey(EscrowTransaction, optional)
    milestone = ForeignKey(Milestone, optional)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

**Notification Types:**
- `TRANSACTION_ACCEPTED` - Transaction has been accepted by seller
- `ESCROW_FUNDED` - Buyer has funded the escrow
- `WORK_SUBMITTED` - Seller has submitted work for review
- `MILESTONE_APPROVED` - Buyer has approved a milestone
- `REVISION_REQUESTED` - Buyer has requested revisions
- `TRANSACTION_COMPLETED` - Transaction is complete

**Database Indexes:**
- `(recipient, -created_at)` - For efficient notification listing
- `(recipient, is_read)` - For fast unread count queries

#### 2. Signal Handlers (`notifications/receivers.py`)

Signal receivers automatically create notifications when events occur:

```python
@receiver(transaction_funded)
def handle_transaction_funded(sender, transaction, buyer, seller, **kwargs):
    # Creates notification for seller
    
@receiver(work_submitted)
def handle_work_submitted(sender, milestone, buyer, seller, **kwargs):
    # Creates notification for buyer
    
@receiver(milestone_approved)
def handle_milestone_approved(sender, milestone, buyer, seller, **kwargs):
    # Creates notification for seller
    
@receiver(revision_requested)
def handle_revision_requested(sender, milestone, buyer, seller, **kwargs):
    # Creates notification for seller
```

#### 3. API Endpoints (`notifications/views.py`)

**NotificationViewSet** provides REST API endpoints:

- `GET /api/notifications/` - List all notifications for authenticated user
- `GET /api/notifications/{id}/` - Get specific notification
- `POST /api/notifications/{id}/mark_as_read/` - Mark notification as read
- `POST /api/notifications/mark_all_as_read/` - Mark all as read
- `GET /api/notifications/unread_count/` - Get unread count

**Response Format:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "recipient": 2,
      "recipient_username": "seller",
      "notification_type": "ESCROW_FUNDED",
      "message": "Transaction 'Project X' has been funded...",
      "transaction": 1,
      "transaction_title": "Project X",
      "milestone": null,
      "milestone_title": null,
      "is_read": false,
      "created_at": "2025-11-15T15:21:02.638570Z"
    }
  ]
}
```

### Frontend Components

#### 1. NotificationBell Component (`components/notifications/NotificationBell.tsx`)

A React component that displays notifications in a dropdown:

**Features:**
- Real-time badge with unread count
- Dropdown list with notification history
- Auto-refresh every 30 seconds
- Click to mark as read
- Mark all as read button
- Relative timestamps (5m ago, 2h ago)
- Icon indicators per notification type

**Usage:**
```tsx
import { NotificationBell } from '@/components/notifications';

<NotificationBell />
```

#### 2. API Integration (`lib/api.ts`)

```typescript
notificationAPI.getAll()
notificationAPI.getUnreadCount()
notificationAPI.markAsRead(id)
notificationAPI.markAllAsRead()
```

## Event Flow

### Example: Milestone Approval

1. Buyer clicks "Approve Milestone" button
2. API endpoint `/api/milestones/{id}/approve/` is called
3. Backend updates milestone status and releases payment
4. `milestone_approved` signal is sent
5. Signal receiver creates `Notification` record for seller
6. Seller's notification bell shows new unread badge
7. Seller clicks bell to see notification
8. Clicking notification marks it as read

## Testing

### Running Tests

```bash
cd backend
python manage.py test notifications
```

**Test Coverage:**
- Signal tests (4 tests) - Verify signals trigger notifications
- Model tests (2 tests) - Verify notification model behavior
- API tests (6 tests) - Verify API endpoints work correctly

All 12 tests pass ✅

### Manual Testing

```python
# Create test notification
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='testuser')

notification = Notification.objects.create(
    recipient=user,
    notification_type=Notification.NotificationType.ESCROW_FUNDED,
    message='Test notification',
    transaction_id=1
)
```

## Performance Considerations

### Database Optimization

1. **Indexes** - Queries are optimized with composite indexes
2. **Select Related** - API queries use `select_related()` to reduce database hits
3. **Pagination** - List endpoint supports pagination to handle large result sets

### Frontend Optimization

1. **Polling Interval** - 30-second refresh interval balances freshness and load
2. **Conditional Rendering** - Dropdown only renders when opened
3. **State Management** - Local state prevents unnecessary re-renders

## Future Enhancements

### Potential Improvements

1. **Email Notifications**
   - Infrastructure is in place (notification tasks)
   - Add email sending in task functions
   - Add user preferences for email notifications

2. **WebSocket Support**
   - Real-time push notifications
   - Remove polling requirement
   - Better user experience

3. **Notification Preferences**
   - Allow users to configure which events trigger notifications
   - Store preferences in user profile

4. **Rich Notifications**
   - Add images/avatars
   - Add action buttons (Approve, View, etc.)
   - Deep links to relevant pages

5. **Notification Categories**
   - Group notifications by type
   - Add filtering in UI
   - Separate badges per category

## Configuration

### Environment Variables

No additional configuration required. The notification system uses the existing Django and database configuration.

### Settings

Notifications are enabled by default. To disable:

```python
# settings.py
NOTIFICATIONS_ENABLED = False  # Default: True
```

## Troubleshooting

### Notifications Not Appearing

1. Check signal receivers are connected:
   ```python
   # In notifications/apps.py
   def ready(self):
       import notifications.receivers
   ```

2. Verify signals are being sent:
   ```python
   # Add logging in view
   logger.info(f"Sending signal: {signal_name}")
   ```

3. Check database for notification records:
   ```python
   Notification.objects.filter(recipient=user).count()
   ```

### Performance Issues

1. Check database indexes exist:
   ```sql
   \d notifications_notification
   ```

2. Monitor query count in API calls:
   ```python
   from django.db import connection
   len(connection.queries)
   ```

3. Reduce polling frequency if needed:
   ```typescript
   // Change from 30000 to 60000 (60 seconds)
   const interval = setInterval(fetchNotifications, 60000);
   ```

## Security

### Authentication & Authorization

- All endpoints require authentication
- Users can only access their own notifications
- No sensitive data exposed in notification messages

### Data Privacy

- Notifications are user-specific
- Deleted users cascade-delete their notifications
- No PII in notification messages

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## Support

For issues or questions about the notification system, please:
1. Check this documentation
2. Review existing tests for examples
3. Check the logs for error messages
4. Create an issue in the repository
