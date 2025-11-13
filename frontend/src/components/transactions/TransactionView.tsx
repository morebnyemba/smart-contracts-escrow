import { MilestoneList } from './MilestoneList';

export function TransactionView({ transaction, milestones, isBuyer, isSeller }) {
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
