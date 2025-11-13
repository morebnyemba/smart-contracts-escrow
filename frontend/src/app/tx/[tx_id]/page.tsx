'use client';

import { TransactionView } from '@/components/transactions/TransactionView';
import { useTransactionStore } from '@/store/transactionStore';
import { useUserStore } from '@/store/userStore';
import { useEffect, useState, use } from 'react';

interface TransactionPageProps {
    params: Promise<{
        tx_id: string;
    }>;
}

export default function TransactionPage({ params }: TransactionPageProps) {
    const unwrappedParams = use(params);
    const { tx_id } = unwrappedParams;
    const { user } = useUserStore();
    const { activeTransaction, milestones, fetchTransaction } = useTransactionStore();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (tx_id) {
            fetchTransaction(tx_id).finally(() => setIsLoading(false));
        }
    }, [tx_id, fetchTransaction]);

    // Mock user for demo purposes
    useEffect(() => {
        if (!user) {
            // Check if we should simulate a seller (for demo purposes)
            const urlParams = new URLSearchParams(window.location.search);
            const userType = urlParams.get('as');
            
            // Simulate logged in user (buyer by default, seller if ?as=seller)
            const mockUser = userType === 'seller' 
                ? { id: 2, username: "seller_user" }
                : { id: 1, username: "buyer_user" };
            useUserStore.getState().login("mock-token", mockUser);
        }
    }, [user]);

    if (isLoading || !activeTransaction) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    <p className="mt-4 text-gray-600">Loading transaction...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return <div className="flex items-center justify-center min-h-screen text-gray-600">Please log in to view this transaction.</div>;
    }

    const isBuyer = user.id === activeTransaction.buyer.id;
    const isSeller = user.id === activeTransaction.seller.id;

    return (
        <TransactionView
            transaction={activeTransaction}
            milestones={milestones}
            isBuyer={isBuyer}
            isSeller={isSeller}
        />
    );
}
