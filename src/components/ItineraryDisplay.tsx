'use client';

import React, { useState } from 'react';
import { TripItinerary, DayPlan, Activity, TransportOption } from '../types';

interface ItineraryDisplayProps {
  itinerary: TripItinerary;
}

interface DayCardProps {
  dayPlan: DayPlan;
  isExpanded: boolean;
  onToggle: () => void;
}

const ActivityCard: React.FC<{ activity: Activity }> = ({ activity }) => {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'sightseeing':
        return '🏛️';
      case 'dining':
        return '🍽️';
      case 'entertainment':
        return '🎭';
      case 'cultural':
        return '🎨';
      default:
        return '📍';
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
    return `${mins}m`;
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getCategoryIcon(activity.category)}</span>
            <h4 className="font-semibold text-gray-900">{activity.name}</h4>
          </div>
          <p className="text-gray-600 text-sm mb-2">{activity.description}</p>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>⏱️ {formatDuration(activity.duration)}</span>
            <span>💰 ${activity.cost.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const TransportCard: React.FC<{ transport: TransportOption }> = ({ transport }) => {
  const getTransportIcon = (type: string) => {
    switch (type) {
      case 'flight':
        return '✈️';
      case 'taxi':
        return '🚕';
      case 'bus':
        return '🚌';
      case 'metro':
        return '🚇';
      case 'walking':
        return '🚶';
      default:
        return '🚗';
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
    return `${mins}m`;
  };

  return (
    <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{getTransportIcon(transport.type)}</span>
          <div>
            <p className="font-medium text-gray-900 capitalize">{transport.type}</p>
            <p className="text-sm text-gray-600">{transport.provider}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="font-semibold text-gray-900">${transport.cost.toFixed(2)}</p>
          <p className="text-sm text-gray-500">{formatDuration(transport.duration)}</p>
        </div>
      </div>
      {transport.route && (
        <p className="text-sm text-gray-600 mt-2">{transport.route}</p>
      )}
    </div>
  );
};

const DayCard: React.FC<DayCardProps> = ({ dayPlan, isExpanded, onToggle }) => {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Day {dayPlan.day_number}
            </h3>
            <p className="text-sm text-gray-600">
              {dayPlan.activities.length} activities • ${dayPlan.estimated_cost.toFixed(2)} estimated
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-blue-600">
              ${dayPlan.estimated_cost.toFixed(2)}
            </span>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </button>

      {isExpanded && (
        <div className="px-6 pb-6">
          <div className="border-t border-gray-200 pt-4">
            {/* Activities Section */}
            {dayPlan.activities.length > 0 && (
              <div className="mb-6">
                <h4 className="text-md font-semibold text-gray-900 mb-3">Activities</h4>
                <div className="space-y-3">
                  {dayPlan.activities.map((activity, index) => (
                    <ActivityCard key={index} activity={activity} />
                  ))}
                </div>
              </div>
            )}

            {/* Transport Section */}
            {dayPlan.transport.length > 0 && (
              <div>
                <h4 className="text-md font-semibold text-gray-900 mb-3">Transportation</h4>
                <div className="space-y-2">
                  {dayPlan.transport.map((transport, index) => (
                    <TransportCard key={index} transport={transport} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const ItineraryDisplay: React.FC<ItineraryDisplayProps> = ({ itinerary }) => {
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1])); // Expand first day by default

  const toggleDay = (dayNumber: number) => {
    setExpandedDays(prev => {
      const newSet = new Set(prev);
      if (newSet.has(dayNumber)) {
        newSet.delete(dayNumber);
      } else {
        newSet.add(dayNumber);
      }
      return newSet;
    });
  };

  const expandAll = () => {
    setExpandedDays(new Set(itinerary.daily_plans.map(day => day.day_number)));
  };

  const collapseAll = () => {
    setExpandedDays(new Set());
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{itinerary.destination}</h2>
          <p className="text-gray-600">
            {itinerary.total_days} day{itinerary.total_days !== 1 ? 's' : ''} • 
            Total Budget: ${itinerary.total_budget.toFixed(2)}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={expandAll}
            className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-md transition-colors"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Day Plans */}
      <div className="space-y-4">
        {itinerary.daily_plans.map((dayPlan) => (
          <DayCard
            key={dayPlan.day_number}
            dayPlan={dayPlan}
            isExpanded={expandedDays.has(dayPlan.day_number)}
            onToggle={() => toggleDay(dayPlan.day_number)}
          />
        ))}
      </div>

      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Trip Summary</h3>
            <p className="text-sm text-gray-600">
              {itinerary.daily_plans.reduce((total, day) => total + day.activities.length, 0)} total activities
            </p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-gray-900">${itinerary.total_budget.toFixed(2)}</p>
            <p className="text-sm text-gray-600">Total estimated cost</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ItineraryDisplay;