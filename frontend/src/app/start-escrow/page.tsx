'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import styles from './page.module.css';
import { transactionAPI, CreateTransactionData } from '@/lib/api';

interface Milestone {
  title: string;
  description: string;
  value: string;
}

export default function StartEscrowPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    seller: '',
    description: '',
  });
  const [milestones, setMilestones] = useState<Milestone[]>([
    { title: '', description: '', value: '' }
  ]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleMilestoneChange = (index: number, field: keyof Milestone, value: string) => {
    const updatedMilestones = [...milestones];
    updatedMilestones[index][field] = value;
    setMilestones(updatedMilestones);
  };

  const addMilestone = () => {
    setMilestones([...milestones, { title: '', description: '', value: '' }]);
  };

  const removeMilestone = (index: number) => {
    if (milestones.length > 1) {
      setMilestones(milestones.filter((_, i) => i !== index));
    }
  };

  const calculateTotal = () => {
    return milestones.reduce((sum, m) => sum + (parseFloat(m.value) || 0), 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.title.trim()) {
      setError('Please enter a transaction title');
      return;
    }

    if (!formData.seller.trim()) {
      setError('Please enter a seller ID');
      return;
    }

    const sellerId = parseInt(formData.seller);
    if (isNaN(sellerId) || sellerId <= 0) {
      setError('Please enter a valid seller ID (positive number)');
      return;
    }

    // Validate milestones
    for (let i = 0; i < milestones.length; i++) {
      const milestone = milestones[i];
      if (!milestone.title.trim()) {
        setError(`Please enter a title for milestone ${i + 1}`);
        return;
      }
      const value = parseFloat(milestone.value);
      if (isNaN(value) || value <= 0) {
        setError(`Please enter a valid amount for milestone ${i + 1}`);
        return;
      }
    }

    const totalValue = calculateTotal();
    if (totalValue <= 0) {
      setError('Total transaction value must be greater than 0');
      return;
    }

    setLoading(true);

    try {
      const transactionData: CreateTransactionData = {
        title: formData.title,
        seller: sellerId,
        milestones: milestones.map(m => ({
          title: m.title,
          description: m.description || undefined,
          value: parseFloat(m.value),
        })),
      };

      const response = await transactionAPI.create(transactionData);

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      if (response.data) {
        // Redirect to the transaction details page
        router.push(`/tx/${response.data.id}`);
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Error creating transaction:', err);
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <header className={styles.header}>
          <h1>Start Escrow Transaction</h1>
          <p className={styles.subtitle}>Create a new escrow transaction with milestones</p>
        </header>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>Transaction Details</h2>
            
            <div className={styles.formGroup}>
              <label htmlFor="title">Transaction Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g., Website Development Project"
                className={styles.input}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="seller">Seller ID *</label>
              <input
                type="text"
                id="seller"
                name="seller"
                value={formData.seller}
                onChange={handleChange}
                placeholder="Enter seller user ID (number)"
                className={styles.input}
                required
              />
              <small className={styles.helpText}>
                Enter the numeric user ID of the seller
              </small>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="description">Description (Optional)</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe the overall project or transaction..."
                className={styles.textarea}
                rows={3}
              />
            </div>
          </div>

          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Milestones</h2>
              <button
                type="button"
                onClick={addMilestone}
                className={styles.addButton}
              >
                + Add Milestone
              </button>
            </div>

            {milestones.map((milestone, index) => (
              <div key={index} className={styles.milestoneCard}>
                <div className={styles.milestoneHeader}>
                  <h3 className={styles.milestoneTitle}>Milestone {index + 1}</h3>
                  {milestones.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMilestone(index)}
                      className={styles.removeButton}
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor={`milestone-title-${index}`}>Milestone Title *</label>
                  <input
                    type="text"
                    id={`milestone-title-${index}`}
                    value={milestone.title}
                    onChange={(e) => handleMilestoneChange(index, 'title', e.target.value)}
                    placeholder="e.g., Design Phase"
                    className={styles.input}
                    required
                  />
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor={`milestone-description-${index}`}>Description</label>
                  <textarea
                    id={`milestone-description-${index}`}
                    value={milestone.description}
                    onChange={(e) => handleMilestoneChange(index, 'description', e.target.value)}
                    placeholder="Describe this milestone..."
                    className={styles.textarea}
                    rows={2}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor={`milestone-value-${index}`}>Amount (USD) *</label>
                  <input
                    type="number"
                    id={`milestone-value-${index}`}
                    value={milestone.value}
                    onChange={(e) => handleMilestoneChange(index, 'value', e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0.01"
                    className={styles.input}
                    required
                  />
                </div>
              </div>
            ))}
          </div>

          <div className={styles.summary}>
            <div className={styles.summaryRow}>
              <span className={styles.summaryLabel}>Total Transaction Value:</span>
              <span className={styles.summaryValue}>${calculateTotal().toFixed(2)}</span>
            </div>
            <div className={styles.summaryRow}>
              <span className={styles.summaryLabel}>Number of Milestones:</span>
              <span className={styles.summaryValue}>{milestones.length}</span>
            </div>
          </div>

          <div className={styles.actions}>
            <Link href="/dashboard/buyer" className={styles.cancelButton}>
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className={styles.submitButton}
            >
              {loading ? 'Creating...' : 'Create Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
