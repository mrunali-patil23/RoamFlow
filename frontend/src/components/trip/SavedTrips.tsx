import React, { useState, useEffect } from 'react';
import { TripPlan, TravelType } from '../../types/trip';

interface SavedTripsProps {
  className?: string;
}

interface TripCardProps {
  trip: TripPlan;
  onView: (trip: TripPlan) => void;
  onCompare: (trip: TripPlan) => void;
  onDelete: (tripId: string) => void;
  isSelected?: boolean;
}

interface TripComparisonProps {
  trips: TripPlan[];
  onClose: () => void;
}

const TripCard: React.FC<TripCardProps> = ({ 
  trip, 
  onView, 
  onCompare, 
  onDelete, 
  isSelected = false 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getBudgetStatusColor = (status: string) => {
    switch (status) {
      case 'Within Budget':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20';
      case 'Slightly Over Budget':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20';
      case 'Over Budget':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getTravelTypeIcon = (travelType: TravelType) => {
    switch (travelType) {
      case TravelType.SOLO:
        return '🧳';
      case TravelType.FRIENDS:
        return '👥';
      case TravelType.FAMILY:
        return '👨‍👩‍👧‍👦';
      case TravelType.COUPLE:
        return '💑';
      default:
        return '🧳';
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 transition-all duration-200 ${
      isSelected 
        ? 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-200 dark:ring-blue-800' 
        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
    }`}>
      {/* Trip Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xl">{getTravelTypeIcon(trip.preferences.travelType)}</span>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              {trip.preferences.destination}
            </h3>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            {formatDate(trip.preferences.startDate)} - {formatDate(trip.preferences.endDate)}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {trip.preferences.travelDays} days • {trip.preferences.travelType}
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
            {formatCurrency(trip.itinerary.totalCostInr)}
          </div>
          <div className={`text-xs px-2 py-1 rounded-full ${getBudgetStatusColor(trip.budgetStatus.status)}`}>
            {trip.budgetStatus.status}
          </div>
        </div>
      </div>

      {/* Trip Details */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
          <div className="text-sm text-gray-500 dark:text-gray-400">Activities</div>
          <div className="font-semibold text-gray-900 dark:text-white">
            {trip.itinerary.days.reduce((total, day) => total + day.activities.length, 0)}
          </div>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
          <div className="text-sm text-gray-500 dark:text-gray-400">Budget</div>
          <div className="font-semibold text-gray-900 dark:text-white">
            {formatCurrency(trip.preferences.maxBudgetInr)}
          </div>
        </div>
      </div>

      {/* Interests */}
      <div className="mb-4">
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">Interests</div>
        <div className="flex flex-wrap gap-1">
          {trip.preferences.interests.slice(0, 3).map((interest, index) => (
            <span 
              key={index}
              className="text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 px-2 py-1 rounded"
            >
              {interest}
            </span>
          ))}
          {trip.preferences.interests.length > 3 && (
            <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">
              +{trip.preferences.interests.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Created Date */}
      <div className="text-xs text-gray-400 dark:text-gray-500 mb-4">
        Created: {trip.createdAt ? formatDate(trip.createdAt) : 'Unknown'}
      </div>

      {/* Actions */}
      <div className="flex space-x-2">
        <button
          onClick={() => onView(trip)}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
        >
          View Details
        </button>
        <button
          onClick={() => onCompare(trip)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isSelected
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          {isSelected ? 'Selected' : 'Compare'}
        </button>
        <button
          onClick={() => onDelete(trip.id)}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

const TripComparison: React.FC<TripComparisonProps> = ({ trips, onClose }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Trip Comparison
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Comparison Table */}
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900 dark:text-white">
                    Criteria
                  </th>
                  {trips.map((trip, index) => (
                    <th key={trip.id} className="text-center py-3 px-4 font-semibold text-gray-900 dark:text-white">
                      Trip {index + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Destination</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {trip.preferences.destination}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Dates</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {formatDate(trip.preferences.startDate)} - {formatDate(trip.preferences.endDate)}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Duration</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {trip.preferences.travelDays} days
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Travel Type</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {trip.preferences.travelType}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Budget</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {formatCurrency(trip.preferences.maxBudgetInr)}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Estimated Cost</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center font-semibold text-blue-600 dark:text-blue-400">
                      {formatCurrency(trip.itinerary.totalCostInr)}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Budget Status</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        trip.budgetStatus.status === 'Within Budget' 
                          ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                          : trip.budgetStatus.status === 'Slightly Over Budget'
                          ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200'
                          : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                      }`}>
                        {trip.budgetStatus.status}
                      </span>
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Activities</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      {trip.itinerary.days.reduce((total, day) => total + day.activities.length, 0)}
                    </td>
                  ))}
                </tr>
                
                <tr>
                  <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">Interests</td>
                  {trips.map((trip) => (
                    <td key={trip.id} className="py-3 px-4 text-center text-gray-600 dark:text-gray-300">
                      <div className="flex flex-wrap justify-center gap-1">
                        {trip.preferences.interests.slice(0, 2).map((interest, index) => (
                          <span 
                            key={index}
                            className="text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 px-2 py-1 rounded"
                          >
                            {interest}
                          </span>
                        ))}
                        {trip.preferences.interests.length > 2 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{trip.preferences.interests.length - 2}
                          </span>
                        )}
                      </div>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const SavedTrips: React.FC<SavedTripsProps> = ({ className = '' }) => {
  const [trips, setTrips] = useState<TripPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTrips, setSelectedTrips] = useState<TripPlan[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  const [sortBy, setSortBy] = useState<'date' | 'cost' | 'destination'>('date');
  const [filterBy, setFilterBy] = useState<'all' | 'within-budget' | 'over-budget'>('all');

  // Mock data for development - replace with actual API calls
  useEffect(() => {
    const loadTrips = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        // const response = await fetch('/api/trips/saved');
        // const data = await response.json();
        
        // Mock data for now
        const mockTrips: TripPlan[] = [];
        setTrips(mockTrips);
      } catch (err) {
        setError('Failed to load saved trips');
      } finally {
        setLoading(false);
      }
    };

    loadTrips();
  }, []);

  const handleViewTrip = (trip: TripPlan) => {
    // TODO: Navigate to trip details view
    console.log('Viewing trip:', trip.id);
  };

  const handleCompareTrip = (trip: TripPlan) => {
    const isSelected = selectedTrips.some(t => t.id === trip.id);
    
    if (isSelected) {
      setSelectedTrips(selectedTrips.filter(t => t.id !== trip.id));
    } else if (selectedTrips.length < 3) {
      setSelectedTrips([...selectedTrips, trip]);
    }
  };

  const handleDeleteTrip = async (tripId: string) => {
    if (window.confirm('Are you sure you want to delete this trip?')) {
      try {
        // TODO: Replace with actual API call
        // await fetch(`/api/trips/${tripId}`, { method: 'DELETE' });
        setTrips(trips.filter(trip => trip.id !== tripId));
        setSelectedTrips(selectedTrips.filter(trip => trip.id !== tripId));
      } catch (err) {
        setError('Failed to delete trip');
      }
    }
  };

  const handleStartComparison = () => {
    if (selectedTrips.length >= 2) {
      setShowComparison(true);
    }
  };

  const filteredAndSortedTrips = trips
    .filter(trip => {
      if (filterBy === 'within-budget') return trip.budgetStatus.status === 'Within Budget';
      if (filterBy === 'over-budget') return trip.budgetStatus.status !== 'Within Budget';
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'cost':
          return a.itinerary.totalCostInr - b.itinerary.totalCostInr;
        case 'destination':
          return a.preferences.destination.localeCompare(b.preferences.destination);
        case 'date':
        default:
          return new Date(b.createdAt || '').getTime() - new Date(a.createdAt || '').getTime();
      }
    });

  if (loading) {
    return (
      <div className={`max-w-6xl mx-auto ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`max-w-6xl mx-auto ${className}`}>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <div className="text-red-600 dark:text-red-400 mb-2">⚠️ Error</div>
          <div className="text-red-800 dark:text-red-200">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`max-w-6xl mx-auto ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Saved Trips
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            {trips.length} saved trip{trips.length !== 1 ? 's' : ''}
          </p>
        </div>

        {selectedTrips.length >= 2 && (
          <button
            onClick={handleStartComparison}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Compare {selectedTrips.length} Trips
          </button>
        )}
      </div>

      {/* Filters and Sort */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Sort by:
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="date">Date Created</option>
            <option value="cost">Cost</option>
            <option value="destination">Destination</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Filter:
          </label>
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value as any)}
            className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Trips</option>
            <option value="within-budget">Within Budget</option>
            <option value="over-budget">Over Budget</option>
          </select>
        </div>

        {selectedTrips.length > 0 && (
          <div className="text-sm text-blue-600 dark:text-blue-400">
            {selectedTrips.length} trip{selectedTrips.length !== 1 ? 's' : ''} selected for comparison
          </div>
        )}
      </div>

      {/* Trips Grid */}
      {filteredAndSortedTrips.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🧳</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No saved trips yet
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Start planning your first trip to see it here!
          </p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            Plan New Trip
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedTrips.map((trip) => (
            <TripCard
              key={trip.id}
              trip={trip}
              onView={handleViewTrip}
              onCompare={handleCompareTrip}
              onDelete={handleDeleteTrip}
              isSelected={selectedTrips.some(t => t.id === trip.id)}
            />
          ))}
        </div>
      )}

      {/* Comparison Modal */}
      {showComparison && (
        <TripComparison
          trips={selectedTrips}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
};

export default SavedTrips;