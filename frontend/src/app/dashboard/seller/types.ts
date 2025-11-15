// TypeScript interfaces for Seller Dashboard

export interface Stats {
  activeTransactions: number;
  pendingWork: number;
  totalEarnings: number;
  completedProjects: number;
}

export interface Transaction {
  id: number;
  title: string;
  buyer: string;
  amount: number;
  status: 'pending' | 'in_progress' | 'review' | 'completed';
  statusLabel: string;
}

export interface WorkItem {
  id: number;
  title: string;
  project: string;
  dueDate: string;
}
