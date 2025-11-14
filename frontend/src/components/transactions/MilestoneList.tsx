import { MilestoneListProps } from '@/types/transaction';

export function MilestoneList({ milestones, isBuyer, isSeller }: MilestoneListProps) {
    
    const handleApprove = async (milestoneId: number) => {
        // const store = useTransactionStore();
        // await api.post(`/api/milestones/${milestoneId}/approve/`);
        // store.fetchTransaction(milestone.transaction_id);
        console.log('Approving milestone:', milestoneId);
    };

    const handleSubmitWork = async (milestoneId: number) => {
        // Implementation will be added
        console.log('Submitting work for milestone:', milestoneId);
    };

    const handleRequestRevision = async (milestoneId: number) => {
        console.log('Requesting revision for milestone:', milestoneId);
    };

    const handleOpenDispute = async (milestoneId: number) => {
        console.log('Opening dispute for milestone:', milestoneId);
    };

    const getStatusBadgeColor = (status: string) => {
        switch (status) {
            case 'PENDING':
                return 'bg-yellow-100 text-yellow-800';
            case 'AWAITING_REVIEW':
                return 'bg-blue-100 text-blue-800';
            case 'APPROVED':
                return 'bg-green-100 text-green-800';
            case 'REVISION_REQUESTED':
                return 'bg-orange-100 text-orange-800';
            case 'DISPUTED':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    };

    if (milestones.length === 0) {
        return (
            <div className="text-center py-8 text-gray-500">
                No milestones defined for this transaction.
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {milestones.map((milestone, index) => (
                <div
                    key={milestone.id}
                    className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                >
                    <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-gray-700 font-semibold text-sm">
                                    {index + 1}
                                </span>
                                <h3 className="text-lg font-semibold text-gray-900">{milestone.title}</h3>
                            </div>
                            {milestone.description && (
                                <p className="text-gray-600 ml-11">{milestone.description}</p>
                            )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeColor(milestone.status)}`}>
                                {milestone.status.replace('_', ' ')}
                            </span>
                            <span className="text-lg font-bold text-gray-900">{formatCurrency(milestone.value)}</span>
                        </div>
                    </div>
                    
                    {/* Buyer Action Buttons */}
                    {isBuyer && milestone.status === 'AWAITING_REVIEW' && (
                        <div className="mt-4 pt-4 border-t border-gray-200 flex flex-wrap gap-2">
                            <button
                                onClick={() => handleApprove(milestone.id)}
                                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                            >
                                ✓ Approve & Release {formatCurrency(milestone.value)}
                            </button>
                            <button
                                onClick={() => handleRequestRevision(milestone.id)}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                            >
                                Request Revision
                            </button>
                            <button
                                onClick={() => handleOpenDispute(milestone.id)}
                                className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                            >
                                Open Dispute
                            </button>
                        </div>
                    )}
                    
                    {/* Seller Action Buttons */}
                    {isSeller && milestone.status === 'PENDING' && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <button
                                onClick={() => handleSubmitWork(milestone.id)}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                            >
                                Submit Work for this Milestone
                            </button>
                        </div>
                    )}
                    {isSeller && milestone.status === 'REVISION_REQUESTED' && (
                        <div className="mt-4 pt-4 border-t border-gray-200 bg-orange-50 -m-5 mt-4 p-5 rounded-b-lg">
                            <p className="text-orange-800 text-sm mb-3">
                                ⚠️ The buyer has requested revisions to this milestone.
                            </p>
                            <button
                                onClick={() => handleSubmitWork(milestone.id)}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                            >
                                Re-submit Work
                            </button>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
