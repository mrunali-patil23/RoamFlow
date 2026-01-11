'use client';

import { BudgetCategory } from '@/types';

interface BudgetSelectorProps {
  value: BudgetCategory | '';
  onChange: (budget: BudgetCategory) => void;
  error?: string;
}

interface BudgetOption {
  value: BudgetCategory;
  label: string;
  description: string;
  icon: string;
}

const BUDGET_OPTIONS: BudgetOption[] = [
  {
    value: 'cheap',
    label: 'Budget',
    description: 'Affordable options, hostels, local transport',
    icon: '💰'
  },
  {
    value: 'moderate',
    label: 'Moderate',
    description: 'Mid-range hotels, mix of experiences',
    icon: '🏨'
  },
  {
    value: 'luxury',
    label: 'Luxury',
    description: 'Premium hotels, fine dining, private transport',
    icon: '✨'
  }
];

export default function BudgetSelector({ value, onChange, error }: BudgetSelectorProps) {
  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {BUDGET_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              value === option.value
                ? 'border-black bg-gray-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            aria-pressed={value === option.value}
            aria-label={`Select ${option.label} budget option`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl" role="img" aria-hidden="true">
                {option.icon}
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900">
                  {option.label}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {option.description}
                </p>
              </div>
            </div>
            
            {/* Selection indicator */}
            {value === option.value && (
              <div className="mt-3 flex items-center text-sm text-gray-700">
                <svg className="w-4 h-4 mr-1 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Selected
              </div>
            )}
          </button>
        ))}
      </div>
      
      {/* Error message */}
      {error && (
        <p className="mt-2 text-sm text-red-600" role="alert">{error}</p>
      )}
    </div>
  );
}