export interface User {
  id: number;
  username: string;
}

export interface Transaction {
  id: string | number;
  title: string;
  description?: string;
  status: 'IN_ESCROW' | 'COMPLETED' | 'DISPUTED' | 'CANCELLED';
  total_value: number;
  buyer: User;
  seller: User;
  created_at?: string;
  updated_at?: string;
}

export interface Milestone {
  id: number;
  title: string;
  description?: string;
  value: number;
  status: 'PENDING' | 'AWAITING_REVIEW' | 'APPROVED' | 'REVISION_REQUESTED' | 'DISPUTED';
  transaction_id: string | number;
  due_date?: string;
}

export interface TransactionViewProps {
  transaction: Transaction;
  milestones: Milestone[];
  isBuyer: boolean;
  isSeller: boolean;
}

export interface MilestoneListProps {
  milestones: Milestone[];
  isBuyer: boolean;
  isSeller: boolean;
}
