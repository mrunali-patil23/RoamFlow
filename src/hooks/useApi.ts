import { useState, useCallback } from 'react';
import { apiClient, ApiError, isApiError, getErrorMessage } from '@/lib/api';
import { LoadingManager } from '@/lib/api';

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  loadingMessage?: string;
}

export interface UseApiActions<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
  setData: (data: T | null) => void;
  setError: (error: string | null) => void;
}

export type UseApiReturn<T> = UseApiState<T> & UseApiActions<T>;

/**
 * Custom hook for managing API calls with loading states and error handling
 */
export function useApi<T = any>(): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
    loadingMessage: undefined,
  });

  // Create loading manager for the API client
  const loadingManager: LoadingManager = {
    setLoading: (loading: boolean, message?: string) => {
      setState(prev => ({
        ...prev,
        loading,
        loadingMessage: message,
        error: loading ? null : prev.error, // Clear error when starting new request
      }));
    },
    isLoading: state.loading,
  };

  // Set the loading manager on the API client
  apiClient.setLoadingManager(loadingManager);

  const execute = useCallback(async (apiCall: () => Promise<T>): Promise<T | null> => {
    try {
      setState(prev => ({ ...prev, error: null }));
      const result = await apiCall();
      setState(prev => ({ ...prev, data: result }));
      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setState(prev => ({ ...prev, error: errorMessage, data: null }));
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      loadingMessage: undefined,
    });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState(prev => ({ ...prev, data }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    setData,
    setError,
  };
}

/**
 * Specialized hook for trip planning API calls
 */
export function useTripApi() {
  const api = useApi();

  const planTrip = useCallback(async (request: any) => {
    return api.execute(() => apiClient.planTrip(request));
  }, [api]);

  const searchFlights = useCallback(async (params: any) => {
    return api.execute(() => apiClient.searchFlights(params));
  }, [api]);

  const getLocalTransport = useCallback(async (request: any) => {
    return api.execute(() => apiClient.getLocalTransport(request));
  }, [api]);

  const getTripById = useCallback(async (tripId: string) => {
    return api.execute(() => apiClient.getTripById(tripId));
  }, [api]);

  const saveTrip = useCallback(async (itinerary: any) => {
    return api.execute(() => apiClient.saveTrip(itinerary));
  }, [api]);

  return {
    ...api,
    planTrip,
    searchFlights,
    getLocalTransport,
    getTripById,
    saveTrip,
  };
}