interface Milestone {
    id: number;
    title: string;
    value: number;
    status: string;
    transaction_id: string;
}

interface MilestoneListProps {
    milestones: Milestone[];
    isBuyer: boolean;
    isSeller: boolean;
}

export function MilestoneList({ milestones, isBuyer, isSeller }: MilestoneListProps) {
    
    const handleApprove = async (milestoneId: number) => {
        // const store = useTransactionStore();
        // await api.post(`/api/milestones/${milestoneId}/approve/`);
        // store.fetchTransaction(milestone.transaction_id);
        console.log('Approving milestone', milestoneId);
    };

    const handleSubmitWork = async (milestoneId: number) => {
        // ...
        console.log('Submitting work for milestone', milestoneId);
    };

    return (
        <ul>
            {milestones.map((milestone) => (
                <li key={milestone.id}>
                    <strong>{milestone.title} (${milestone.value})</strong>
                    <p>Status: {milestone.status}</p>
                    
                    {/* --- BUYER BUTTONS --- */}
                    {isBuyer && milestone.status === 'AWAITING_REVIEW' && (
                        <div>
                            <button onClick={() => handleApprove(milestone.id)}>
                                Approve Work (Release ${milestone.value})
                            </button>
                            <button>Request Revision</button>
                            <button>Open Dispute</button>
                        </div>
                    )}
                    
                    {/* --- SELLER BUTTONS --- */}
                    {isSeller && milestone.status === 'PENDING' && (
                        <button onClick={() => handleSubmitWork(milestone.id)}>
                            Submit Work for this Milestone
                        </button>
                    )}
                    {isSeller && milestone.status === 'REVISION_REQUESTED' && (
                        <button onClick={() => handleSubmitWork(milestone.id)}>
                            Re-submit Work
                        </button>
                    )}
                </li>
            ))}
        </ul>
    );
}
