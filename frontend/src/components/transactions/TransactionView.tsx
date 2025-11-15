import { MilestoneList } from './MilestoneList';
import { TransactionViewProps } from '@/types/transaction';

export function TransactionView({ transaction, milestones, isBuyer, isSeller }: TransactionViewProps) {
    const getStatusBadgeColor = (status: string) => {
        switch (status) {
            case 'IN_ESCROW':
                return 'bg-blue-100 text-blue-800';
            case 'COMPLETED':
                return 'bg-green-100 text-green-800';
            case 'DISPUTED':
                return 'bg-red-100 text-red-800';
            case 'CANCELLED':
                return 'bg-gray-100 text-gray-800';
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

    const calculateProgress = () => {
        const approvedMilestones = milestones.filter(m => m.status === 'APPROVED').length;
        return milestones.length > 0 ? (approvedMilestones / milestones.length) * 100 : 0;
    };

    const progress = calculateProgress();

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
        <div className="max-w-5xl mx-auto p-6 space-y-6">
            {/* Header Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">{transaction.title}</h1>
                        {transaction.description && (
                            <p className="text-gray-600">{transaction.description}</p>
                        )}
                    </div>
                    <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getStatusBadgeColor(transaction.status)}`}>
                        {transaction.status.replace('_', ' ')}
                    </span>
                </div>

                {/* Transaction Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
                    <div>
                        <p className="text-sm text-gray-500 mb-1">Total Value</p>
                        <p className="text-2xl font-bold text-gray-900">{formatCurrency(transaction.total_value)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500 mb-1">Buyer</p>
                        <p className="text-lg font-semibold text-gray-900">{transaction.buyer.username}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500 mb-1">Seller</p>
                        <p className="text-lg font-semibold text-gray-900">{transaction.seller.username}</p>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6">
                    <div className="flex justify-between items-center mb-2">
                        <p className="text-sm font-medium text-gray-700">Project Progress</p>
                        <p className="text-sm text-gray-600">{Math.round(progress)}%</p>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Milestones Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Milestones</h2>
                <MilestoneList
                    milestones={milestones}
                    isBuyer={isBuyer}
                    isSeller={isSeller}
                />
            </div>

            {/* Completion Section */}
            {transaction.status === 'COMPLETED' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-green-900 mb-3">🎉 Project Complete!</h3>
                    <p className="text-green-700 mb-4">
                        Congratulations! This project has been completed successfully.
                    </p>
                    <button className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors">
                        Leave Review
                    </button>
                </div>
            )}
        </div>
    );
}
