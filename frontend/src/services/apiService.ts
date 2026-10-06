/**
 * API Service for connecting frontend to backend
 * Handles all HTTP requests to the FastAPI backend with comprehensive error handling
 */

import { TripFormData } from '../types/trip';

const API_BASE_URL = 'http://localhost:8000';

// Types for API responses
interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
    email: string;
    created_at: string;
    updated_at: string;
  };
}

interface ValidationResponse {
  valid: boolean;
  message: string;
  errors?: string[];
}

interface PreferenceOptions {
  travel_types: string[];
  budget_levels: string[];
  interests: string[];
}

// Custom error classes
export class NetworkError extends Error {
  constructor(message: string = 'Network connection failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends Error {
  constructor(message: string, public errors?: string[]) {
    super(message);
    this.name = 'ValidationError';
  }
}

class ApiService {
  private static retryCount = 3;
  private static retryDelay = 1000; // 1 second

  private static getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  private static async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private static async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle specific HTTP status codes
      switch (response.status) {
        case 401:
          // Clear invalid token
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          throw new AuthenticationError(errorData.detail || 'Authentication required');
        case 422:
          throw new ValidationError(
            errorData.detail || 'Validation failed',
            Array.isArray(errorData.detail) ? errorData.detail.map((e: any) => e.msg) : undefined
          );
        case 500:
          throw new Error('Server error. Please try again later.');
        case 503:
          throw new Error('Service temporarily unavailable. Please try again later.');
        default:
          throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }
    }
    return response.json();
  }

  private static async fetchWithRetry<T>(
    url: string,
    options: RequestInit,
    retries: number = this.retryCount
  ): Promise<T> {
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          ...options,
          signal: AbortSignal.timeout(10000) // 10 second timeout
        });
        return await this.handleResponse<T>(response);
      } catch (error) {
        // Don't retry on authentication or validation errors
        if (error instanceof AuthenticationError || error instanceof ValidationError) {
          throw error;
        }

        // Check if it's a network error
        if (error instanceof TypeError || (error as any).name === 'NetworkError' || (error as any).name === 'TimeoutError') {
          if (attempt === retries) {
            throw new NetworkError('Unable to connect to the server. Please check your internet connection.');
          }
          
          // Wait before retrying
          await this.delay(this.retryDelay * (attempt + 1));
          continue;
        }

        // For other errors, don't retry
        throw error;
      }
    }
    
    throw new NetworkError('Maximum retry attempts exceeded');
  }

  // Authentication endpoints
  static async login(username: string, password: string): Promise<AuthResponse> {
    const data = await this.fetchWithRetry<AuthResponse>(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    // Store token in localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  }

  static async register(username: string, email: string, password: string): Promise<AuthResponse> {
    const data = await this.fetchWithRetry<AuthResponse>(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    
    // Store token in localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  }

  static async getCurrentUser(): Promise<AuthResponse['user']> {
    return this.fetchWithRetry<AuthResponse['user']>(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders()
    });
  }

  static async logout(): Promise<void> {
    try {
      await this.fetchWithRetry(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      }, 1); // Only retry once for logout
    } finally {
      // Always clear local storage regardless of API response
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  }

  // Trip preferences endpoints
  static async validateTripPreferences(tripData: TripFormData): Promise<ValidationResponse> {
    // Convert form data to API format
    const apiData = {
      destination: tripData.destination,
      start_date: tripData.startDate,
      end_date: tripData.endDate,
      travel_days: tripData.travelDays,
      travel_type: tripData.travelType,
      budget_preference: tripData.budgetPreference,
      max_budget_inr: parseFloat(tripData.maxBudgetInr.replace(/[₹,\s]/g, '')),
      interests: tripData.interests
    };

    return this.fetchWithRetry<ValidationResponse>(`${API_BASE_URL}/trip-preferences/validate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(apiData)
    });
  }

  static async validateDates(startDate: string, endDate: string): Promise<ValidationResponse> {
    return this.fetchWithRetry<ValidationResponse>(`${API_BASE_URL}/trip-preferences/validate-dates`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ start_date: startDate, end_date: endDate })
    });
  }

  static async validateBudget(maxBudgetInr: number, travelDays: number): Promise<ValidationResponse> {
    return this.fetchWithRetry<ValidationResponse>(`${API_BASE_URL}/trip-preferences/validate-budget`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ max_budget_inr: maxBudgetInr, travel_days: travelDays })
    });
  }

  static async getPreferenceOptions(): Promise<PreferenceOptions> {
    return this.fetchWithRetry<PreferenceOptions>(`${API_BASE_URL}/trip-preferences/options`, {
      headers: this.getAuthHeaders()
    });
  }

  // Trip planning endpoints
  static async createTripPlan(tripData: TripFormData): Promise<any> {
    // Convert form data to API format
    const apiData = {
      destination: tripData.destination,
      start_date: tripData.startDate,
      end_date: tripData.endDate,
      travel_days: tripData.travelDays,
      travel_type: tripData.travelType,
      budget_preference: tripData.budgetPreference,
      max_budget_inr: parseFloat(tripData.maxBudgetInr.replace(/[₹,\s]/g, '')),
      interests: tripData.interests
    };

    return this.fetchWithRetry(`${API_BASE_URL}/trip-planning/create`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(apiData)
    });
  }

  static async getSavedTrips(): Promise<any[]> {
    return this.fetchWithRetry(`${API_BASE_URL}/trip-planning/saved`, {
      headers: this.getAuthHeaders()
    });
  }

  static async getTripPlan(tripId: string): Promise<any> {
    return this.fetchWithRetry(`${API_BASE_URL}/trip-planning/${tripId}`, {
      headers: this.getAuthHeaders()
    });
  }
  static async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    return this.fetchWithRetry(`${API_BASE_URL}/health`, {}, 1); // Only retry once for health check
  }

  // Network status check
  static async checkNetworkStatus(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      return false;
    }
  }
}

export default ApiService;