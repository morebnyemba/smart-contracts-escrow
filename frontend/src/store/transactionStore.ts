import { create } from 'zustand';
import { Transaction, Milestone } from '@/types/transaction';

interface TransactionStore {
  activeTransaction: Transaction | null;
  milestones: Milestone[];
  fetchTransaction: (tx_id: string) => Promise<void>;
  updateMilestoneStatus: (milestone_id: number, status: Milestone['status']) => void;
}

export const useTransactionStore = create<TransactionStore>((set) => ({
  activeTransaction: null,
  milestones: [],
  fetchTransaction: async (tx_id: string) => {
    // Simulate API call
    const dummyTransaction: Transaction = {
      id: tx_id,
      title: "Project Alpha",
      status: "IN_ESCROW",
      total_value: 200.00,
      buyer: { id: 1, username: "buyer_user" },
      seller: { id: 2, username: "seller_user" },
    };
    const dummyMilestones: Milestone[] = [
      { id: 101, title: "Milestone 1", value: 50.00, status: "AWAITING_REVIEW", transaction_id: tx_id },
      { id: 102, title: "Milestone 2", value: 50.00, status: "PENDING", transaction_id: tx_id },
      { id: 103, title: "Milestone 3", value: 50.00, status: "PENDING", transaction_id: tx_id },
      { id: 104, title: "Milestone 4", value: 50.00, status: "PENDING", transaction_id: tx_id },
    ];
    set({ activeTransaction: dummyTransaction, milestones: dummyMilestones });
  },
  updateMilestoneStatus: (milestone_id: number, status: Milestone['status']) => set((state) => ({
    milestones: state.milestones.map((m) =>
      m.id === milestone_id ? { ...m, status } : m
    ),
  })),
}));
