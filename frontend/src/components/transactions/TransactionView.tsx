import { MilestoneList } from './MilestoneList';

interface User {
    id: number;
    username: string;
}

interface Transaction {
    id: string;
    title: string;
    status: string;
    total_value: number;
    buyer: User;
    seller: User;
}

interface Milestone {
    id: number;
    title: string;
    value: number;
    status: string;
    transaction_id: string;
}

interface TransactionViewProps {
    transaction: Transaction;
    milestones: Milestone[];
    isBuyer: boolean;
    isSeller: boolean;
}

export function TransactionView({ transaction, milestones, isBuyer, isSeller }: TransactionViewProps) {
    return (
        <div>
            <h2>{transaction.title}</h2>
            <p>Status: {transaction.status}</p>
            <p>Total Value: ${transaction.total_value}</p>

            <MilestoneList
                milestones={milestones}
                isBuyer={isBuyer}
                isSeller={isSeller}
            />
            
            {/* Logic for "Leave Review" button (Step 8) */}
            {transaction.status === 'COMPLETED' && (
                <div>
                    <h3>Project Complete!</h3>
                    <button>Leave Review</button>
                </div>
            )}
        </div>
    );
}
