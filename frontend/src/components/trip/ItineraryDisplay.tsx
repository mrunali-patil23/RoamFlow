import React from 'react';
import { Itinerary, DayPlan, Activity, ActivityType } from '../../types/trip';

interface ItineraryDisplayProps {
  itinerary: Itinerary;
  className?: string;
}

interface DayPlanCardProps {
  dayPlan: DayPlan;
}

interface ActivityCardProps {
  activity: Activity;
}

const ActivityCard: React.FC<ActivityCardProps> = ({ activity }) => {
  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case ActivityType.ATTRACTION:
        return '🏛️';
      case ActivityType.EVENT:
        return '🎭';
      case ActivityType.MEAL:
        return '🍽️';
      case ActivityType.TRANSPORT:
        return '🚗';
      case ActivityType.ACCOMMODATION:
        return '🏨';
      case ActivityType.FREE_TIME:
        return '⏰';
      default:
        return '📍';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xl">{getActivityIcon(activity.activityType)}</span>
          <h4 className="font-semibold text-gray-900 dark:text-white">{activity.name}</h4>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-green-600 dark:text-green-400">
            {formatCurrency(activity.costInr)}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {activity.durationHours}h
          </div>
        </div>
      </div>
      
      <p className="text-gray-600 dark:text-gray-300 text-sm mb-2">
        {activity.description}
      </p>
      
      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center space-x-4">
          {activity.location && (
            <span className="flex items-center">
              📍 {activity.location}
            </span>
          )}
          {activity.rating && (
            <span className="flex items-center">
              ⭐ {activity.rating.toFixed(1)}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {activity.startTime && activity.endTime && (
            <span>{activity.startTime} - {activity.endTime}</span>
          )}
          {activity.bookingRequired && (
            <span className="bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded">
              Booking Required
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

const DayPlanCard: React.FC<DayPlanCardProps> = ({ dayPlan }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getWeatherIcon = (condition: string) => {
    const lowerCondition = condition.toLowerCase();
    if (lowerCondition.includes('sunny') || lowerCondition.includes('clear')) return '☀️';
    if (lowerCondition.includes('cloud')) return '☁️';
    if (lowerCondition.includes('rain')) return '🌧️';
    if (lowerCondition.includes('storm')) return '⛈️';
    if (lowerCondition.includes('snow')) return '❄️';
    return '🌤️';
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Day {dayPlan.dayNumber}
          </h3>
          <p className="text-gray-600 dark:text-gray-300">
            {formatDate(dayPlan.date)}
          </p>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {formatCurrency(dayPlan.dailyCostInr)}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Daily Total
          </div>
        </div>
      </div>

      {/* Weather Information */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{getWeatherIcon(dayPlan.weather.condition)}</span>
            <div>
              <div className="font-semibold text-gray-900 dark:text-white">
                {dayPlan.weather.condition}
              </div>
              {dayPlan.weather.description && (
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  {dayPlan.weather.description}
                </div>
              )}
            </div>
          </div>
          
          <div className="text-right">
            {dayPlan.weather.temperatureHigh && dayPlan.weather.temperatureLow && (
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {Math.round(dayPlan.weather.temperatureHigh)}° / {Math.round(dayPlan.weather.temperatureLow)}°
              </div>
            )}
            <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
              {dayPlan.weather.humidity && (
                <span>💧 {dayPlan.weather.humidity}%</span>
              )}
              {dayPlan.weather.precipitationChance && (
                <span>🌧️ {dayPlan.weather.precipitationChance}%</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Activities */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
          Activities ({dayPlan.activities.length})
        </h4>
        {dayPlan.activities.map((activity, index) => (
          <ActivityCard key={index} activity={activity} />
        ))}
      </div>

      {/* Notes */}
      {dayPlan.notes && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <strong>Notes:</strong> {dayPlan.notes}
          </div>
        </div>
      )}
    </div>
  );
};

const ItineraryDisplay: React.FC<ItineraryDisplayProps> = ({ itinerary, className = '' }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getTotalDuration = () => {
    return itinerary.days.reduce((total, day) => {
      return total + day.activities.reduce((dayTotal, activity) => dayTotal + activity.durationHours, 0);
    }, 0);
  };

  const getTotalActivities = () => {
    return itinerary.days.reduce((total, day) => total + day.activities.length, 0);
  };

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      {/* Itinerary Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 mb-6 shadow-lg">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Your Trip Itinerary
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {itinerary.days.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">Days</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {getTotalActivities()}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">Activities</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {Math.round(getTotalDuration())}h
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">Total Duration</div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {formatCurrency(itinerary.totalCostInr)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-300">Total Cost</div>
          </div>
        </div>
      </div>

      {/* Day Plans */}
      <div>
        {itinerary.days.map((dayPlan) => (
          <DayPlanCard key={dayPlan.dayNumber} dayPlan={dayPlan} />
        ))}
      </div>
    </div>
  );
};

export default ItineraryDisplay;