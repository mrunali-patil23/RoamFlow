'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { TripFormData, FormErrors, LoadingState, TripItinerary, ErrorResponse, BudgetCategory, TravelerType } from '@/types';

// Action types for the reducer
type TripPlanningAction =
  | { type: 'SET_FORM_DATA'; payload: Partial<TripFormData> }
  | { type: 'SET_FORM_ERRORS'; payload: FormErrors }
  | { type: 'CLEAR_FORM_ERRORS' }
  | { type: 'SET_LOADING'; payload: LoadingState }
  | { type: 'SET_CURRENT_ITINERARY'; payload: TripItinerary | null }
  | { type: 'SET_ERROR'; payload: ErrorResponse | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESET_FORM' }
  | { type: 'LOAD_PREFERENCES'; payload: Partial<TripFormData> }
  | { type: 'SAVE_PREFERENCES'; payload: { budget?: BudgetCategory; travelerType?: TravelerType } };

// State interface
interface TripPlanningState {
  formData: TripFormData;
  formErrors: FormErrors;
  loading: LoadingState;
  currentItinerary: TripItinerary | null;
  error: ErrorResponse | null;
  preferences: {
    budget?: BudgetCategory;
    travelerType?: TravelerType;
  };
}

// Context interface
interface TripPlanningContextType {
  state: TripPlanningState;
  dispatch: React.Dispatch<TripPlanningAction>;
  // Convenience methods
  setFormData: (data: Partial<TripFormData>) => void;
  setFormErrors: (errors: FormErrors) => void;
  clearFormErrors: () => void;
  setLoading: (loading: LoadingState) => void;
  setCurrentItinerary: (itinerary: TripItinerary | null) => void;
  setError: (error: ErrorResponse | null) => void;
  clearError: () => void;
  resetForm: () => void;
  savePreferences: (preferences: { budget?: BudgetCategory; travelerType?: TravelerType }) => void;
}

// Initial state
const initialState: TripPlanningState = {
  formData: {
    destination: '',
    days: '',
    budget: '',
    travelerType: ''
  },
  formErrors: {},
  loading: {
    isLoading: false,
    message: undefined
  },
  currentItinerary: null,
  error: null,
  preferences: {}
};

// Reducer function
function tripPlanningReducer(state: TripPlanningState, action: TripPlanningAction): TripPlanningState {
  switch (action.type) {
    case 'SET_FORM_DATA':
      return {
        ...state,
        formData: { ...state.formData, ...action.payload }
      };
    
    case 'SET_FORM_ERRORS':
      return {
        ...state,
        formErrors: action.payload
      };
    
    case 'CLEAR_FORM_ERRORS':
      return {
        ...state,
        formErrors: {}
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    
    case 'SET_CURRENT_ITINERARY':
      return {
        ...state,
        currentItinerary: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      };
    
    case 'RESET_FORM':
      return {
        ...state,
        formData: {
          destination: '',
          days: '',
          budget: state.preferences.budget || '',
          travelerType: state.preferences.travelerType || ''
        },
        formErrors: {},
        error: null
      };
    
    case 'LOAD_PREFERENCES':
      return {
        ...state,
        preferences: {
          budget: action.payload.budget as BudgetCategory,
          travelerType: action.payload.travelerType as TravelerType
        },
        formData: {
          ...state.formData,
          budget: action.payload.budget || state.formData.budget,
          travelerType: action.payload.travelerType || state.formData.travelerType
        }
      };
    
    case 'SAVE_PREFERENCES':
      return {
        ...state,
        preferences: {
          ...state.preferences,
          ...action.payload
        }
      };
    
    default:
      return state;
  }
}

// Create context
const TripPlanningContext = createContext<TripPlanningContextType | undefined>(undefined);

// Provider component
interface TripPlanningProviderProps {
  children: ReactNode;
}

export function TripPlanningProvider({ children }: TripPlanningProviderProps) {
  const [state, dispatch] = useReducer(tripPlanningReducer, initialState);

  // Load preferences from localStorage on mount
  useEffect(() => {
    try {
      const savedPreferences = localStorage.getItem('tripPlanningPreferences');
      if (savedPreferences) {
        const preferences = JSON.parse(savedPreferences);
        dispatch({ type: 'LOAD_PREFERENCES', payload: preferences });
      }
    } catch (error) {
      console.warn('Failed to load preferences from localStorage:', error);
    }
  }, []);

  // Save preferences to localStorage when they change
  useEffect(() => {
    try {
      if (state.preferences.budget || state.preferences.travelerType) {
        localStorage.setItem('tripPlanningPreferences', JSON.stringify(state.preferences));
      }
    } catch (error) {
      console.warn('Failed to save preferences to localStorage:', error);
    }
  }, [state.preferences]);

  // Convenience methods
  const setFormData = (data: Partial<TripFormData>) => {
    dispatch({ type: 'SET_FORM_DATA', payload: data });
  };

  const setFormErrors = (errors: FormErrors) => {
    dispatch({ type: 'SET_FORM_ERRORS', payload: errors });
  };

  const clearFormErrors = () => {
    dispatch({ type: 'CLEAR_FORM_ERRORS' });
  };

  const setLoading = (loading: LoadingState) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setCurrentItinerary = (itinerary: TripItinerary | null) => {
    dispatch({ type: 'SET_CURRENT_ITINERARY', payload: itinerary });
  };

  const setError = (error: ErrorResponse | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const resetForm = () => {
    dispatch({ type: 'RESET_FORM' });
  };

  const savePreferences = (preferences: { budget?: BudgetCategory; travelerType?: TravelerType }) => {
    dispatch({ type: 'SAVE_PREFERENCES', payload: preferences });
  };

  const contextValue: TripPlanningContextType = {
    state,
    dispatch,
    setFormData,
    setFormErrors,
    clearFormErrors,
    setLoading,
    setCurrentItinerary,
    setError,
    clearError,
    resetForm,
    savePreferences
  };

  return (
    <TripPlanningContext.Provider value={contextValue}>
      {children}
    </TripPlanningContext.Provider>
  );
}

// Custom hook to use the context
export function useTripPlanning() {
  const context = useContext(TripPlanningContext);
  if (context === undefined) {
    throw new Error('useTripPlanning must be used within a TripPlanningProvider');
  }
  return context;
}

// Export the context for testing purposes
export { TripPlanningContext };