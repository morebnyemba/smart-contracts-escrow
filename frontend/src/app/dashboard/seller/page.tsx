'use client';

import styles from './page.module.css';
import { mockStats, mockActiveTransactions, mockPendingWork } from './mockData';
import { Transaction } from './types';

export default function SellerPortal() {
  const stats = mockStats;
  const activeTransactions = mockActiveTransactions;
  const pendingWork = mockPendingWork;

  const getStatusBadgeClass = (status: Transaction['status']) => {
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
