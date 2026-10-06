import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TripInputForm } from '../components/trip';
import { TripFormData } from '../types/trip';
import ApiService, { ValidationError, NetworkError, AuthenticationError } from '../services/apiService';
import NetworkStatus from '../components/ui/NetworkStatus';

const TripPlannerPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showNetworkStatus, setShowNetworkStatus] = useState(false);

  const handleTripSubmit = async (tripData: TripFormData) => {
    setLoading(true);
    setError(null);
    setShowNetworkStatus(false);

    try {
      // Validate trip preferences with backend
      const validationResult = await ApiService.validateTripPreferences(tripData);
      
      if (!validationResult.valid) {
        const errorMessage = validationResult.errors?.join(', ') || validationResult.message;
        throw new ValidationError(errorMessage, validationResult.errors);
      }
      
      // Create the trip plan
      console.log('Creating trip plan with data:', tripData);
      const tripPlan = await ApiService.createTripPlan(tripData);
      
      console.log('Trip plan created successfully:', tripPlan);
      
      // Navigate to results page with trip plan data
      navigate('/trip-results', { 
        state: { tripPlan },
        replace: true 
      });
      
    } catch (err) {
      let errorMessage = 'Failed to create trip plan';
      
      if (err instanceof ValidationError) {
        errorMessage = err.message;
      } else if (err instanceof NetworkError) {
        errorMessage = 'Unable to connect to server. Please check your internet connection.';
        setShowNetworkStatus(true);
      } else if (err instanceof AuthenticationError) {
        errorMessage = 'Please log in again to continue.';
      } else {
        errorMessage = err instanceof Error ? err.message : 'Failed to create trip plan';
      }
      
      setError(errorMessage);
      console.error('Trip planning error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {showNetworkStatus && (
          <div className="mb-6">
            <NetworkStatus />
          </div>
        )}
        <TripInputForm
          onSubmit={handleTripSubmit}
          loading={loading}
          error={error}
        />
      </div>
    </div>
  );
};

export default TripPlannerPage;