import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ItineraryDisplay from '../components/trip/ItineraryDisplay';
import CostBreakdown from '../components/trip/CostBreakdown';
import BudgetStatus from '../components/trip/BudgetStatus';
// import PDFExporter from '../components/export/PDFExporter';
// import ShareableLink from '../components/share/ShareableLink';

interface TripPlan {
  id: string;
  user_id: string;
  preferences: any;
  itinerary: any;
  cost_breakdown: any;
  budget_status: any;
}

const TripResultsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const tripPlan = location.state?.tripPlan as TripPlan;

  if (!tripPlan) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Trip Plan Not Found
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              The trip plan could not be loaded. Please try creating a new trip plan.
            </p>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Back to Trip Planner
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Your Trip to {tripPlan.preferences.destination}
            </h1>
            <button
              onClick={() => navigate('/')}
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
            >
              Plan Another Trip
            </button>
          </div>
          
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-300">
            <span>📅 {tripPlan.preferences.start_date} to {tripPlan.preferences.end_date}</span>
            <span>🎒 {tripPlan.preferences.travel_type}</span>
            <span>💰 {tripPlan.preferences.budget_preference} Budget</span>
            <span>🗓️ {tripPlan.preferences.travel_days} Days</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mb-8 flex flex-wrap gap-4">
          {/* <PDFExporter tripPlan={tripPlan} />
          <ShareableLink tripPlan={tripPlan} /> */}
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Export to PDF
          </button>
          <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Share Trip
          </button>
        </div>

        {/* Budget Status */}
        <div className="mb-8">
          <BudgetStatus 
            budgetStatus={{
              status: tripPlan.budget_status.status,
              differenceInr: tripPlan.budget_status.difference_inr,
              suggestions: tripPlan.budget_status.suggestions
            }}
            maxBudget={tripPlan.preferences.max_budget_inr}
            totalCost={tripPlan.cost_breakdown.total_cost_inr}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Itinerary - Takes up 2 columns on large screens */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Day-by-Day Itinerary
              </h2>
              <ItineraryDisplay itinerary={{
                tripId: tripPlan.itinerary.trip_id,
                days: tripPlan.itinerary.days.map((day: any) => ({
                  dayNumber: day.day_number,
                  date: day.date,
                  activities: day.activities.map((activity: any) => ({
                    name: activity.name,
                    activityType: activity.activity_type as any,
                    description: activity.description,
                    durationHours: activity.duration_hours,
                    costInr: activity.cost_inr,
                    location: activity.location,
                    rating: activity.rating,
                    startTime: activity.start_time,
                    endTime: activity.end_time,
                    bookingRequired: activity.booking_required,
                    sourceData: activity.source_data
                  })),
                  weather: {
                    date: day.weather?.date || day.date,
                    temperatureHigh: day.weather?.temperature_high,
                    temperatureLow: day.weather?.temperature_low,
                    condition: day.weather?.condition || 'Unknown',
                    description: day.weather?.description || '',
                    humidity: day.weather?.humidity,
                    precipitationChance: day.weather?.precipitation_chance
                  },
                  dailyCostInr: day.daily_cost_inr,
                  notes: day.notes || ''
                })),
                totalCostInr: tripPlan.itinerary.total_cost_inr,
                createdAt: tripPlan.created_at
              }} />
            </div>
          </div>

          {/* Cost Breakdown - Takes up 1 column */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Cost Breakdown
              </h2>
              <CostBreakdown costBreakdown={{
                flightCostInr: tripPlan.cost_breakdown.flight_cost_inr,
                hotelCostInr: tripPlan.cost_breakdown.hotel_cost_inr,
                attractionsCostInr: tripPlan.cost_breakdown.attractions_cost_inr,
                eventsCostInr: tripPlan.cost_breakdown.events_cost_inr,
                localExpensesInr: tripPlan.cost_breakdown.local_expenses_inr,
                totalCostInr: tripPlan.cost_breakdown.total_cost_inr,
                dailyBreakdown: [] // Backend doesn't return daily breakdown yet
              }} />
            </div>
          </div>
        </div>

        {/* Trip Summary */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Trip Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {tripPlan.itinerary.days?.length || tripPlan.preferences.travel_days}
              </div>
              <div className="text-gray-600 dark:text-gray-300">Days</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                ₹{tripPlan.itinerary.total_cost_inr?.toLocaleString() || '0'}
              </div>
              <div className="text-gray-600 dark:text-gray-300">Total Cost</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {tripPlan.itinerary.days?.reduce((total: number, day: any) => 
                  total + (day.activities?.length || 0), 0) || 0}
              </div>
              <div className="text-gray-600 dark:text-gray-300">Activities</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripResultsPage;