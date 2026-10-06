/**
 * Integration tests for offline functionality
 * Tests offline mode detection and fallback behavior
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import App from '../../App';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';
import ApiService from '../../services/apiService';

// Mock API Service
vi.mock('../../services/apiService');
const mockApiService = vi.mocked(ApiService);

// Mock network status hook
vi.mock('../../hooks/useNetworkStatus');
const mockUseNetworkStatus = vi.mocked(useNetworkStatus);

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Mock navigator.onLine
Object.defineProperty(navigator, 'onLine', {
  writable: true,
  value: true,
});

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Offline Functionality Integration Tests', () => {
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

    // Default online state
    mockUseNetworkStatus.mockReturnValue({
      isOnline: true,
      isApiConnected: true,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should detect when user goes offline', async () => {
    // Start with online state
    mockUseNetworkStatus.mockReturnValue({
      isOnline: true,
      isApiConnected: true,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });

    const { rerender } = render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should not show offline indicator initially
    expect(screen.queryByText(/offline/i)).not.toBeInTheDocument();

    // Simulate going offline
    mockUseNetworkStatus.mockReturnValue({
      isOnline: false,
      isApiConnected: false,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });

    rerender(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show offline indicator
    await waitFor(() => {
      expect(screen.getByText(/offline/i)).toBeInTheDocument();
    });
  });

  it('should detect API connection issues while online', async () => {
    // Simulate online but API disconnected
    mockUseNetworkStatus.mockReturnValue({
      isOnline: true,
      isApiConnected: false,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show connection issues indicator
    await waitFor(() => {
      expect(screen.getByText(/connection issues/i)).toBeInTheDocument();
    });
  });

  it('should provide retry functionality when connection fails', async () => {
    const mockCheckConnection = vi.fn();
    
    // Simulate connection issues
    mockUseNetworkStatus.mockReturnValue({
      isOnline: true,
      isApiConnected: false,
      lastChecked: new Date(),
      checkConnection: mockCheckConnection
    });

    // Mock API failure then success
    mockApiService.validateTripPreferences
      .mockRejectedValueOnce(new Error('Network connection failed'))
      .mockResolvedValueOnce({
        valid: true,
        message: 'Trip preferences are valid'
      });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Navigate to trip planner and try to submit
    await waitFor(() => {
      expect(screen.getByText('Plan Your Perfect Trip')).toBeInTheDocument();
    });

    // Fill in minimal form data
    const destinationInput = screen.getByLabelText(/destination/i);
    const startDateInput = screen.getByLabelText(/start date/i);
    const endDateInput = screen.getByLabelText(/end date/i);
    const budgetInput = screen.getByLabelText(/maximum budget/i);

    fireEvent.change(destinationInput, { target: { value: 'Paris, France' } });
    fireEvent.change(startDateInput, { target: { value: '2024-06-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-06-07' } });
    fireEvent.change(budgetInput, { target: { value: '100000' } });

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

    // Should show network error and retry option
    await waitFor(() => {
      expect(screen.getByText(/unable to connect to server/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
    });

    // Click retry button
    const retryButton = screen.getByRole('button', { name: /retry connection/i });
    fireEvent.click(retryButton);

    // Should call checkConnection
    expect(mockCheckConnection).toHaveBeenCalled();
  });

  it('should handle offline data availability', async () => {
    // Mock offline cache service
    const mockCachedData = {
      tripId: 'cached-trip-123',
      destination: 'Paris, France',
      itinerary: {
        days: [
          {
            dayNumber: 1,
            date: '2024-06-01',
            activities: [
              {
                name: 'Visit Eiffel Tower',
                activityType: 'attraction',
                description: 'Iconic landmark',
                durationHours: 2,
                costInr: 2000,
                bookingRequired: false
              }
            ],
            weather: {
              date: '2024-06-01',
              condition: 'Sunny',
              description: 'Clear skies'
            },
            dailyCostInr: 5000
          }
        ],
        totalCostInr: 50000
      }
    };

    // Mock localStorage to return cached data
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'mock-token';
      if (key === 'user') return JSON.stringify({
        id: 'user-123',
        username: 'testuser',
        email: 'test@example.com',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      });
      if (key === 'lastGeneratedItinerary') return JSON.stringify(mockCachedData);
      return null;
    });

    // Simulate offline state
    mockUseNetworkStatus.mockReturnValue({
      isOnline: false,
      isApiConnected: false,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show offline indicator
    await waitFor(() => {
      expect(screen.getByText(/offline/i)).toBeInTheDocument();
    });

    // Should still be able to access the app
    expect(screen.getByText('Welcome to AI Trip Planner')).toBeInTheDocument();
    expect(screen.getByText('Welcome, testuser!')).toBeInTheDocument();
  });

  it('should show appropriate messages for different connection states', async () => {
    const scenarios = [
      {
        state: { isOnline: false, isApiConnected: false },
        expectedMessage: /no internet connection/i
      },
      {
        state: { isOnline: true, isApiConnected: false },
        expectedMessage: /server connection issues/i
      },
      {
        state: { isOnline: true, isApiConnected: true },
        expectedMessage: null // No message when everything is working
      }
    ];

    for (const scenario of scenarios) {
      mockUseNetworkStatus.mockReturnValue({
        ...scenario.state,
        lastChecked: new Date(),
        checkConnection: vi.fn()
      });

      const { unmount } = render(
        <TestWrapper>
          <App />
        </TestWrapper>
      );

      if (scenario.expectedMessage) {
        await waitFor(() => {
          expect(screen.getByText(scenario.expectedMessage)).toBeInTheDocument();
        });
      } else {
        // Should not show any connection-related messages
        expect(screen.queryByText(/offline/i)).not.toBeInTheDocument();
        expect(screen.queryByText(/connection issues/i)).not.toBeInTheDocument();
      }

      unmount();
    }
  });

  it('should handle authentication errors when offline', async () => {
    // Simulate offline state
    mockUseNetworkStatus.mockReturnValue({
      isOnline: false,
      isApiConnected: false,
      lastChecked: new Date(),
      checkConnection: vi.fn()
    });

    // Mock no stored authentication
    mockLocalStorage.getItem.mockReturnValue(null);

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show login form
    expect(screen.getByText('Sign In')).toBeInTheDocument();

    // Should show offline indicator
    expect(screen.getByText(/offline/i)).toBeInTheDocument();

    // Try to login while offline
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    // Should show network error
    await waitFor(() => {
      expect(screen.getByText(/unable to connect to server/i)).toBeInTheDocument();
    });
  });
});