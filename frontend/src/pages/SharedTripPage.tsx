import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { TripPlan } from '../types/trip';
import ItineraryDisplay from '../components/trip/ItineraryDisplay';
import CostBreakdown from '../components/trip/CostBreakdown';
import BudgetStatus from '../components/trip/BudgetStatus';
import PDFExporter from '../components/export/PDFExporter';
import { format } from 'date-fns';

const SharedTripPage: React.FC = () => {
  const { encodedData } = useParams<{ encodedData: string }>();
  const [tripPlan, setTripPlan] = useState<TripPlan | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const decodeTripData = () => {
      try {
        if (!encodedData) {
          throw new Error('No trip data provided');
        }

        const decodedData = atob(encodedData);
        const parsedTripPlan: TripPlan = JSON.parse(decodedData);
        
        // Validate that the decoded data has the required structure
        if (!parsedTripPlan.id || !parsedTripPlan.preferences || !parsedTripPlan.itinerary) {
          throw new Error('Invalid trip data structure');
        }

        setTripPlan(parsedTripPlan);
      } catch (err) {
        console.error('Error decoding trip data:', err);
        setError('Invalid or corrupted trip link. Please check the URL and try again.');
      } finally {
        setLoading(false);
      }
    };

    decodeTripData();
  }, [encodedData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">Loading trip plan...</p>
        </div>
      </div>
    );
  }

  if (error || !tripPlan) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Unable to Load Trip
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            {error}
          </p>
          <Link
            to="/"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Create Your Own Trip
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Shared Trip Plan
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <PDFExporter tripPlan={tripPlan} />
              <Link
                to="/"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-sm"
              >
                Create Your Own Trip
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Trip Overview */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {tripPlan.preferences.destination}
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              {format(new Date(tripPlan.preferences.startDate), 'MMM dd, yyyy')} - {format(new Date(tripPlan.preferences.endDate), 'MMM dd, yyyy')}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              {tripPlan.preferences.travelDays} days • {tripPlan.preferences.travelType} • {tripPlan.preferences.budgetPreference} budget
            </p>
          </div>

          {/* Trip Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Travel Type</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{tripPlan.preferences.travelType}</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Budget Level</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">{tripPlan.preferences.budgetPreference}</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Max Budget</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">₹{tripPlan.preferences.maxBudgetInr.toLocaleString('en-IN')}</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Cost</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">₹{tripPlan.costBreakdown.totalCostInr.toLocaleString('en-IN')}</p>
            </div>
          </div>

          {/* Interests */}
          <div className="text-center">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Interests</h3>
            <div className="flex flex-wrap justify-center gap-2">
              {tripPlan.preferences.interests.map((interest) => (
                <span
                  key={interest}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full"
                >
                  {interest}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Budget Status */}
        <div className="mb-6">
          <BudgetStatus budgetStatus={tripPlan.budgetStatus} />
        </div>

        {/* Cost Breakdown */}
        <div className="mb-6">
          <CostBreakdown costBreakdown={tripPlan.costBreakdown} />
        </div>

        {/* Itinerary */}
        <div>
          <ItineraryDisplay itinerary={tripPlan.itinerary} />
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 dark:text-gray-400">
          <p className="text-sm">
            This trip was planned using AI Trip Planner. 
            <Link to="/" className="text-blue-500 hover:text-blue-700 ml-1">
              Create your own trip plan
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
};

export default SharedTripPage;