'use client';

import { TransactionView } from '@/components/transactions/TransactionView';
import { useUserStore } from '@/store/userStore';
import { useEffect, useState } from 'react';
import { transactionAPI } from '@/lib/api';
import { Transaction as ApiTransaction } from '@/lib/api';
import { Transaction, Milestone } from '@/types/transaction';

export default function TransactionPage({ params }: { params: { tx_id: string } }) {
    const { tx_id } = params;
    const { user } = useUserStore();
    const [transaction, setTransaction] = useState<Transaction | null>(null);
    const [milestones, setMilestones] = useState<Milestone[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        const fetchTransaction = async () => {
            if (!tx_id) return;

            try {
                const response = await transactionAPI.getById(tx_id);
                
                if (response.error) {
                    setError(response.error);
                } else if (response.data) {
                    // Map API response to component interface
                    const apiTx: ApiTransaction = response.data;
                    const mappedTx: Transaction = {
                        id: apiTx.id,
                        title: apiTx.title,
                        description: apiTx.description,
                        status: apiTx.status as Transaction['status'],
                        total_value: parseFloat(apiTx.total_value),
                        buyer: apiTx.buyer,
                        seller: apiTx.seller,
                        created_at: apiTx.created_at,
                    };
                    
                    const mappedMilestones: Milestone[] = apiTx.milestones.map(m => ({
                        id: m.id,
                        title: m.title,
                        description: m.description,
                        value: parseFloat(m.value),
                        status: m.status as Milestone['status'],
                        transaction_id: apiTx.id,
                    }));
                    
                    setTransaction(mappedTx);
                    setMilestones(mappedMilestones);
                }
            } catch (err) {
                setError('Failed to fetch transaction');
                console.error('Error fetching transaction:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchTransaction();
    }, [tx_id]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    <p className="mt-4 text-gray-600">Loading transaction...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center text-red-600">
                    <p className="text-xl font-semibold mb-2">Error</p>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center text-gray-600">
                    <p className="text-xl font-semibold mb-2">Authentication Required</p>
                    <p>Please log in to view this transaction.</p>
                </div>
            </div>
        );
    }

    if (!transaction) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center text-gray-600">
                    <p>Transaction not found.</p>
                </div>
            </div>
        );
    }

    const isBuyer = user.id === transaction.buyer.id;
    const isSeller = user.id === transaction.seller.id;

    return (
        <TransactionView
            transaction={transaction}
            milestones={milestones}
            isBuyer={isBuyer}
            isSeller={isSeller}
        />
    );
}
