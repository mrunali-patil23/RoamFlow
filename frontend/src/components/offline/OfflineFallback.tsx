/**
 * Offline fallback component for the AI Trip Planner.
 * 
 * This component displays cached trip data when the application is offline
 * and provides options for managing cached data.
 */

import React, { useState, useEffect } from 'react';
import { useOfflineCache } from '../../hooks/useOfflineCache';
import { CachedTripPlan, TripPlan } from '../../services/offlineCacheService';

interface OfflineFallbackProps {
  className?: string;
  onTripSelect?: (tripPlan: TripPlan) => void;
}

const OfflineFallback: React.FC<OfflineFallbackProps> = ({ 
  className = '', 
  onTripSelect 
}) => {
  const { 
    isOnline, 
    offlineStatus, 
    getLastCachedItinerary, 
    getCachedTripPlans,
    clearAllCache,
    cacheInfo
  } = useOfflineCache();

  const [lastItinerary, setLastItinerary] = useState<CachedTripPlan | null>(null);
  const [cachedPlans, setCachedPlans] = useState<TripPlan[]>([]);
  const [selectedTab, setSelectedTab] = useState<'last' | 'saved'>('last');

  useEffect(() => {
    // Load cached data when component mounts or when cache changes
    setLastItinerary(getLastCachedItinerary());
    setCachedPlans(getCachedTripPlans());
  }, [getLastCachedItinerary, getCachedTripPlans, cacheInfo]);

  // Don't show if online or no cached data
  if (isOnline || !offlineStatus.hasCachedData) {
    return null;
  }

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleTripSelect = (tripPlan: TripPlan) => {
    if (onTripSelect) {
      onTripSelect(tripPlan);
    }
  };

  const handleClearCache = () => {
    if (window.confirm('Are you sure you want to clear all cached data? This cannot be undone.')) {
      clearAllCache();
      setLastItinerary(null);
      setCachedPlans([]);
    }
  };

  return (
    <div className={`bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 ${className}`}>
      {/* Offline header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <h2 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
            You're Offline
          </h2>
        </div>
        <button
          onClick={handleClearCache}
          className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          title="Clear all cached data"
        >
          🗑️ Clear Cache
        </button>
      </div>

      <p className="text-yellow-700 dark:text-yellow-300 mb-4">
        You're currently offline, but we have some cached data available for you to view.
      </p>

      {/* Tab navigation */}
      <div className="flex space-x-4 mb-4 border-b border-yellow-200 dark:border-yellow-800">
        <button
          onClick={() => setSelectedTab('last')}
          className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
            selectedTab === 'last'
              ? 'border-yellow-500 text-yellow-700 dark:text-yellow-300'
              : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
          }`}
        >
          Last Generated Trip
          {cacheInfo.hasLastItinerary && (
            <span className="ml-1 inline-flex items-center justify-center w-2 h-2 bg-yellow-500 rounded-full"></span>
          )}
        </button>
        <button
          onClick={() => setSelectedTab('saved')}
          className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
            selectedTab === 'saved'
              ? 'border-yellow-500 text-yellow-700 dark:text-yellow-300'
              : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
          }`}
        >
          Saved Trips
          {cacheInfo.cachedPlansCount > 0 && (
            <span className="ml-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-yellow-800 bg-yellow-200 rounded-full">
              {cacheInfo.cachedPlansCount}
            </span>
          )}
        </button>
      </div>

      {/* Tab content */}
      <div className="space-y-4">
        {selectedTab === 'last' && (
          <div>
            {lastItinerary ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {lastItinerary.preferences.destination}
                  </h3>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(lastItinerary.preferences.startDate)} - {formatDate(lastItinerary.preferences.endDate)}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Travel Type:</span>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {lastItinerary.preferences.travelType}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Budget:</span>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {formatCurrency(lastItinerary.preferences.maxBudgetInr)}
                    </p>
                  </div>
                </div>

                <div className="mb-3">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Interests:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {lastItinerary.preferences.interests.map((interest, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => handleTripSelect(lastItinerary.tripPlan)}
                  className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  View Trip Details
                </button>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <p>No cached trip available</p>
                <p className="text-sm mt-1">Generate a trip while online to cache it for offline viewing</p>
              </div>
            )}
          </div>
        )}

        {selectedTab === 'saved' && (
          <div>
            {cachedPlans.length > 0 ? (
              <div className="space-y-3">
                {cachedPlans.map((trip, index) => (
                  <div
                    key={trip.id || index}
                    className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-md font-medium text-gray-900 dark:text-gray-100">
                        {trip.preferences.destination}
                      </h3>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {trip.preferences.travelDays} days
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {formatDate(trip.preferences.startDate)} - {trip.preferences.travelType}
                      </div>
                      <button
                        onClick={() => handleTripSelect(trip)}
                        className="text-yellow-600 hover:text-yellow-700 dark:text-yellow-400 dark:hover:text-yellow-300 text-sm font-medium"
                      >
                        View →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <p>No saved trips cached</p>
                <p className="text-sm mt-1">Save trips while online to access them offline</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Cache info */}
      <div className="mt-4 pt-4 border-t border-yellow-200 dark:border-yellow-800">
        <div className="flex items-center justify-between text-xs text-yellow-700 dark:text-yellow-300">
          <span>
            {cacheInfo.isExpired ? '⚠️ Cache expired' : '✅ Cache valid'}
          </span>
          <span>
            Last updated: {cacheInfo.cacheAge ? new Date(Date.now() - cacheInfo.cacheAge).toLocaleString() : 'Unknown'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default OfflineFallback;