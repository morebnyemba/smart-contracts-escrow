export function MilestoneList({ milestones, isBuyer, isSeller }) {
    
    const handleApprove = async (milestoneId) => {
        // const store = useTransactionStore();
        // await api.post(`/api/milestones/${milestoneId}/approve/`);
        // store.fetchTransaction(milestone.transaction_id);
    };

    const handleSubmitWork = async (milestoneId) => {
        // ...
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
