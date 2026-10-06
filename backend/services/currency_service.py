"""
Currency conversion service for converting various currencies to INR.
"""

import requests
from typing import Dict, Optional, Union
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class CurrencyService:
    """Service for currency conversion to INR."""
    
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
        self.session = requests.Session()
        self._exchange_rates_cache = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)
    
    def convert_to_inr(self, amount: Union[float, int, str], from_currency: str) -> float:
        """Convert an amount from the specified currency to INR."""
        try:
            # Convert amount to float
            if isinstance(amount, str):
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
            rates = self.FALLBACK_RATES.copy()
            
            if from_currency not in rates:
                logger.warning(f"Unsupported currency: {from_currency}. Using USD as fallback.")
                from_currency = 'USD'
            
            # Convert to INR
            exchange_rate = rates[from_currency]
            inr_amount = amount * exchange_rate
            
            return round(inr_amount, 2)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Currency conversion error: {e}")
            raise ValueError(f"Invalid amount or currency: {amount} {from_currency}")
    
    def format_inr_price(self, amount: float) -> str:
        """Format an INR amount with proper currency symbol and formatting."""
        if amount is None:
            return "₹0"
        
        try:
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
            numeric_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if numeric_match:
                amount = float(numeric_match.group())
                return self.convert_to_inr(amount, detected_currency)
            
            return None
            
        except Exception as e:
            logger.error(f"Price extraction error: {e}")
            return None