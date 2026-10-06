"""
Unit tests for currency conversion service.
Tests specific functionality without property-based testing to avoid import issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_currency_conversion_basic():
    """
    Basic unit test for currency conversion functionality.
    Tests that currency conversion works correctly for known values.
    """
    # Mock all external dependencies before importing
    with patch('backend.config.settings') as mock_settings, \
         patch('requests.Session') as mock_session_class:
        
        # Setup mock settings
        mock_settings.SERP_API_KEY = 'test-api-key'
        mock_settings.SERP_API_BASE_URL = 'https://serpapi.com'
        
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Import after mocking
        from backend.services.currency_service import CurrencyService
        
        # Create service instance
        currency_service = CurrencyService()
        
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
        assert '1K' in formatted, f"Should format thousands: {formatted}"
        
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
    """
    Test edge cases for currency conversion.
    """
    # Mock all external dependencies before importing
    with patch('backend.config.settings') as mock_settings, \
         patch('requests.Session') as mock_session_class:
        
        # Setup mock settings
        mock_settings.SERP_API_KEY = 'test-api-key'
        mock_settings.SERP_API_BASE_URL = 'https://serpapi.com'
        
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Import after mocking
        from backend.services.currency_service import CurrencyService
        
        # Create service instance
        currency_service = CurrencyService()
        
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


if __name__ == "__main__":
    test_currency_conversion_basic()
    test_currency_conversion_edge_cases()
    print("All currency conversion tests passed!")