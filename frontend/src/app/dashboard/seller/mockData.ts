// Mock data for Seller Dashboard
// In a real app, this would come from API/store

import { Stats, Transaction, WorkItem } from './types';

export const mockStats: Stats = {
  activeTransactions: 3,
  pendingWork: 5,
  totalEarnings: 1250.00,
  completedProjects: 12,
};

export const mockActiveTransactions: Transaction[] = [
  {
    id: 1,
    title: 'E-commerce Website Development',
    buyer: 'John Doe',
    amount: 500.00,
    status: 'in_progress',
    statusLabel: 'In Progress',
  },
  {
    id: 2,
    title: 'Mobile App UI Design',
    buyer: 'Jane Smith',
    amount: 350.00,
    status: 'review',
    statusLabel: 'Under Review',
  },
  {
    id: 3,
    title: 'Logo Design Package',
    buyer: 'Tech Startup Inc',
    amount: 200.00,
    status: 'pending',
    statusLabel: 'Pending',
  },
];

export const mockPendingWork: WorkItem[] = [
  {
    id: 101,
    title: 'Homepage Design',
    project: 'E-commerce Website Development',
    dueDate: '2 days',
  },
  {
    id: 102,
    title: 'Product Catalog',
    project: 'E-commerce Website Development',
    dueDate: '5 days',
  },
  {
    id: 103,
    title: 'Final UI Mockups',
    project: 'Mobile App UI Design',
    dueDate: '1 day',
  },
];
