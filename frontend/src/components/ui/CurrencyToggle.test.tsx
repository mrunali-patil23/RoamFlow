import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import CurrencyToggle from './CurrencyToggle';
import { CurrencyProvider, useCurrency, Currency } from '../../contexts/CurrencyContext';

// Test component to display currency values
const CurrencyDisplay: React.FC<{ amount: number }> = ({ amount }) => {
  const { formatCurrency } = useCurrency();
  return <div data-testid="currency-display">{formatCurrency(amount)}</div>;
};

const CurrencyToggleWrapper: React.FC<{ amount?: number }> = ({ amount = 1000 }) => (
  <CurrencyProvider>
    <CurrencyToggle />
    <CurrencyDisplay amount={amount} />
  </CurrencyProvider>
);

describe('CurrencyToggle Property Tests', () => {
  // Feature: ai-trip-planner, Property 28: Currency Toggle Functionality
  it('should consistently toggle between currencies and update displayed amounts', () => {
    fc.assert(
      fc.property(
        fc.array(fc.constantFrom('INR', 'USD', 'EUR'), { minLength: 1, maxLength: 10 }),
        fc.integer({ min: 100, max: 100000 }),
        (currencySequence, amount) => {
          const { container, getByTestId, unmount } = render(<CurrencyToggleWrapper amount={amount} />);
          
          try {
            // Get all currency buttons
            const inrButton = container.querySelector('button[aria-label="Switch to INR"]');
            const usdButton = container.querySelector('button[aria-label="Switch to USD"]');
            const eurButton = container.querySelector('button[aria-label="Switch to EUR"]');
            
            expect(inrButton).toBeTruthy();
            expect(usdButton).toBeTruthy();
            expect(eurButton).toBeTruthy();
            
            const buttons = { INR: inrButton!, USD: usdButton!, EUR: eurButton! };
            
            // Test each currency in the sequence
            currencySequence.forEach((targetCurrency) => {
              // Click the target currency button
              fireEvent.click(buttons[targetCurrency]);
              
              // Verify the button is now active (has blue background)
              expect(buttons[targetCurrency].classList.contains('bg-blue-500')).toBe(true);
              expect(buttons[targetCurrency].classList.contains('text-white')).toBe(true);
              
              // Verify other buttons are not active
              Object.entries(buttons).forEach(([curr, button]) => {
                if (curr !== targetCurrency) {
                  expect(button.classList.contains('bg-blue-500')).toBe(false);
                  expect(button.classList.contains('text-white')).toBe(false);
                }
              });
              
              // Verify the currency display is updated
              const currencyDisplay = getByTestId('currency-display');
              const displayText = currencyDisplay.textContent || '';
              
              // Check that the display contains the correct currency symbol
              switch (targetCurrency) {
                case 'INR':
                  expect(displayText.startsWith('₹')).toBe(true);
                  break;
                case 'USD':
                  expect(displayText.startsWith('$')).toBe(true);
                  break;
                case 'EUR':
                  expect(displayText.startsWith('€')).toBe(true);
                  break;
              }
              
              // Verify the amount is properly formatted (contains numbers)
              expect(/\d/.test(displayText)).toBe(true);
            });
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should maintain correct exchange rate relationships between currencies', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1000, max: 50000 }),
        (amountInr) => {
          const { container, getByTestId, unmount } = render(<CurrencyToggleWrapper amount={amountInr} />);
          
          try {
            const inrButton = container.querySelector('button[aria-label="Switch to INR"]');
            const usdButton = container.querySelector('button[aria-label="Switch to USD"]');
            const eurButton = container.querySelector('button[aria-label="Switch to EUR"]');
            
            // Get INR amount (baseline)
            fireEvent.click(inrButton!);
            const inrDisplay = getByTestId('currency-display').textContent || '';
            const inrAmount = parseFloat(inrDisplay.replace(/[₹,]/g, ''));
            
            // Get USD amount
            fireEvent.click(usdButton!);
            const usdDisplay = getByTestId('currency-display').textContent || '';
            const usdAmount = parseFloat(usdDisplay.replace(/[$,]/g, ''));
            
            // Get EUR amount
            fireEvent.click(eurButton!);
            const eurDisplay = getByTestId('currency-display').textContent || '';
            // Handle both comma and period as decimal separators
            const eurAmount = parseFloat(eurDisplay.replace(/[€]/g, '').replace(',', '.').replace(/\s/g, ''));
            
            // Verify exchange rate relationships
            // USD should be much smaller than INR (approximately 1/80)
            expect(usdAmount).toBeLessThan(inrAmount);
            expect(usdAmount).toBeGreaterThan(0);
            
            // EUR should be much smaller than INR (approximately 1/90)  
            expect(eurAmount).toBeLessThan(inrAmount);
            expect(eurAmount).toBeGreaterThan(0);
            
            // USD and EUR should be relatively close to each other
            if (usdAmount > 0 && eurAmount > 0) {
              const ratio = Math.max(usdAmount, eurAmount) / Math.min(usdAmount, eurAmount);
              expect(ratio).toBeLessThan(2); // Should not differ by more than 2x
            }
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should format currency amounts correctly for each currency', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1000000 }),
        fc.constantFrom('INR', 'USD', 'EUR'),
        (amount, targetCurrency) => {
          const { container, getByTestId, unmount } = render(<CurrencyToggleWrapper amount={amount} />);
          
          try {
            const button = container.querySelector(`button[aria-label="Switch to ${targetCurrency}"]`);
            fireEvent.click(button!);
            
            const currencyDisplay = getByTestId('currency-display');
            const displayText = currencyDisplay.textContent || '';
            
            // Verify currency symbol is present
            switch (targetCurrency) {
              case 'INR':
                expect(displayText.startsWith('₹')).toBe(true);
                // INR should use Indian number formatting (with commas)
                if (amount >= 1000) {
                  expect(displayText.includes(',')).toBe(true);
                }
                break;
              case 'USD':
                expect(displayText.startsWith('$')).toBe(true);
                // USD should show decimal places
                expect(displayText.includes('.')).toBe(true);
                break;
              case 'EUR':
                expect(displayText.startsWith('€')).toBe(true);
                // EUR should show decimal places (German locale uses comma)
                expect(displayText.includes(',') || displayText.includes('.')).toBe(true);
                break;
            }
            
            // Verify the display contains numbers
            expect(/\d/.test(displayText)).toBe(true);
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});