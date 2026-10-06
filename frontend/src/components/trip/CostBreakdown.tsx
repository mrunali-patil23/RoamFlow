import React, { useState } from 'react';
import { CostBreakdown as CostBreakdownType, DailyCost } from '../../types/trip';

interface CostBreakdownProps {
  costBreakdown: CostBreakdownType;
  className?: string;
}

interface CostCategoryProps {
  label: string;
  amount: number;
  icon: string;
  color: string;
  percentage: number;
}

interface DailyCostRowProps {
  dailyCost: DailyCost;
}

const CostCategory: React.FC<CostCategoryProps> = ({ label, amount, icon, color, percentage }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center space-x-3">
        <div className={`w-10 h-10 rounded-full ${color} flex items-center justify-center text-white`}>
          <span className="text-lg">{icon}</span>
        </div>
        <div>
          <div className="font-semibold text-gray-900 dark:text-white">{label}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {percentage.toFixed(1)}% of total
          </div>
        </div>
      </div>
      
      <div className="text-right">
        <div className="text-lg font-bold text-gray-900 dark:text-white">
          {formatCurrency(amount)}
        </div>
        <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-1">
          <div 
            className={`h-2 rounded-full ${color}`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

const DailyCostRow: React.FC<DailyCostRowProps> = ({ dailyCost }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <tr className="border-b border-gray-200 dark:border-gray-700">
      <td className="py-3 px-4 text-sm font-medium text-gray-900 dark:text-white">
        Day {dailyCost.dayNumber}
      </td>
      <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
        {formatDate(dailyCost.date)}
      </td>
      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white text-right">
        {formatCurrency(dailyCost.flightCostInr)}
      </td>
      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white text-right">
        {formatCurrency(dailyCost.hotelCostInr)}
      </td>
      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white text-right">
        {formatCurrency(dailyCost.attractionsCostInr)}
      </td>
      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white text-right">
        {formatCurrency(dailyCost.eventsCostInr)}
      </td>
      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white text-right">
        {formatCurrency(dailyCost.localExpensesInr)}
      </td>
      <td className="py-3 px-4 text-sm font-bold text-blue-600 dark:text-blue-400 text-right">
        {formatCurrency(dailyCost.totalCostInr)}
      </td>
    </tr>
  );
};

const CostBreakdown: React.FC<CostBreakdownProps> = ({ costBreakdown, className = '' }) => {
  const [activeView, setActiveView] = useState<'section' | 'daily'>('section');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const calculatePercentage = (amount: number) => {
    return costBreakdown.totalCostInr > 0 ? (amount / costBreakdown.totalCostInr) * 100 : 0;
  };

  const costCategories = [
    {
      label: 'Flights',
      amount: costBreakdown.flightCostInr,
      icon: '✈️',
      color: 'bg-blue-500',
      percentage: calculatePercentage(costBreakdown.flightCostInr),
    },
    {
      label: 'Hotels',
      amount: costBreakdown.hotelCostInr,
      icon: '🏨',
      color: 'bg-green-500',
      percentage: calculatePercentage(costBreakdown.hotelCostInr),
    },
    {
      label: 'Attractions',
      amount: costBreakdown.attractionsCostInr,
      icon: '🏛️',
      color: 'bg-purple-500',
      percentage: calculatePercentage(costBreakdown.attractionsCostInr),
    },
    {
      label: 'Events',
      amount: costBreakdown.eventsCostInr,
      icon: '🎭',
      color: 'bg-orange-500',
      percentage: calculatePercentage(costBreakdown.eventsCostInr),
    },
    {
      label: 'Local Expenses',
      amount: costBreakdown.localExpensesInr,
      icon: '🍽️',
      color: 'bg-red-500',
      percentage: calculatePercentage(costBreakdown.localExpensesInr),
    },
  ];

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 mb-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Cost Breakdown
          </h2>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {formatCurrency(costBreakdown.totalCostInr)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Total Trip Cost
            </div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveView('section')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeView === 'section'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Section-wise
          </button>
          <button
            onClick={() => setActiveView('daily')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeView === 'daily'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Day-wise
          </button>
        </div>
      </div>

      {/* Section-wise View */}
      {activeView === 'section' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Cost by Category
          </h3>
          {costCategories.map((category, index) => (
            <CostCategory
              key={index}
              label={category.label}
              amount={category.amount}
              icon={category.icon}
              color={category.color}
              percentage={category.percentage}
            />
          ))}
        </div>
      )}

      {/* Daily View */}
      {activeView === 'daily' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Daily Cost Breakdown
            </h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Day
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Flights
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Hotels
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Attractions
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Events
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Local
                  </th>
                  <th className="py-3 px-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {costBreakdown.dailyBreakdown.map((dailyCost) => (
                  <DailyCostRow key={dailyCost.dayNumber} dailyCost={dailyCost} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default CostBreakdown;