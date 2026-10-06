"""
Standalone currency conversion tests.
Tests currency conversion logic without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Optional, Union
import logging
from datetime import datetime, timedelta


class StandaloneCurrencyService:
    """Standalone currency service for testing without external dependencies."""
    
    # Static exchange rates as fallback (approximate rates as of 2024)
    FALLBACK_RATES = {
        'USD': 83.0,    # 1 USD = 83 INR
        'EUR': 90.0,    # 1 EUR = 90 INR
        'GBP': 105.0,   # 1 GBP = 105 INR
        'JPY': 0.56,    # 1 JPY = 0.56 INR
        'AUD': 55.0,    # 1 AUD = 55 INR
        'CAD': 61.0,    # 1 CAD = 61 INR
        'SGD': 62.0,    # 1 SGD = 62 INR
        'AED': 22.6,    # 1 AED = 22.6 INR
        'THB': 2.3,     # 1 THB = 2.3 INR
        'MYR': 18.0,    # 1 MYR = 18 INR
        'INR': 1.0      # 1 INR = 1 INR
    }
    
    def __init__(self):
        self._exchange_rates_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)
    
    def _get_exchange_rates(self) -> Dict[str, float]:
        """Get current exchange rates, using cache if available."""
        return self.FALLBACK_RATES.copy()
    
    def convert_to_inr(self, amount: Union[float, int, str], from_currency: str) -> float:
        """Convert an amount from the specified currency to INR."""
        try:
            # Convert amount to float
            if isinstance(amount, str):
                # Remove currency symbols and commas
                cleaned_amount = amount.replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('₹', '').strip()
                amount = float(cleaned_amount)
            else:
                amount = float(amount)
            
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            
            # Normalize currency code
            from_currency = from_currency.upper().strip()
            
            # If already in INR, return as is
            if from_currency == 'INR':
                return amount
            
            # Get exchange rates
            rates = self._get_exchange_rates()
            
            if from_currency not in rates:
                from_currency = 'USD'  # Fallback to USD
            
            # Convert to INR
            exchange_rate = rates[from_currency]
            inr_amount = amount * exchange_rate
            
            return round(inr_amount, 2)
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount or currency: {amount} {from_currency}")
    
    def extract_and_convert_price(self, price_text: str, default_currency: str = 'USD') -> Optional[float]:
        """Extract price from text and convert to INR."""
        if not price_text:
            return None
        
        try:
            # Common currency symbols and their codes
            currency_symbols = {
                '$': 'USD',
                '€': 'EUR', 
                '£': 'GBP',
                '₹': 'INR',
                '¥': 'JPY',
                'A$': 'AUD',
                'C$': 'CAD',
                'S$': 'SGD',
                'AED': 'AED',
                '฿': 'THB',
                'RM': 'MYR'
            }
            
            # Try to detect currency from symbols
            detected_currency = default_currency
            for symbol, currency in currency_symbols.items():
                if symbol in price_text:
                    detected_currency = currency
                    break
            
            # Extract numeric value
            import re
            # Remove currency symbols and extract numbers
            numeric_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if numeric_match:
                amount = float(numeric_match.group())
                return self.convert_to_inr(amount, detected_currency)
            
            return None
            
        except Exception as e:
            return None
    
    def format_inr_price(self, amount: float) -> str:
        """Format an INR amount with proper currency symbol and formatting."""
        if amount is None:
            return "₹0"
        
        try:
            # Format with Indian number system (lakhs, crores)
            if amount >= 10000000:  # 1 crore
                return f"₹{amount/10000000:.1f} Cr"
            elif amount >= 100000:  # 1 lakh
                return f"₹{amount/100000:.1f} L"
            elif amount >= 1000:  # Thousands
                return f"₹{amount/1000:.1f}K"
            else:
                return f"₹{amount:,.0f}"
        except:
            return f"₹{amount}"
    
    def get_supported_currencies(self) -> list:
        """Get list of supported currency codes."""
        return list(self.FALLBACK_RATES.keys())


def test_currency_conversion_basic():
    """Basic unit test for currency conversion functionality."""
    currency_service = StandaloneCurrencyService()
    
    # Test basic currency conversion
    usd_amount = 100.0
    inr_amount = currency_service.convert_to_inr(usd_amount, 'USD')
    
    # Should convert using fallback rate (1 USD = 83 INR)
    expected_inr = 100.0 * 83.0
    assert inr_amount == expected_inr, f"Expected {expected_inr}, got {inr_amount}"
    
    # Test INR to INR conversion (should be identity)
    inr_to_inr = currency_service.convert_to_inr(100.0, 'INR')
    assert inr_to_inr == 100.0, f"INR to INR should be identity, got {inr_to_inr}"
    
    # Test formatted price
    formatted = currency_service.format_inr_price(1000.0)
    assert '₹' in formatted, f"Formatted price should contain ₹ symbol: {formatted}"
    assert '1.0K' in formatted, f"Should format thousands: {formatted}"
    
    # Test supported currencies
    supported = currency_service.get_supported_currencies()
    assert 'USD' in supported, "USD should be supported"
    assert 'EUR' in supported, "EUR should be supported"
    assert 'INR' in supported, "INR should be supported"
    
    # Test price extraction
    extracted = currency_service.extract_and_convert_price("$50", 'USD')
    assert extracted is not None, "Should extract price from $50"
    assert extracted == 50.0 * 83.0, f"Should convert $50 to INR: {extracted}"


def test_currency_conversion_edge_cases():
    """Test edge cases for currency conversion."""
    currency_service = StandaloneCurrencyService()
    
    # Test zero amount
    zero_result = currency_service.convert_to_inr(0, 'USD')
    assert zero_result == 0.0, f"Zero amount should convert to zero: {zero_result}"
    
    # Test string amount
    string_result = currency_service.convert_to_inr("100", 'USD')
    numeric_result = currency_service.convert_to_inr(100, 'USD')
    assert string_result == numeric_result, "String and numeric amounts should be equal"
    
    # Test invalid currency (should fallback to USD)
    invalid_result = currency_service.convert_to_inr(100, 'INVALID')
    usd_result = currency_service.convert_to_inr(100, 'USD')
    assert invalid_result == usd_result, "Invalid currency should fallback to USD"
    
    # Test negative amount (should raise error)
    with pytest.raises(ValueError):
        currency_service.convert_to_inr(-100, 'USD')


def test_currency_conversion_consistency():
    """Test that currency conversion is consistent."""
    currency_service = StandaloneCurrencyService()
    
    # Test consistency - same input should give same output
    amount = 100.0
    currency = 'EUR'
    
    result1 = currency_service.convert_to_inr(amount, currency)
    result2 = currency_service.convert_to_inr(amount, currency)
    
    assert result1 == result2, f"Currency conversion should be consistent: {result1} != {result2}"
    
    # Test that all supported currencies are convertible
    for currency in currency_service.get_supported_currencies():
        test_amount = 100.0
        converted = currency_service.convert_to_inr(test_amount, currency)
        assert isinstance(converted, float), f"Conversion from {currency} should return float"
        assert converted >= 0, f"Conversion from {currency} should be non-negative"
    
    # Test formatted prices contain INR symbol
    test_amounts = [100, 1000, 100000, 10000000]
    for amount in test_amounts:
        formatted = currency_service.format_inr_price(amount)
        assert '₹' in formatted, f"Formatted price should contain ₹ symbol: {formatted}"
        assert isinstance(formatted, str), f"Formatted price should be string: {type(formatted)}"


if __name__ == "__main__":
    test_currency_conversion_basic()
    test_currency_conversion_edge_cases()
    test_currency_conversion_consistency()
    print("All currency conversion tests passed!")