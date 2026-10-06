import React from 'react';
import { BudgetStatus as BudgetStatusType } from '../../types/trip';

interface BudgetStatusProps {
  budgetStatus: BudgetStatusType;
  maxBudget: number;
  totalCost: number;
  className?: string;
}

const BudgetStatus: React.FC<BudgetStatusProps> = ({ 
  budgetStatus, 
  maxBudget, 
  totalCost, 
  className = '' 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Within Budget':
        return {
          bg: 'bg-green-50 dark:bg-green-900/20',
          border: 'border-green-200 dark:border-green-800',
          text: 'text-green-800 dark:text-green-200',
          icon: '✅',
          progressColor: 'bg-green-500',
        };
      case 'Slightly Over Budget':
        return {
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-yellow-200 dark:border-yellow-800',
          text: 'text-yellow-800 dark:text-yellow-200',
          icon: '⚠️',
          progressColor: 'bg-yellow-500',
        };
      case 'Over Budget':
        return {
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-red-200 dark:border-red-800',
          text: 'text-red-800 dark:text-red-200',
          icon: '❌',
          progressColor: 'bg-red-500',
        };
      default:
        return {
          bg: 'bg-gray-50 dark:bg-gray-900/20',
          border: 'border-gray-200 dark:border-gray-800',
          text: 'text-gray-800 dark:text-gray-200',
          icon: '📊',
          progressColor: 'bg-gray-500',
        };
    }
  };

  const statusStyle = getStatusColor(budgetStatus.status);
  const budgetUsagePercentage = maxBudget > 0 ? (totalCost / maxBudget) * 100 : 0;
  const isOverBudget = totalCost > maxBudget;

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <div className={`rounded-xl p-6 border ${statusStyle.bg} ${statusStyle.border} shadow-lg`}>
        {/* Status Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{statusStyle.icon}</span>
            <div>
              <h2 className={`text-xl font-bold ${statusStyle.text}`}>
                {budgetStatus.status}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Budget Analysis
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`text-2xl font-bold ${statusStyle.text}`}>
              {isOverBudget ? '+' : ''}{formatCurrency(Math.abs(budgetStatus.differenceInr))}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">
              {isOverBudget ? 'Over Budget' : 'Under Budget'}
            </div>
          </div>
        </div>

        {/* Budget Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Budget Usage
            </span>
            <span className={`text-sm font-medium ${statusStyle.text}`}>
              {budgetUsagePercentage.toFixed(1)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-300 ${statusStyle.progressColor}`}
              style={{ width: `${Math.min(budgetUsagePercentage, 100)}%` }}
            ></div>
            {budgetUsagePercentage > 100 && (
              <div className="relative">
                <div 
                  className="absolute top-0 h-3 bg-red-600 rounded-full opacity-50"
                  style={{ 
                    width: `${Math.min((budgetUsagePercentage - 100), 50)}%`,
                    left: '100%'
                  }}
                ></div>
              </div>
            )}
          </div>
          
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>₹0</span>
            <span>{formatCurrency(maxBudget)}</span>
            {isOverBudget && (
              <span className="text-red-600 dark:text-red-400">
                {formatCurrency(totalCost)}
              </span>
            )}
          </div>
        </div>

        {/* Budget Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatCurrency(maxBudget)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Maximum Budget
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {formatCurrency(totalCost)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Estimated Cost
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 text-center">
            <div className={`text-lg font-bold ${isOverBudget ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
              {formatCurrency(Math.abs(budgetStatus.differenceInr))}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {isOverBudget ? 'Over Budget' : 'Remaining'}
            </div>
          </div>
        </div>

        {/* Suggestions */}
        {budgetStatus.suggestions && budgetStatus.suggestions.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
              <span className="mr-2">💡</span>
              Cost-Saving Suggestions
            </h3>
            <ul className="space-y-2">
              {budgetStatus.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {suggestion}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Additional Info for Within Budget */}
        {budgetStatus.status === 'Within Budget' && budgetStatus.differenceInr < 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mt-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
              <span className="mr-2">🎉</span>
              Great News!
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Your trip is well within budget! You have {formatCurrency(Math.abs(budgetStatus.differenceInr))} 
              remaining that you could use for additional activities, upgrades, or save for future trips.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BudgetStatus;