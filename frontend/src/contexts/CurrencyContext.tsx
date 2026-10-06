import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Currency = 'INR' | 'USD' | 'EUR';

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
  convertFromINR: (amountInr: number) => number;
  formatCurrency: (amount: number) => string;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

// Exchange rates (in practice, these would come from an API)
const EXCHANGE_RATES = {
  INR: 1,
  USD: 0.012, // 1 INR = 0.012 USD (approximate)
  EUR: 0.011, // 1 INR = 0.011 EUR (approximate)
};

const CURRENCY_SYMBOLS = {
  INR: '₹',
  USD: '$',
  EUR: '€',
};

interface CurrencyProviderProps {
  children: ReactNode;
}

export const CurrencyProvider: React.FC<CurrencyProviderProps> = ({ children }) => {
  const [currency, setCurrency] = useState<Currency>('INR');

  const convertFromINR = (amountInr: number): number => {
    return amountInr * EXCHANGE_RATES[currency];
  };

  const formatCurrency = (amount: number): string => {
    const convertedAmount = convertFromINR(amount);
    const symbol = CURRENCY_SYMBOLS[currency];
    
    // Format based on currency
    switch (currency) {
      case 'INR':
        return `${symbol}${convertedAmount.toLocaleString('en-IN')}`;
      case 'USD':
        return `${symbol}${convertedAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      case 'EUR':
        return `${symbol}${convertedAmount.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      default:
        return `${symbol}${convertedAmount.toFixed(2)}`;
    }
  };

  return (
    <CurrencyContext.Provider value={{ currency, setCurrency, convertFromINR, formatCurrency }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = (): CurrencyContextType => {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};