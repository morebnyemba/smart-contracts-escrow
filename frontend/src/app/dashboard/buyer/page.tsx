'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import styles from './buyer.module.css';

interface Transaction {
  id: string;
  title: string;
  status: string;
  total_value: number;
  seller: { id: number; username: string };
  created_at: string;
  milestones_completed: number;
  total_milestones: number;
}

export default function BuyerPortal() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    // Simulate fetching buyer's transactions
    const dummyTransactions: Transaction[] = [
      {
        id: 'tx-001',
        title: 'Website Redesign Project',
        status: 'AWAITING_REVIEW',
        total_value: 5000,
        seller: { id: 2, username: 'webdesigner_pro' },
        created_at: '2025-11-01',
        milestones_completed: 2,
        total_milestones: 4,
      },
      {
        id: 'tx-002',
        title: 'Mobile App Development',
        status: 'IN_PROGRESS',
        total_value: 12000,
        seller: { id: 3, username: 'app_developer' },
        created_at: '2025-10-15',
        milestones_completed: 1,
        total_milestones: 6,
      },
      {
        id: 'tx-003',
        title: 'Logo Design',
        status: 'COMPLETED',
        total_value: 500,
        seller: { id: 4, username: 'creative_designer' },
        created_at: '2025-10-01',
        milestones_completed: 2,
        total_milestones: 2,
      },
      {
        id: 'tx-004',
        title: 'E-commerce Platform',
        status: 'IN_ESCROW',
        total_value: 8000,
        seller: { id: 5, username: 'fullstack_dev' },
        created_at: '2025-11-10',
        milestones_completed: 0,
        total_milestones: 5,
      },
    ];
    
    setTimeout(() => {
      setTransactions(dummyTransactions);
      setLoading(false);
    }, 500);
  }, []);

  const filteredTransactions = transactions.filter((tx) => {
    if (filter === 'all') return true;
    if (filter === 'active') return ['IN_PROGRESS', 'AWAITING_REVIEW', 'IN_ESCROW'].includes(tx.status);
    if (filter === 'completed') return tx.status === 'COMPLETED';
    return true;
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'AWAITING_REVIEW':
        return styles.statusAwaitingReview;
      case 'IN_PROGRESS':
        return styles.statusInProgress;
      case 'COMPLETED':
        return styles.statusCompleted;
      case 'IN_ESCROW':
        return styles.statusInEscrow;
      default:
        return styles.statusDefault;
    }
  };

  const formatStatus = (status: string) => {
    return status.replace(/_/g, ' ');
  };

  const totalValue = transactions.reduce((sum, tx) => sum + tx.total_value, 0);
  const activeCount = transactions.filter(tx => 
    ['IN_PROGRESS', 'AWAITING_REVIEW', 'IN_ESCROW'].includes(tx.status)
  ).length;
  const completedCount = transactions.filter(tx => tx.status === 'COMPLETED').length;

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Buyer Dashboard</h1>
        <p className={styles.subtitle}>Manage your transactions and track progress</p>
      </header>

      <div className={styles.stats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{activeCount}</div>
          <div className={styles.statLabel}>Active Projects</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{completedCount}</div>
          <div className={styles.statLabel}>Completed</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>${totalValue.toLocaleString()}</div>
          <div className={styles.statLabel}>Total Value</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{transactions.length}</div>
          <div className={styles.statLabel}>All Transactions</div>
        </div>
      </div>

      <div className={styles.filters}>
        <button 
          className={filter === 'all' ? styles.filterActive : styles.filterButton}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={filter === 'active' ? styles.filterActive : styles.filterButton}
          onClick={() => setFilter('active')}
        >
          Active
        </button>
        <button 
          className={filter === 'completed' ? styles.filterActive : styles.filterButton}
          onClick={() => setFilter('completed')}
        >
          Completed
        </button>
      </div>

      <div className={styles.transactionsList}>
        {filteredTransactions.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No transactions found</p>
            <Link href="/find-seller" className={styles.findSellerButton}>
              Find a Seller
            </Link>
          </div>
        ) : (
          filteredTransactions.map((transaction) => (
            <div key={transaction.id} className={styles.transactionCard}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>
                  <h3>{transaction.title}</h3>
                  <span className={`${styles.statusBadge} ${getStatusBadgeClass(transaction.status)}`}>
                    {formatStatus(transaction.status)}
                  </span>
                </div>
                <div className={styles.cardValue}>${transaction.total_value.toLocaleString()}</div>
              </div>
              
              <div className={styles.cardBody}>
                <div className={styles.cardInfo}>
                  <span className={styles.infoLabel}>Seller:</span>
                  <span className={styles.infoValue}>@{transaction.seller.username}</span>
                </div>
                <div className={styles.cardInfo}>
                  <span className={styles.infoLabel}>Progress:</span>
                  <span className={styles.infoValue}>
                    {transaction.milestones_completed} / {transaction.total_milestones} milestones
                  </span>
                </div>
                <div className={styles.progressBar}>
                  <div 
                    className={styles.progressFill}
                    style={{ 
                      width: `${(transaction.milestones_completed / transaction.total_milestones) * 100}%` 
                    }}
                  />
                </div>
              </div>

              <div className={styles.cardFooter}>
                <span className={styles.dateInfo}>Created: {transaction.created_at}</span>
                <div className={styles.actions}>
                  <Link href={`/tx/${transaction.id}`} className={styles.viewButton}>
                    View Details
                  </Link>
                  {transaction.status === 'AWAITING_REVIEW' && (
                    <button className={styles.approveButton}>
                      Review Work
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
