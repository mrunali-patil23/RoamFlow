'use client';

import React, { useState, useEffect, useRef } from 'react';
import { TripItinerary, DayPlan, Activity } from '../types';

interface MapVisualizationProps {
  itinerary: TripItinerary;
}

interface LocationPoint {
  id: string;
  name: string;
  day: number;
  type: 'activity' | 'transport' | 'destination';
  coordinates?: [number, number]; // [lat, lng]
  description?: string;
}

// Mock coordinates for demonstration - in a real app, these would come from geocoding
const getMockCoordinates = (locationName: string): [number, number] => {
  // Simple hash function to generate consistent coordinates for demo
  let hash = 0;
  for (let i = 0; i < locationName.length; i++) {
    const char = locationName.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Generate coordinates within a reasonable range (e.g., around a city center)
  const lat = 40.7128 + (hash % 1000) / 10000; // Around NYC latitude
  const lng = -74.0060 + ((hash >> 10) % 1000) / 10000; // Around NYC longitude
  
  return [lat, lng];
};

const StaticMapView: React.FC<{ locations: LocationPoint[] }> = ({ locations }) => {
  const [selectedLocation, setSelectedLocation] = useState<LocationPoint | null>(null);

  const getDayColor = (day: number) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-orange-500',
      'bg-red-500',
      'bg-indigo-500',
      'bg-pink-500',
      'bg-yellow-500',
    ];
    return colors[(day - 1) % colors.length];
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'activity':
        return '📍';
      case 'transport':
        return '🚗';
      case 'destination':
        return '🏛️';
      default:
        return '📍';
    }
  };

  return (
    <div className="bg-gray-100 rounded-lg p-6 min-h-[400px] relative">
      {/* Map Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Route Visualization</h3>
        <p className="text-sm text-gray-600">
          Interactive map showing your planned activities and routes
        </p>
      </div>

      {/* Static Map Representation */}
      <div className="bg-white rounded-lg border-2 border-gray-200 h-80 relative overflow-hidden">
        {/* Map Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <svg width="100%" height="100%" className="text-gray-300">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* Location Markers */}
        <div className="absolute inset-0 p-4">
          {locations.map((location, index) => {
            const x = 10 + (index % 6) * 15; // Distribute horizontally
            const y = 15 + Math.floor(index / 6) * 20; // Stack vertically
            
            return (
              <div
                key={location.id}
                className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-1/2"
                style={{ left: `${x}%`, top: `${y}%` }}
                onClick={() => setSelectedLocation(location)}
              >
                <div className={`w-8 h-8 rounded-full ${getDayColor(location.day)} flex items-center justify-center text-white text-xs font-bold shadow-lg hover:scale-110 transition-transform`}>
                  {location.day}
                </div>
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1">
                  <span className="text-xs bg-white px-1 py-0.5 rounded shadow text-gray-700 whitespace-nowrap">
                    {location.name.length > 15 ? location.name.substring(0, 15) + '...' : location.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Route Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {locations.slice(0, -1).map((_, index) => {
            const x1 = 10 + (index % 6) * 15;
            const y1 = 15 + Math.floor(index / 6) * 20;
            const x2 = 10 + ((index + 1) % 6) * 15;
            const y2 = 15 + Math.floor((index + 1) / 6) * 20;
            
            return (
              <line
                key={index}
                x1={`${x1}%`}
                y1={`${y1}%`}
                x2={`${x2}%`}
                y2={`${y2}%`}
                stroke="#3B82F6"
                strokeWidth="2"
                strokeDasharray="5,5"
                opacity="0.6"
              />
            );
          })}
        </svg>

        {/* Map Controls */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-md p-2">
          <div className="flex flex-col gap-1">
            <button className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded flex items-center justify-center text-gray-600">
              +
            </button>
            <button className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded flex items-center justify-center text-gray-600">
              −
            </button>
          </div>
        </div>
      </div>

      {/* Location Details Panel */}
      {selectedLocation && (
        <div className="mt-4 bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{getTypeIcon(selectedLocation.type)}</span>
                <h4 className="font-semibold text-gray-900">{selectedLocation.name}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${getDayColor(selectedLocation.day)}`}>
                  Day {selectedLocation.day}
                </span>
              </div>
              {selectedLocation.description && (
                <p className="text-gray-600 text-sm">{selectedLocation.description}</p>
              )}
            </div>
            <button
              onClick={() => setSelectedLocation(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
          <span className="text-sm text-gray-600">Activities</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-blue-500 opacity-60"></div>
          <span className="text-sm text-gray-600">Route</span>
        </div>
      </div>
    </div>
  );
};

const RouteList: React.FC<{ locations: LocationPoint[] }> = ({ locations }) => {
  const groupedByDay = locations.reduce((acc, location) => {
    if (!acc[location.day]) {
      acc[location.day] = [];
    }
    acc[location.day].push(location);
    return acc;
  }, {} as Record<number, LocationPoint[]>);

  const getDayColor = (day: number) => {
    const colors = [
      'border-blue-500 bg-blue-50',
      'border-green-500 bg-green-50',
      'border-purple-500 bg-purple-50',
      'border-orange-500 bg-orange-50',
      'border-red-500 bg-red-50',
      'border-indigo-500 bg-indigo-50',
      'border-pink-500 bg-pink-50',
      'border-yellow-500 bg-yellow-50',
    ];
    return colors[(day - 1) % colors.length];
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Route Details</h3>
      {Object.entries(groupedByDay)
        .sort(([a], [b]) => parseInt(a) - parseInt(b))
        .map(([day, dayLocations]) => (
          <div key={day} className={`border-l-4 pl-4 ${getDayColor(parseInt(day))}`}>
            <h4 className="font-medium text-gray-900 mb-2">Day {day}</h4>
            <div className="space-y-2">
              {dayLocations.map((location, index) => (
                <div key={location.id} className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-white border-2 border-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{location.name}</p>
                    {location.description && (
                      <p className="text-sm text-gray-600">{location.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
    </div>
  );
};

export const MapVisualization: React.FC<MapVisualizationProps> = ({ itinerary }) => {
  const [activeView, setActiveView] = useState<'map' | 'list'>('map');
  const [locations, setLocations] = useState<LocationPoint[]>([]);

  useEffect(() => {
    // Extract locations from itinerary
    const extractedLocations: LocationPoint[] = [];

    // Add destination as main location
    extractedLocations.push({
      id: 'destination',
      name: itinerary.destination,
      day: 1,
      type: 'destination',
      coordinates: getMockCoordinates(itinerary.destination),
      description: `Main destination: ${itinerary.destination}`,
    });

    // Add activities as locations
    itinerary.daily_plans.forEach((day) => {
      day.activities.forEach((activity, index) => {
        extractedLocations.push({
          id: `activity-${day.day_number}-${index}`,
          name: activity.name,
          day: day.day_number,
          type: 'activity',
          coordinates: getMockCoordinates(activity.name),
          description: activity.description,
        });
      });
    });

    setLocations(extractedLocations);
  }, [itinerary]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Route Map</h2>
          <p className="text-gray-600">
            Visualize your travel route and planned activities
          </p>
        </div>
        
        {/* View Toggle */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveView('map')}
            className={`py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeView === 'map'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Map View
          </button>
          <button
            onClick={() => setActiveView('list')}
            className={`py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeView === 'list'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            List View
          </button>
        </div>
      </div>

      {/* Content */}
      {activeView === 'map' ? (
        <StaticMapView locations={locations} />
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <RouteList locations={locations} />
        </div>
      )}

      {/* Map Integration Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-blue-500 mt-0.5">ℹ️</div>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">Map Integration</h4>
            <p className="text-sm text-blue-800">
              This is a static representation of your route. In a production environment, 
              this would integrate with Google Maps, Leaflet, or another mapping service 
              to provide interactive maps with real coordinates and routing.
            </p>
          </div>
        </div>
      </div>

      {/* Route Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-blue-600">{locations.length}</p>
          <p className="text-sm text-gray-600">Total Locations</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-green-600">{itinerary.total_days}</p>
          <p className="text-sm text-gray-600">Travel Days</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-purple-600">
            {Math.round(locations.length / itinerary.total_days)}
          </p>
          <p className="text-sm text-gray-600">Avg. Stops/Day</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-orange-600">
            {locations.filter(l => l.type === 'activity').length}
          </p>
          <p className="text-sm text-gray-600">Activities</p>
        </div>
      </div>
    </div>
  );
};

export default MapVisualization;