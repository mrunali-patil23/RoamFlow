/**
 * Integration tests for trip planning flow
 * Tests complete trip planning user journey
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import TripPlannerPage from '../../pages/TripPlannerPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { CurrencyProvider } from '../../contexts/CurrencyContext';
import ApiService from '../../services/apiService';

// Mock API Service
vi.mock('../../services/apiService');
const mockApiService = vi.mocked(ApiService);

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Test wrapper component with all providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider>
      <CurrencyProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </CurrencyProvider>
    </ThemeProvider>
  </BrowserRouter>
);

describe('Trip Planning Flow Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock authenticated user
    const mockUser = {
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };

    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'mock-token';
      if (key === 'user') return JSON.stringify(mockUser);
      return null;
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should complete full trip planning flow successfully', async () => {
    // Mock successful validation response
    mockApiService.validateTripPreferences.mockResolvedValue({
      valid: true,
      message: 'Trip preferences are valid'
    });

    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    // Should show trip input form
    expect(screen.getByText('Plan Your Perfect Trip')).toBeInTheDocument();

    // Fill in trip form
    const destinationInput = screen.getByLabelText(/destination/i);
    const startDateInput = screen.getByLabelText(/start date/i);
    const endDateInput = screen.getByLabelText(/end date/i);
    const budgetInput = screen.getByLabelText(/maximum budget/i);

    fireEvent.change(destinationInput, { target: { value: 'Paris, France' } });
    fireEvent.change(startDateInput, { target: { value: '2024-06-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-06-07' } });
    fireEvent.change(budgetInput, { target: { value: '100000' } });

    // Select travel type
    const soloOption = screen.getByLabelText(/solo/i);
    fireEvent.click(soloOption);

    // Select budget preference
    const mediumBudgetOption = screen.getByLabelText(/medium/i);
    fireEvent.click(mediumBudgetOption);

    // Select interests
    const cultureInterest = screen.getByLabelText(/culture/i);
    const foodInterest = screen.getByLabelText(/food/i);
    fireEvent.click(cultureInterest);
    fireEvent.click(foodInterest);

    // Submit form
    const submitButton = screen.getByRole('button', { name: /create trip plan/i });
    fireEvent.click(submitButton);

    // Should show loading state
    expect(screen.getByText(/creating your trip plan/i)).toBeInTheDocument();

    // Wait for validation to complete
    await waitFor(() => {
      expect(mockApiService.validateTripPreferences).toHaveBeenCalledWith({
        destination: 'Paris, France',
        startDate: '2024-06-01',
        endDate: '2024-06-07',
        travelDays: 6,
        travelType: 'Solo',
        budgetPreference: 'medium',
        maxBudgetInr: '₹1,00,000',
        interests: ['culture', 'food']
      });
    });

    // Should show success message (placeholder)
    await waitFor(() => {
      expect(screen.getByText(/trip plan created successfully/i)).toBeInTheDocument();
    });
  });

  it('should handle validation errors gracefully', async () => {
    // Mock validation error response
    mockApiService.validateTripPreferences.mockResolvedValue({
      valid: false,
      message: 'Validation failed',
      errors: ['Start date must be in the future', 'Budget is too low']
    });

    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    // Fill in form with invalid data
    const destinationInput = screen.getByLabelText(/destination/i);
    const startDateInput = screen.getByLabelText(/start date/i);
    const endDateInput = screen.getByLabelText(/end date/i);
    const budgetInput = screen.getByLabelText(/maximum budget/i);

    fireEvent.change(destinationInput, { target: { value: 'Tokyo, Japan' } });
    fireEvent.change(startDateInput, { target: { value: '2023-01-01' } }); // Past date
    fireEvent.change(endDateInput, { target: { value: '2023-01-07' } });
    fireEvent.change(budgetInput, { target: { value: '1000' } }); // Low budget

    // Select required fields
    const soloOption = screen.getByLabelText(/solo/i);
    fireEvent.click(soloOption);

    const mediumBudgetOption = screen.getByLabelText(/medium/i);
    fireEvent.click(mediumBudgetOption);

    const cultureInterest = screen.getByLabelText(/culture/i);
    fireEvent.click(cultureInterest);

    // Submit form
    const submitButton = screen.getByRole('button', { name: /create trip plan/i });
    fireEvent.click(submitButton);

    // Wait for validation to complete
    await waitFor(() => {
      expect(mockApiService.validateTripPreferences).toHaveBeenCalled();
    });

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/start date must be in the future, budget is too low/i)).toBeInTheDocument();
    });

    // Should not show success message
    expect(screen.queryByText(/trip plan created successfully/i)).not.toBeInTheDocument();
  });

  it('should handle network errors with retry functionality', async () => {
    // Mock network error
    const networkError = new Error('Network connection failed');
    networkError.name = 'NetworkError';
    mockApiService.validateTripPreferences.mockRejectedValue(networkError);

    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    // Fill in valid form data
    const destinationInput = screen.getByLabelText(/destination/i);
    const startDateInput = screen.getByLabelText(/start date/i);
    const endDateInput = screen.getByLabelText(/end date/i);
    const budgetInput = screen.getByLabelText(/maximum budget/i);

    fireEvent.change(destinationInput, { target: { value: 'London, UK' } });
    fireEvent.change(startDateInput, { target: { value: '2024-08-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-08-07' } });
    fireEvent.change(budgetInput, { target: { value: '150000' } });

    // Select required fields
    const soloOption = screen.getByLabelText(/solo/i);
    fireEvent.click(soloOption);

    const mediumBudgetOption = screen.getByLabelText(/medium/i);
    fireEvent.click(mediumBudgetOption);

    const cultureInterest = screen.getByLabelText(/culture/i);
    fireEvent.click(cultureInterest);

    // Submit form
    const submitButton = screen.getByRole('button', { name: /create trip plan/i });
    fireEvent.click(submitButton);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/unable to connect to server/i)).toBeInTheDocument();
    });

    // Should show network status component
    expect(screen.getByText(/server connection issues/i)).toBeInTheDocument();

    // Should show retry button
    expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
  });

  it('should validate form fields before submission', async () => {
    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    // Try to submit empty form
    const submitButton = screen.getByRole('button', { name: /create trip plan/i });
    fireEvent.click(submitButton);

    // Should show validation errors for required fields
    await waitFor(() => {
      expect(screen.getByText(/destination is required/i)).toBeInTheDocument();
      expect(screen.getByText(/start date is required/i)).toBeInTheDocument();
      expect(screen.getByText(/end date is required/i)).toBeInTheDocument();
      expect(screen.getByText(/maximum budget is required/i)).toBeInTheDocument();
      expect(screen.getByText(/please select at least one interest/i)).toBeInTheDocument();
    });

    // Should not call API
    expect(mockApiService.validateTripPreferences).not.toHaveBeenCalled();
  });

  it('should auto-calculate travel days from dates', async () => {
    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    // Set start and end dates
    const startDateInput = screen.getByLabelText(/start date/i);
    const endDateInput = screen.getByLabelText(/end date/i);
    const travelDaysInput = screen.getByLabelText(/number of travel days/i);

    fireEvent.change(startDateInput, { target: { value: '2024-06-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-06-10' } });

    // Should auto-calculate travel days
    await waitFor(() => {
      expect(travelDaysInput).toHaveValue(9);
    });
  });

  it('should format budget input with Indian currency', async () => {
    render(
      <TestWrapper>
        <TripPlannerPage />
      </TestWrapper>
    );

    const budgetInput = screen.getByLabelText(/maximum budget/i);

    // Type numeric value
    fireEvent.change(budgetInput, { target: { value: '50000' } });

    // Should format with Indian currency
    await waitFor(() => {
      expect(budgetInput).toHaveValue('₹50,000');
    });
  });
});