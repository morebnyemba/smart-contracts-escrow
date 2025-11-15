export interface Notification {
  id: number;
  recipient: number;
  recipient_username: string;
  notification_type: 'TRANSACTION_ACCEPTED' | 'ESCROW_FUNDED' | 'WORK_SUBMITTED' | 'MILESTONE_APPROVED' | 'REVISION_REQUESTED' | 'TRANSACTION_COMPLETED';
  message: string;
  transaction: number | null;
  transaction_title: string | null;
  milestone: number | null;
  milestone_title: string | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notification[];
}

export interface UnreadCountResponse {
  count: number;
}
