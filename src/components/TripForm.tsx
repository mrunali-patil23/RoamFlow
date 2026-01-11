'use client';

import { useEffect } from 'react';
import { TripFormData, FormErrors, BudgetCategory, TravelerType } from '@/types';
import { useTripPlanning } from '@/contexts/TripPlanningContext';
import { usePreferences } from '@/hooks/usePreferences';
import DestinationSelector from './DestinationSelector';
import BudgetSelector from './BudgetSelector';
import TravelerTypeSelector from './TravelerTypeSelector';

interface TripFormProps {
  onSubmit: (formData: TripFormData) => void;
  isLoading?: boolean;
  error?: string | null;
}

export default function TripForm({ onSubmit, isLoading = false, error }: TripFormProps) {
  const { 
    state, 
    setFormData, 
    setFormErrors, 
    clearFormErrors 
  } = useTripPlanning();

  const { 
    saveTripToHistory, 
    getFavoriteDestinations,
    getPreferenceSuggestions 
  } = usePreferences();

  const { formData, formErrors } = state;

  // Load preference suggestions on component mount
  useEffect(() => {
    const suggestions = getPreferenceSuggestions();
    
    // Only pre-populate if form is empty
    if (!formData.budget && !formData.travelerType) {
      const updates: Partial<TripFormData> = {};
      
      if (suggestions.budget) {
        updates.budget = suggestions.budget;
      }
      
      if (suggestions.travelerType) {
        updates.travelerType = suggestions.travelerType;
      }
      
      if (suggestions.defaultTripDuration && !formData.days) {
        updates.days = suggestions.defaultTripDuration;
      }
      
      if (Object.keys(updates).length > 0) {
        setFormData(updates);
      }
    }
  }, [formData, setFormData, getPreferenceSuggestions]);

  // Clear errors when external error prop changes
  useEffect(() => {
    if (!error && formErrors.general) {
      setFormErrors({ ...formErrors, general: undefined });
    }
  }, [error, formErrors, setFormErrors]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Validate destination
    if (!formData.destination.trim()) {
      newErrors.destination = 'Please select a destination';
    }

    // Validate days
    if (formData.days === '' || !formData.days) {
      newErrors.days = 'Please enter the number of days';
    } else {
      const daysNum = typeof formData.days === 'string' ? parseInt(formData.days, 10) : formData.days;
      if (isNaN(daysNum) || daysNum < 1 || daysNum > 30) {
        newErrors.days = 'Number of days must be between 1 and 30';
      }
    }

    // Validate budget
    if (!formData.budget) {
      newErrors.budget = 'Please select a budget category';
    }

    // Validate traveler type
    if (!formData.travelerType) {
      newErrors.travelerType = 'Please select your traveler type';
    }

    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Save trip to history and update preferences
      const tripData = {
        destination: formData.destination,
        days: typeof formData.days === 'string' ? parseInt(formData.days, 10) : formData.days,
        budget: formData.budget as BudgetCategory,
        travelerType: formData.travelerType as TravelerType
      };
      
      saveTripToHistory(tripData);

      // Convert days to number for submission
      const submissionData: TripFormData = {
        ...formData,
        days: tripData.days
      };
      onSubmit(submissionData);
    }
  };

  const handleDestinationChange = (destination: string) => {
    setFormData({ destination });
    if (formErrors.destination) {
      setFormErrors({ ...formErrors, destination: undefined });
    }
  };

  const handleDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData({ days: value === '' ? '' : parseInt(value, 10) });
    if (formErrors.days) {
      setFormErrors({ ...formErrors, days: undefined });
    }
  };

  const handleBudgetChange = (budget: BudgetCategory) => {
    setFormData({ budget });
    if (formErrors.budget) {
      setFormErrors({ ...formErrors, budget: undefined });
    }
  };

  const handleTravelerTypeChange = (travelerType: TravelerType) => {
    setFormData({ travelerType });
    if (formErrors.travelerType) {
      setFormErrors({ ...formErrors, travelerType: undefined });
    }
  };

  // Get favorite destinations for the destination selector
  const favoriteDestinations = getFavoriteDestinations();

  return (
    <form onSubmit={handleSubmit} className="space-y-8" role="form">
      {/* Destination Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Where would you like to go?
        </label>
        {favoriteDestinations.length > 0 && (
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-2">Recent destinations:</p>
            <div className="flex flex-wrap gap-2">
              {favoriteDestinations.slice(0, 3).map((dest) => (
                <button
                  key={dest}
                  type="button"
                  onClick={() => handleDestinationChange(dest)}
                  className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                >
                  {dest}
                </button>
              ))}
            </div>
          </div>
        )}
        <DestinationSelector
          value={formData.destination}
          onChange={handleDestinationChange}
          error={formErrors.destination}
        />
      </div>

      {/* Trip Duration */}
      <div>
        <label htmlFor="days" className="block text-sm font-medium text-gray-700 mb-2">
          How many days?
        </label>
        <input
          type="number"
          id="days"
          min="1"
          max="30"
          value={formData.days}
          onChange={handleDaysChange}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            formErrors.days ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter number of days (1-30)"
          disabled={isLoading}
        />
        {formErrors.days && (
          <p className="mt-1 text-sm text-red-600">{formErrors.days}</p>
        )}
      </div>

      {/* Budget Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What's your budget?
        </label>
        <BudgetSelector
          value={formData.budget}
          onChange={handleBudgetChange}
          error={formErrors.budget}
        />
      </div>

      {/* Traveler Type Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Who's traveling?
        </label>
        <TravelerTypeSelector
          value={formData.travelerType}
          onChange={handleTravelerTypeChange}
          error={formErrors.travelerType}
        />
      </div>

      {/* General Error Display */}
      {((formErrors.general && formErrors.general.trim()) || (error && error.trim())) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-600">
            {(formErrors.general && formErrors.general.trim()) || (error && error.trim())}
          </p>
        </div>
      )}

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-colors ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Planning your trip...
            </span>
          ) : (
            'Plan My Trip'
          )}
        </button>
      </div>
    </form>
  );
}