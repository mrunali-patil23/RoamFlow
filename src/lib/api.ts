// API client configuration and utilities with type-safe methods
import {
  TripRequest,
  TripItinerary,
  FlightSearchParams,
  FlightOptions,
  TransportRequest,
  TransportOptions,
  APIResponse,
  ErrorResponse,
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public errorResponse?: ErrorResponse
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Request/Response interceptor types
export type RequestInterceptor = (config: RequestInit) => RequestInit | Promise<RequestInit>;
export type ResponseInterceptor = (response: Response) => Response | Promise<Response>;

// Loading state management
export interface LoadingManager {
  setLoading: (loading: boolean, message?: string) => void;
  isLoading: boolean;
}

export class ApiClient {
  private baseUrl: string;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private loadingManager?: LoadingManager;
  private defaultTimeout: number = 30000; // 30 seconds

  constructor(baseUrl: string = API_BASE_URL, loadingManager?: LoadingManager) {
    this.baseUrl = baseUrl;
    this.loadingManager = loadingManager;
  }

  // Interceptor management
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  // Loading state management
  setLoadingManager(manager: LoadingManager): void {
    this.loadingManager = manager;
  }

  private setLoading(loading: boolean, message?: string): void {
    if (this.loadingManager) {
      this.loadingManager.setLoading(loading, message);
    }
  }

  private async applyRequestInterceptors(config: RequestInit): Promise<RequestInit> {
    let finalConfig = config;
    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig);
    }
    return finalConfig;
  }

  private async applyResponseInterceptors(response: Response): Promise<Response> {
    let finalResponse = response;
    for (const interceptor of this.responseInterceptors) {
      finalResponse = await interceptor(finalResponse);
    }
    return finalResponse;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    // Apply response interceptors
    const processedResponse = await this.applyResponseInterceptors(response);
    
    if (!processedResponse.ok) {
      let errorResponse: ErrorResponse | undefined;
      
      try {
        errorResponse = await processedResponse.json();
      } catch {
        // If we can't parse the error response, create a generic one
        errorResponse = {
          success: false,
          error: true,
          message: `HTTP ${processedResponse.status}: ${processedResponse.statusText}`,
          error_code: 'HTTP_ERROR',
        };
      }

      throw new ApiError(
        errorResponse?.message || `HTTP error! status: ${processedResponse.status}`,
        processedResponse.status,
        errorResponse
      );
    }

    return processedResponse.json();
  }

  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {},
    loadingMessage?: string
  ): Promise<T> {
    this.setLoading(true, loadingMessage);
    
    try {
      // Create timeout controller
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);

      // Prepare request config
      const config: RequestInit = {
        ...options,
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          ...options.headers,
        },
      };

      // Apply request interceptors
      const finalConfig = await this.applyRequestInterceptors(config);

      // Make the request
      const response = await fetch(`${this.baseUrl}${endpoint}`, finalConfig);
      
      // Clear timeout
      clearTimeout(timeoutId);
      
      return await this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, {
          success: false,
          error: true,
          message: 'Request timed out',
          error_code: 'TIMEOUT_ERROR',
        });
      }
      throw error;
    } finally {
      this.setLoading(false);
    }
  }

  async get<T>(endpoint: string, loadingMessage?: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'GET',
    }, loadingMessage);
  }

  async post<T>(endpoint: string, data: any, loadingMessage?: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }, loadingMessage);
  }

  async put<T>(endpoint: string, data: any, loadingMessage?: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }, loadingMessage);
  }

  async delete<T>(endpoint: string, loadingMessage?: string): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'DELETE',
    }, loadingMessage);
  }

  // Type-safe API methods for specific endpoints

  /**
   * Plan a trip using AI based on user preferences
   */
  async planTrip(request: TripRequest): Promise<APIResponse<TripItinerary>> {
    return this.post<APIResponse<TripItinerary>>(
      '/api/v1/plan-trip', 
      request,
      'Planning your trip with AI...'
    );
  }

  /**
   * Search for flights based on search parameters
   */
  async searchFlights(params: FlightSearchParams): Promise<APIResponse<FlightOptions>> {
    const queryString = new URLSearchParams({
      origin: params.origin,
      destination: params.destination,
      departure_date: params.departure_date,
      passengers: params.passengers.toString(),
      ...(params.return_date && { return_date: params.return_date }),
    }).toString();

    return this.get<APIResponse<FlightOptions>>(
      `/api/v1/flights?${queryString}`,
      'Searching for flights...'
    );
  }

  /**
   * Get local transport options for a location
   */
  async getLocalTransport(request: TransportRequest): Promise<APIResponse<TransportOptions>> {
    const queryString = new URLSearchParams({
      location: request.location,
      ...(request.transport_type && { transport_type: request.transport_type }),
    }).toString();

    return this.get<APIResponse<TransportOptions>>(
      `/api/v1/local-transport?${queryString}`,
      'Loading transport options...'
    );
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<APIResponse<{ status: string }>> {
    return this.get<APIResponse<{ status: string }>>('/health', 'Checking server status...');
  }

  /**
   * Get trip by ID
   */
  async getTripById(tripId: string): Promise<APIResponse<TripItinerary>> {
    return this.get<APIResponse<TripItinerary>>(
      `/api/v1/trips/${tripId}`,
      'Loading trip details...'
    );
  }

  /**
   * Save trip to database
   */
  async saveTrip(itinerary: TripItinerary): Promise<APIResponse<{ trip_id: string }>> {
    return this.post(
      '/api/v1/trips',
      itinerary,
      'Saving your trip...'
    );
  }
}

// Create default API client instance
export const apiClient = new ApiClient();

// Add default request interceptor for logging
apiClient.addRequestInterceptor((config) => {
  if (process.env.NODE_ENV === 'development') {
    console.log('API Request:', config);
  }
  return config;
});

// Add default response interceptor for logging
apiClient.addResponseInterceptor((response) => {
  if (process.env.NODE_ENV === 'development') {
    console.log('API Response:', response.status, response.statusText);
  }
  return response;
});

// Utility functions for API error handling
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

export function getErrorCode(error: unknown): string | undefined {
  if (isApiError(error) && error.errorResponse) {
    return error.errorResponse.error_code;
  }
  return undefined;
}

export function isRetryableError(error: unknown): boolean {
  if (isApiError(error)) {
    // Retry on network errors, timeouts, and 5xx server errors
    return error.status >= 500 || error.status === 408 || error.status === 0;
  }
  return false;
}

export function getRetryAfter(error: unknown): number | undefined {
  if (isApiError(error) && error.errorResponse) {
    return error.errorResponse.retry_after;
  }
  return undefined;
}