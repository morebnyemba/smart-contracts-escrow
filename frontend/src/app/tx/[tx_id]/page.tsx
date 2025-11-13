'use client';

import { TransactionView } from '@/components/transactions/TransactionView';
import { useTransactionStore } from '@/store/transactionStore';
import { useUserStore } from '@/store/userStore';
import { useEffect } from 'react';

interface TransactionPageProps {
    params: {
        tx_id: string;
    };
}

export default function TransactionPage({ params }: TransactionPageProps) {
    const { tx_id } = params;
    const { user } = useUserStore();
    const { activeTransaction, milestones, fetchTransaction } = useTransactionStore();

    useEffect(() => {
        if (tx_id) {
            fetchTransaction(tx_id);
        }
    }, [tx_id, fetchTransaction]);

    if (!activeTransaction || !user) {
        return <div>Loading...</div>;
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
