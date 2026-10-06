import React from 'react';
import { useCurrency, Currency } from '../../contexts/CurrencyContext';

interface CurrencyToggleProps {
  className?: string;
}

const CurrencyToggle: React.FC<CurrencyToggleProps> = ({ 
  className = "flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1"
}) => {
  const { currency, setCurrency } = useCurrency();

  const currencies: Currency[] = ['INR', 'USD', 'EUR'];

  return (
    <div className={className}>
      {currencies.map((curr) => (
        <button
          key={curr}
          onClick={() => setCurrency(curr)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            currency === curr
              ? 'bg-blue-500 text-white shadow-sm'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
          aria-label={`Switch to ${curr}`}
          title={`Switch to ${curr}`}
        >
          {curr}
        </button>
      ))}
    </div>
  );
};

export default CurrencyToggle;