/**
 * Integration tests for authentication flow
 * Tests complete user authentication journey
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import App from '../../App';
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

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Authentication Flow Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should complete full login flow successfully', async () => {
    // Mock successful login response
    const mockUser = {
      id: 'user-123',
      username: 'testuser',
      email: 'test@example.com',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };

    mockApiService.login.mockResolvedValue({
      access_token: 'mock-token',
      token_type: 'bearer',
      user: mockUser
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show login form initially (no token in localStorage)
    expect(screen.getByText('Sign In')).toBeInTheDocument();

    // Fill in login form
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    // Wait for login to complete
    await waitFor(() => {
      expect(mockApiService.login).toHaveBeenCalledWith('testuser', 'password123');
    });

    // Should store token and user data
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', 'mock-token');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser));

    // Should redirect to main app
    await waitFor(() => {
      expect(screen.getByText('Welcome to AI Trip Planner')).toBeInTheDocument();
      expect(screen.getByText('Welcome, testuser!')).toBeInTheDocument();
    });
  });

  it('should handle login failure gracefully', async () => {
    // Mock failed login response
    mockApiService.login.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Fill in login form with invalid credentials
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const loginButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(loginButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    // Should not store any data
    expect(mockLocalStorage.setItem).not.toHaveBeenCalled();

    // Should remain on login page
    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('should complete full registration flow successfully', async () => {
    // Mock successful registration response
    const mockUser = {
      id: 'user-456',
      username: 'newuser',
      email: 'new@example.com',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };

    mockApiService.register.mockResolvedValue({
      access_token: 'new-token',
      token_type: 'bearer',
      user: mockUser
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Switch to registration form
    const switchToRegisterButton = screen.getByText(/don't have an account/i);
    fireEvent.click(switchToRegisterButton);

    // Should show registration form
    expect(screen.getByText('Create Account')).toBeInTheDocument();

    // Fill in registration form
    const usernameInput = screen.getByLabelText(/username/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const registerButton = screen.getByRole('button', { name: /create account/i });

    fireEvent.change(usernameInput, { target: { value: 'newuser' } });
    fireEvent.change(emailInput, { target: { value: 'new@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'newpassword123' } });
    fireEvent.click(registerButton);

    // Wait for registration to complete
    await waitFor(() => {
      expect(mockApiService.register).toHaveBeenCalledWith('newuser', 'new@example.com', 'newpassword123');
    });

    // Should store token and user data
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', 'new-token');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser));

    // Should redirect to main app
    await waitFor(() => {
      expect(screen.getByText('Welcome to AI Trip Planner')).toBeInTheDocument();
      expect(screen.getByText('Welcome, newuser!')).toBeInTheDocument();
    });
  });

  it('should handle logout flow correctly', async () => {
    // Mock authenticated state
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

    mockApiService.logout.mockResolvedValue();

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show authenticated state
    await waitFor(() => {
      expect(screen.getByText('Welcome, testuser!')).toBeInTheDocument();
    });

    // Click logout button
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(logoutButton);

    // Should call logout API
    await waitFor(() => {
      expect(mockApiService.logout).toHaveBeenCalled();
    });

    // Should clear localStorage
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('access_token');
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user');

    // Should redirect to login page
    await waitFor(() => {
      expect(screen.getByText('Sign In')).toBeInTheDocument();
    });
  });

  it('should handle authentication persistence on page reload', async () => {
    // Mock authenticated state in localStorage
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

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should automatically show authenticated state
    await waitFor(() => {
      expect(screen.getByText('Welcome, testuser!')).toBeInTheDocument();
      expect(screen.getByText('Welcome to AI Trip Planner')).toBeInTheDocument();
    });

    // Should not show login form
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
  });
});