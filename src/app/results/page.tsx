'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import ItineraryDisplay from '../../components/ItineraryDisplay';
import BudgetBreakdown from '../../components/BudgetBreakdown';
import MapVisualization from '../../components/MapVisualization';
import { ApiErrorBoundary } from '../../components/ApiErrorBoundary';
import { useTripApi } from '../../hooks/useApi';
import { useTripPlanning } from '../../contexts/TripPlanningContext';
import { getErrorMessage } from '../../lib/api';

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { getTripById, loading, error } = useTripApi();
  const { 
    state, 
    setCurrentItinerary, 
    setLoading, 
    setError, 
    resetForm 
  } = useTripPlanning();
  const [activeTab, setActiveTab] = useState<'itinerary' | 'budget' | 'map'>('itinerary');

  // Use itinerary from global context if available, otherwise use local state
  const itinerary = state.currentItinerary;

  useEffect(() => {
    const loadTripData = async () => {
      const tripId = searchParams.get('tripId');
      
      // If we already have itinerary in global context, use it
      if (itinerary) {
        return;
      }
      
      // First, try to get data from sessionStorage (for newly created trips)
      const sessionData = sessionStorage.getItem('currentTrip');
      if (sessionData) {
        try {
          const parsedData = JSON.parse(sessionData);
          setCurrentItinerary(parsedData);
          return;
        } catch (e) {
          console.error('Error parsing session data:', e);
        }
      }
      
      // If no session data and we have a trip ID, fetch from API
      if (tripId) {
        setLoading({ isLoading: true, message: 'Loading your itinerary...' });
        try {
          const response = await getTripById(tripId);
          if (response && response.success && response.data) {
            setCurrentItinerary(response.data);
            setLoading({ isLoading: false });
          } else {
            const errorMessage = response?.message || 'Failed to load trip data';
            setError({
              success: false,
              error: true,
              message: errorMessage,
              error_code: 'TRIP_LOAD_FAILED'
            });
            setLoading({ isLoading: false });
          }
        } catch (err) {
          console.error('Error loading trip:', err);
          setError({
            success: false,
            error: true,
            message: getErrorMessage(err),
            error_code: 'NETWORK_ERROR'
          });
          setLoading({ isLoading: false });
        }
      } else {
        // No trip ID and no session data - redirect to home
        router.push('/');
      }
    };

    loadTripData();
  }, [searchParams, getTripById, router, itinerary, setCurrentItinerary, setLoading, setError]);

  const handlePlanNewTrip = () => {
    resetForm();
    router.push('/');
  };

  const handleRetryLoad = () => {
    window.location.reload();
  };

  if (loading || state.loading.isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {state.loading.message || 'Loading your itinerary...'}
          </p>
        </div>
      </div>
    );
  }

  if (error || state.error) {
    const errorMessage = error || state.error?.message || 'An error occurred';
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to load your trip</h2>
          <p className="text-gray-600 mb-4">{errorMessage}</p>
          <div className="space-x-4">
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
            <button
              onClick={handlePlanNewTrip}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Plan New Trip
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No trip found</h2>
          <p className="text-gray-600 mb-4">
            We couldn't find your trip. Please try planning a new one.
          </p>
          <button
            onClick={handlePlanNewTrip}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Plan New Trip
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Your Travel Itinerary
          </h1>
          <p className="text-gray-600">
            Here's your personalized travel plan for {itinerary.destination}
          </p>
        </header>
        
        <main className="max-w-7xl mx-auto">
          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setActiveTab('itinerary')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'itinerary'
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                📅 Itinerary
              </button>
              <button
                onClick={() => setActiveTab('budget')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'budget'
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                💰 Budget
              </button>
              <button
                onClick={() => setActiveTab('map')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'map'
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                🗺️ Map
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <ApiErrorBoundary onRetry={handleRetryLoad}>
            <div className="bg-white rounded-lg shadow-lg p-6">
              {activeTab === 'itinerary' && <ItineraryDisplay itinerary={itinerary} />}
              {activeTab === 'budget' && <BudgetBreakdown itinerary={itinerary} />}
              {activeTab === 'map' && <MapVisualization itinerary={itinerary} />}
            </div>
          </ApiErrorBoundary>

          {/* Action Buttons */}
          <div className="mt-8 flex justify-center gap-4">
            <button
              onClick={handlePlanNewTrip}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Plan Another Trip
            </button>
            <button
              onClick={() => window.print()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Save Itinerary
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <ApiErrorBoundary>
        <ResultsContent />
      </ApiErrorBoundary>
    </Suspense>
  );
}