'use client';

import { useEffect, useCallback } from 'react';
import { BudgetCategory, TravelerType, TripFormData } from '@/types';
import { useTripPlanning } from '@/contexts/TripPlanningContext';

// Extended preferences interface
interface UserPreferences {
  budget?: BudgetCategory;
  travelerType?: TravelerType;
  favoriteDestinations?: string[];
  lastUsedDestination?: string;
  defaultTripDuration?: number;
  preferencesSavedAt?: string;
}

// Storage keys
const PREFERENCES_KEY = 'tripPlanningPreferences';
const TRIP_HISTORY_KEY = 'tripPlanningHistory';

export function usePreferences() {
  const { state, setFormData, savePreferences } = useTripPlanning();

  // Load preferences from localStorage
  const loadPreferences = useCallback((): UserPreferences => {
    try {
      const saved = localStorage.getItem(PREFERENCES_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (error) {
      console.warn('Failed to load preferences:', error);
    }
    return {};
  }, []);

  // Save preferences to localStorage
  const saveUserPreferences = useCallback((preferences: UserPreferences) => {
    try {
      const updatedPreferences = {
        ...preferences,
        preferencesSavedAt: new Date().toISOString()
      };
      localStorage.setItem(PREFERENCES_KEY, JSON.stringify(updatedPreferences));
      
      // Update global context
      savePreferences({
        budget: preferences.budget,
        travelerType: preferences.travelerType
      });
    } catch (error) {
      console.warn('Failed to save preferences:', error);
    }
  }, [savePreferences]);

  // Update specific preference
  const updatePreference = useCallback(<K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => {
    const currentPreferences = loadPreferences();
    const updatedPreferences = {
      ...currentPreferences,
      [key]: value
    };
    saveUserPreferences(updatedPreferences);
  }, [loadPreferences, saveUserPreferences]);

  // Add destination to favorites
  const addFavoriteDestination = useCallback((destination: string) => {
    const preferences = loadPreferences();
    const favorites = preferences.favoriteDestinations || [];
    
    if (!favorites.includes(destination)) {
      const updatedFavorites = [destination, ...favorites].slice(0, 5); // Keep only top 5
      updatePreference('favoriteDestinations', updatedFavorites);
    }
  }, [loadPreferences, updatePreference]);

  // Get favorite destinations
  const getFavoriteDestinations = useCallback((): string[] => {
    const preferences = loadPreferences();
    return preferences.favoriteDestinations || [];
  }, [loadPreferences]);

  // Pre-populate form with preferences
  const prePopulateForm = useCallback(() => {
    const preferences = loadPreferences();
    const formUpdates: Partial<TripFormData> = {};

    if (preferences.budget && !state.formData.budget) {
      formUpdates.budget = preferences.budget;
    }

    if (preferences.travelerType && !state.formData.travelerType) {
      formUpdates.travelerType = preferences.travelerType;
    }

    if (preferences.lastUsedDestination && !state.formData.destination) {
      formUpdates.destination = preferences.lastUsedDestination;
    }

    if (preferences.defaultTripDuration && !state.formData.days) {
      formUpdates.days = preferences.defaultTripDuration;
    }

    if (Object.keys(formUpdates).length > 0) {
      setFormData(formUpdates);
    }
  }, [loadPreferences, state.formData, setFormData]);

  // Save trip to history
  const saveTripToHistory = useCallback((tripData: {
    destination: string;
    days: number;
    budget: BudgetCategory;
    travelerType: TravelerType;
    tripId?: string;
    createdAt?: string;
  }) => {
    try {
      const historyData = {
        ...tripData,
        createdAt: tripData.createdAt || new Date().toISOString()
      };

      // Update preferences based on this trip
      saveUserPreferences({
        ...loadPreferences(),
        budget: tripData.budget,
        travelerType: tripData.travelerType,
        lastUsedDestination: tripData.destination,
        defaultTripDuration: tripData.days
      });

      // Add to favorites
      addFavoriteDestination(tripData.destination);

      // Save to trip history
      const existingHistory = JSON.parse(localStorage.getItem(TRIP_HISTORY_KEY) || '[]');
      const updatedHistory = [historyData, ...existingHistory].slice(0, 10); // Keep only last 10 trips
      localStorage.setItem(TRIP_HISTORY_KEY, JSON.stringify(updatedHistory));
    } catch (error) {
      console.warn('Failed to save trip to history:', error);
    }
  }, [loadPreferences, saveUserPreferences, addFavoriteDestination]);

  // Get trip history
  const getTripHistory = useCallback(() => {
    try {
      const history = localStorage.getItem(TRIP_HISTORY_KEY);
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.warn('Failed to load trip history:', error);
      return [];
    }
  }, []);

  // Clear all preferences
  const clearPreferences = useCallback(() => {
    try {
      localStorage.removeItem(PREFERENCES_KEY);
      localStorage.removeItem(TRIP_HISTORY_KEY);
      savePreferences({});
    } catch (error) {
      console.warn('Failed to clear preferences:', error);
    }
  }, [savePreferences]);

  // Get preference suggestions based on history
  const getPreferenceSuggestions = useCallback(() => {
    const preferences = loadPreferences();
    const history = getTripHistory();
    
    // Analyze trip history to suggest preferences
    const budgetCounts: Record<BudgetCategory, number> = {
      cheap: 0,
      moderate: 0,
      luxury: 0
    };
    
    const travelerTypeCounts: Record<TravelerType, number> = {
      'just-me': 0,
      couple: 0,
      family: 0,
      friends: 0
    };

    history.forEach((trip: any) => {
      if (trip.budget) budgetCounts[trip.budget as BudgetCategory]++;
      if (trip.travelerType) travelerTypeCounts[trip.travelerType as TravelerType]++;
    });

    // Find most common preferences
    const suggestedBudget = Object.entries(budgetCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] as BudgetCategory;
    
    const suggestedTravelerType = Object.entries(travelerTypeCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] as TravelerType;

    return {
      budget: preferences.budget || suggestedBudget,
      travelerType: preferences.travelerType || suggestedTravelerType,
      favoriteDestinations: preferences.favoriteDestinations || [],
      lastUsedDestination: preferences.lastUsedDestination,
      defaultTripDuration: preferences.defaultTripDuration || 7
    };
  }, [loadPreferences, getTripHistory]);

  // Auto-load preferences on mount
  useEffect(() => {
    prePopulateForm();
  }, [prePopulateForm]);

  return {
    preferences: state.preferences,
    loadPreferences,
    saveUserPreferences,
    updatePreference,
    addFavoriteDestination,
    getFavoriteDestinations,
    prePopulateForm,
    saveTripToHistory,
    getTripHistory,
    clearPreferences,
    getPreferenceSuggestions
  };
}