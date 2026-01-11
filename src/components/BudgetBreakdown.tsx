'use client';

import React, { useState } from 'react';
import { TripItinerary, ActivityCategory, TransportType } from '../types';

interface BudgetBreakdownProps {
  itinerary: TripItinerary;
}

interface CategoryBreakdown {
  category: string;
  amount: number;
  percentage: number;
  icon: string;
  color: string;
}

interface DayBreakdown {
  day: number;
  amount: number;
  activities: number;
  transport: number;
}

export const BudgetBreakdown: React.FC<BudgetBreakdownProps> = ({ itinerary }) => {
  const [activeView, setActiveView] = useState<'category' | 'daily' | 'transport'>('category');

  // Calculate category-wise breakdown
  const calculateCategoryBreakdown = (): CategoryBreakdown[] => {
    const categoryTotals: Record<string, number> = {};
    
    // Sum up activities by category
    itinerary.daily_plans.forEach(day => {
      day.activities.forEach(activity => {
        categoryTotals[activity.category] = (categoryTotals[activity.category] || 0) + activity.cost;
      });
    });

    // Sum up transport costs
    const transportTotal = itinerary.daily_plans.reduce((total, day) => {
      return total + day.transport.reduce((dayTotal, transport) => dayTotal + transport.cost, 0);
    }, 0);

    if (transportTotal > 0) {
      categoryTotals['transport'] = transportTotal;
    }

    const total = itinerary.total_budget;
    
    const categoryConfig: Record<string, { icon: string; color: string; label: string }> = {
      sightseeing: { icon: '🏛️', color: 'bg-blue-500', label: 'Sightseeing' },
      dining: { icon: '🍽️', color: 'bg-green-500', label: 'Dining' },
      entertainment: { icon: '🎭', color: 'bg-purple-500', label: 'Entertainment' },
      cultural: { icon: '🎨', color: 'bg-orange-500', label: 'Cultural' },
      transport: { icon: '🚗', color: 'bg-gray-500', label: 'Transportation' },
    };

    return Object.entries(categoryTotals)
      .map(([category, amount]) => ({
        category: categoryConfig[category]?.label || category,
        amount,
        percentage: total > 0 ? (amount / total) * 100 : 0,
        icon: categoryConfig[category]?.icon || '📍',
        color: categoryConfig[category]?.color || 'bg-gray-400',
      }))
      .sort((a, b) => b.amount - a.amount);
  };

  // Calculate daily breakdown
  const calculateDailyBreakdown = (): DayBreakdown[] => {
    return itinerary.daily_plans.map(day => {
      const activitiesCost = day.activities.reduce((sum, activity) => sum + activity.cost, 0);
      const transportCost = day.transport.reduce((sum, transport) => sum + transport.cost, 0);
      
      return {
        day: day.day_number,
        amount: day.estimated_cost,
        activities: activitiesCost,
        transport: transportCost,
      };
    });
  };

  // Calculate transport type breakdown
  const calculateTransportBreakdown = (): CategoryBreakdown[] => {
    const transportTotals: Record<string, number> = {};
    
    itinerary.daily_plans.forEach(day => {
      day.transport.forEach(transport => {
        transportTotals[transport.type] = (transportTotals[transport.type] || 0) + transport.cost;
      });
    });

    const total = Object.values(transportTotals).reduce((sum, amount) => sum + amount, 0);
    
    const transportConfig: Record<string, { icon: string; color: string }> = {
      flight: { icon: '✈️', color: 'bg-blue-600' },
      taxi: { icon: '🚕', color: 'bg-yellow-500' },
      bus: { icon: '🚌', color: 'bg-green-600' },
      metro: { icon: '🚇', color: 'bg-red-500' },
      walking: { icon: '🚶', color: 'bg-gray-400' },
    };

    return Object.entries(transportTotals)
      .map(([type, amount]) => ({
        category: type.charAt(0).toUpperCase() + type.slice(1),
        amount,
        percentage: total > 0 ? (amount / total) * 100 : 0,
        icon: transportConfig[type]?.icon || '🚗',
        color: transportConfig[type]?.color || 'bg-gray-400',
      }))
      .sort((a, b) => b.amount - a.amount);
  };

  const categoryBreakdown = calculateCategoryBreakdown();
  const dailyBreakdown = calculateDailyBreakdown();
  const transportBreakdown = calculateTransportBreakdown();

  const ProgressBar: React.FC<{ percentage: number; color: string }> = ({ percentage, color }) => (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full ${color} transition-all duration-300`}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  );

  const CategoryView = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending by Category</h3>
      {categoryBreakdown.map((item, index) => (
        <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium text-gray-900">{item.category}</span>
            </div>
            <div className="text-right">
              <span className="font-semibold text-gray-900">${item.amount.toFixed(2)}</span>
              <span className="text-sm text-gray-500 ml-2">({item.percentage.toFixed(1)}%)</span>
            </div>
          </div>
          <ProgressBar percentage={item.percentage} color={item.color} />
        </div>
      ))}
    </div>
  );

  const DailyView = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Spending</h3>
      {dailyBreakdown.map((day, index) => (
        <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">Day {day.day}</h4>
            <span className="font-semibold text-gray-900">${day.amount.toFixed(2)}</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Activities</span>
              <span className="text-gray-900">${day.activities.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Transportation</span>
              <span className="text-gray-900">${day.transport.toFixed(2)}</span>
            </div>
          </div>
          <div className="mt-2">
            <ProgressBar 
              percentage={(day.amount / itinerary.total_budget) * 100} 
              color="bg-blue-500" 
            />
          </div>
        </div>
      ))}
    </div>
  );

  const TransportView = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Transportation Costs</h3>
      {transportBreakdown.length > 0 ? (
        transportBreakdown.map((item, index) => (
          <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium text-gray-900">{item.category}</span>
              </div>
              <div className="text-right">
                <span className="font-semibold text-gray-900">${item.amount.toFixed(2)}</span>
                <span className="text-sm text-gray-500 ml-2">({item.percentage.toFixed(1)}%)</span>
              </div>
            </div>
            <ProgressBar percentage={item.percentage} color={item.color} />
          </div>
        ))
      ) : (
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <p className="text-gray-500">No transportation costs found</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header with Total */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Budget Breakdown</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-100">Total Estimated Cost</p>
            <p className="text-3xl font-bold">${itinerary.total_budget.toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-blue-100">{itinerary.total_days} Days</p>
            <p className="text-xl font-semibold">
              ${(itinerary.total_budget / itinerary.total_days).toFixed(2)}/day
            </p>
          </div>
        </div>
      </div>

      {/* View Toggle */}
      <div className="flex bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveView('category')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'category'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          By Category
        </button>
        <button
          onClick={() => setActiveView('daily')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'daily'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          By Day
        </button>
        <button
          onClick={() => setActiveView('transport')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'transport'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Transport
        </button>
      </div>

      {/* Content */}
      <div>
        {activeView === 'category' && <CategoryView />}
        {activeView === 'daily' && <DailyView />}
        {activeView === 'transport' && <TransportView />}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-blue-600">
            {itinerary.daily_plans.reduce((total, day) => total + day.activities.length, 0)}
          </p>
          <p className="text-sm text-gray-600">Total Activities</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-green-600">
            ${(itinerary.total_budget / itinerary.total_days).toFixed(0)}
          </p>
          <p className="text-sm text-gray-600">Avg. Daily Cost</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-purple-600">
            {categoryBreakdown.length}
          </p>
          <p className="text-sm text-gray-600">Categories</p>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200 text-center">
          <p className="text-2xl font-bold text-orange-600">
            {transportBreakdown.reduce((sum, item) => sum + item.amount, 0).toFixed(0)}
          </p>
          <p className="text-sm text-gray-600">Transport Cost</p>
        </div>
      </div>
    </div>
  );
};

export default BudgetBreakdown;