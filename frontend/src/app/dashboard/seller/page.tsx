'use client';

import { useEffect, useState } from 'react';
import styles from './page.module.css';
import { transactionAPI } from '@/lib/api';
import { Transaction as LocalTransaction } from './types';

interface Stats {
  activeTransactions: number;
  pendingWork: number;
  totalEarnings: number;
  completedProjects: number;
}

interface WorkItem {
  id: number;
  title: string;
  project: string;
  dueDate: string;
}

export default function SellerPortal() {
  const [stats, setStats] = useState<Stats>({
    activeTransactions: 0,
    pendingWork: 0,
    totalEarnings: 0,
    completedProjects: 0,
  });
  const [activeTransactions, setActiveTransactions] = useState<LocalTransaction[]>([]);
  const [pendingWork, setPendingWork] = useState<WorkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await transactionAPI.getAll();
        
        if (response.error) {
          setError(response.error);
          setLoading(false);
          return;
        }

        if (response.data) {
          const transactions = response.data.results;
          
          // Map transactions to local format
          const mapped = transactions
            .filter(tx => tx.status === 'IN_ESCROW' || tx.status === 'COMPLETED')
            .map(tx => {
              let status: LocalTransaction['status'] = 'pending';
              let statusLabel = 'Pending';
              
              if (tx.status === 'COMPLETED') {
                status = 'completed';
                statusLabel = 'Completed';
              } else if (tx.milestones.some(m => m.status === 'AWAITING_REVIEW')) {
                status = 'review';
                statusLabel = 'Under Review';
              } else if (tx.milestones.some(m => m.status === 'PENDING' || m.status === 'REVISION_REQUESTED')) {
                status = 'in_progress';
                statusLabel = 'In Progress';
              }
              
              return {
                id: tx.id,
                title: tx.title,
                buyer: tx.buyer.username,
                amount: parseFloat(tx.total_value),
                status,
                statusLabel,
              };
            });
          
          setActiveTransactions(mapped);
          
          // Extract pending work items from milestones
          const workItems: WorkItem[] = [];
          transactions.forEach(tx => {
            tx.milestones
              .filter(m => m.status === 'PENDING' || m.status === 'REVISION_REQUESTED')
              .forEach(m => {
                workItems.push({
                  id: m.id,
                  title: m.title,
                  project: tx.title,
                  dueDate: 'TBD', // API doesn't provide due date yet
                });
              });
          });
          setPendingWork(workItems);
          
          // Calculate stats
          const completedCount = transactions.filter(tx => tx.status === 'COMPLETED').length;
          const activeCount = transactions.filter(tx => tx.status === 'IN_ESCROW').length;
          const totalEarnings = transactions
            .filter(tx => tx.status === 'COMPLETED')
            .reduce((sum, tx) => sum + parseFloat(tx.total_value), 0);
          
          setStats({
            activeTransactions: activeCount,
            pendingWork: workItems.length,
            totalEarnings,
            completedProjects: completedCount,
          });
        }
      } catch (err) {
        setError('Failed to fetch dashboard data');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusBadgeClass = (status: LocalTransaction['status']) => {
    switch (status) {
      case 'pending':
        return styles.pending;
      case 'in_progress':
        return styles.inProgress;
      case 'review':
        return styles.review;
      case 'completed':
        return styles.completed;
      default:
        return styles.pending;
    }
  };

  const handleViewAllTransactions = () => {
    console.log('Navigate to all transactions');
    // TODO: Implement navigation to full transactions list
  };

  const handleViewAllWorkItems = () => {
    console.log('Navigate to all work items');
    // TODO: Implement navigation to full work items list
  };

  const handleSubmitWork = (workItemId: number) => {
    console.log('Submit work for item:', workItemId);
    // TODO: Implement work submission logic
  };

  const handleTransactionClick = (transactionId: number) => {
    console.log('View transaction details:', transactionId);
    // TODO: Implement navigation to transaction details page
  };

  if (loading) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.container}>
          <div className={styles.header}>Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.container}>
          <div className={styles.header} style={{ color: 'red' }}>{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <h1>Seller Dashboard</h1>
          <p>Manage your projects, track earnings, and submit work</p>
        </div>

        {/* Stats Grid */}
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <h3>Active Transactions</h3>
            <div className={styles.value}>{stats.activeTransactions}</div>
            <div className={styles.subtext}>Currently in progress</div>
          </div>
          <div className={styles.statCard}>
            <h3>Pending Work Items</h3>
            <div className={styles.value}>{stats.pendingWork}</div>
            <div className={styles.subtext}>Milestones to complete</div>
          </div>
          <div className={styles.statCard}>
            <h3>Total Earnings</h3>
            <div className={styles.value}>${stats.totalEarnings.toFixed(2)}</div>
            <div className={styles.subtext}>All time revenue</div>
          </div>
          <div className={styles.statCard}>
            <h3>Completed Projects</h3>
            <div className={styles.value}>{stats.completedProjects}</div>
            <div className={styles.subtext}>Successfully delivered</div>
          </div>
        </div>

        {/* Active Transactions Section */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>Active Transactions</h2>
            <button 
              className={styles.viewAllButton}
              onClick={handleViewAllTransactions}
            >
              View All
            </button>
          </div>
          <div className={styles.transactionsList}>
            {activeTransactions.map((transaction) => (
              <button
                key={transaction.id}
                className={styles.transactionCard}
                onClick={() => handleTransactionClick(transaction.id)}
                aria-label={`View details for ${transaction.title}`}
              >
                <div className={styles.transactionInfo}>
                  <h4>{transaction.title}</h4>
                  <p>Buyer: {transaction.buyer}</p>
                </div>
                <div className={styles.transactionMeta}>
                  <span className={`${styles.badge} ${getStatusBadgeClass(transaction.status)}`}>
                    {transaction.statusLabel}
                  </span>
                  <span className={styles.amount}>${transaction.amount.toFixed(2)}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Pending Work Items Section */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>Pending Work Items</h2>
            <button 
              className={styles.viewAllButton}
              onClick={handleViewAllWorkItems}
            >
              View All
            </button>
          </div>
          {pendingWork.length > 0 ? (
            <div className={styles.workItemsList}>
              {pendingWork.map((item) => (
                <div key={item.id} className={styles.workItem}>
                  <div className={styles.workItemInfo}>
                    <h4>{item.title}</h4>
                    <p>{item.project} • Due in {item.dueDate}</p>
                  </div>
                  <button 
                    className={styles.submitButton}
                    onClick={() => handleSubmitWork(item.id)}
                  >
                    Submit Work
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <p>No pending work items</p>
              <span className={styles.subtext}>All caught up! Great work.</span>
            </div>
          )}
        </div>

        {/* Profile & Verification Section */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>Profile & Verification</h2>
          </div>
          <div className={styles.profileSection}>
            <div className={styles.profileCard}>
              <h4>Account Status</h4>
              <div className={styles.profileItem}>
                <span>Verification Status</span>
                <span className={`${styles.verificationStatus} ${styles.verified}`}>
                  ✓ Verified
                </span>
              </div>
              <div className={styles.profileItem}>
                <span>Member Since</span>
                <span>Jan 2024</span>
              </div>
              <div className={styles.profileItem}>
                <span>Response Time</span>
                <span>2 hours</span>
              </div>
            </div>
            <div className={styles.profileCard}>
              <h4>Performance Metrics</h4>
              <div className={styles.profileItem}>
                <span>Success Rate</span>
                <span>96%</span>
              </div>
              <div className={styles.profileItem}>
                <span>On-Time Delivery</span>
                <span>94%</span>
              </div>
              <div className={styles.profileItem}>
                <span>Buyer Rating</span>
                <span>4.8 / 5.0</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
