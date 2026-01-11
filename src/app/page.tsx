'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import TripForm from '@/components/TripForm';
import { ApiErrorBoundary } from '@/components/ApiErrorBoundary';
import { TripFormData, TripRequest } from '@/types';
import { useTripApi } from '@/hooks/useApi';
import { useTripPlanning } from '@/contexts/TripPlanningContext';
import { usePreferences } from '@/hooks/usePreferences';
import { isApiError, getErrorMessage } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const { planTrip, loading, error } = useTripApi();
  const { 
    state, 
    setLoading, 
    setError, 
    clearError, 
    setCurrentItinerary 
  } = useTripPlanning();
  const { saveTripToHistory } = usePreferences();
  const [formError, setFormError] = useState<string | null>(null);

  const handleFormSubmit = async (formData: TripFormData) => {
    setFormError(null);
    clearError();
    
    // Set loading state in global context
    setLoading({ isLoading: true, message: 'Planning your trip...' });
    
    try {
      // Convert form data to API request format
      const tripRequest: TripRequest = {
        destination: formData.destination,
        days: typeof formData.days === 'string' ? parseInt(formData.days, 10) : formData.days,
        budget: formData.budget as any,
        travelers: formData.travelerType as any,
      };

      console.log('Submitting trip request:', tripRequest);
      
      // Call the backend API
      const response = await planTrip(tripRequest);
      
      if (response && response.success && response.data) {
        // Store the trip data in global context
        setCurrentItinerary(response.data);
        
        // Save trip to history and update preferences
        saveTripToHistory({
          destination: tripRequest.destination,
          days: tripRequest.days,
          budget: tripRequest.budget,
          travelerType: tripRequest.travelers,
          tripId: response.data.trip_id,
          createdAt: response.data.created_at
        });
        
        // Also store in sessionStorage for backup
        sessionStorage.setItem('currentTrip', JSON.stringify(response.data));
        
        // Clear loading state
        setLoading({ isLoading: false });
        
        // Navigate to results page with trip ID
        router.push(`/results?tripId=${response.data.trip_id}`);
      } else {
        const errorMessage = response?.message || 'Failed to plan trip. Please try again.';
        setFormError(errorMessage);
        setError({
          success: false,
          error: true,
          message: errorMessage,
          error_code: 'TRIP_PLANNING_FAILED'
        });
        setLoading({ isLoading: false });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      const errorMessage = getErrorMessage(error);
      setFormError(errorMessage);
      setError({
        success: false,
        error: true,
        message: errorMessage,
        error_code: 'NETWORK_ERROR'
      });
      setLoading({ isLoading: false });
    }
  };

  const handleRetryFormSubmission = () => {
    setFormError(null);
    clearError();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Travel Planner
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Create personalized travel itineraries with AI-powered planning and real-time transport data
          </p>
        </header>
        
        <main className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Plan Your Perfect Trip
            </h2>
            <p className="text-gray-600 mb-8">
              Tell us about your travel preferences and we'll create a comprehensive itinerary just for you.
            </p>
            
            {/* Display API errors */}
            {(error || formError || state.error) && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="text-red-500 mr-3">⚠️</div>
                  <div>
                    <h3 className="text-sm font-medium text-red-800">
                      Unable to plan your trip
                    </h3>
                    <p className="text-sm text-red-600 mt-1">
                      {error || formError || state.error?.message}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <ApiErrorBoundary onRetry={handleRetryFormSubmission}>
              <TripForm 
                onSubmit={handleFormSubmit} 
                isLoading={loading || state.loading.isLoading} 
              />
            </ApiErrorBoundary>
          </div>
        </main>
      </div>
    </div>
  );
}
