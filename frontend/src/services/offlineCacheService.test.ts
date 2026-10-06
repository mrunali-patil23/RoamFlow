/**
 * Property-based tests for offline cache service functionality.
 * 
 * These tests verify that offline data availability and caching operations
 * maintain data integrity and correctness across all valid inputs.
 */

import { offlineCacheService, TripPlan, CachedTripPlan } from './offlineCacheService';
import { TripPreferences, TravelType, BudgetLevel, Interest } from '../types/trip';
import { vi } from 'vitest';

// Mock localStorage for testing
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock navigator.onLine with proper getter/setter
let mockOnlineStatus = true;
Object.defineProperty(navigator, 'onLine', {
  get: () => mockOnlineStatus,
  set: (value) => { mockOnlineStatus = value; },
  configurable: true
});

// Mock window event listeners for online/offline events
const mockEventListeners: { [key: string]: EventListener[] } = {};
const originalAddEventListener = window.addEventListener;
const originalRemoveEventListener = window.removeEventListener;

window.addEventListener = vi.fn((event: string, listener: EventListener) => {
  if (!mockEventListeners[event]) {
    mockEventListeners[event] = [];
  }
  mockEventListeners[event].push(listener);
});

window.removeEventListener = vi.fn((event: string, listener: EventListener) => {
  if (mockEventListeners[event]) {
    const index = mockEventListeners[event].indexOf(listener);
    if (index > -1) {
      mockEventListeners[event].splice(index, 1);
    }
  }
});

// Helper function to trigger online/offline events
const triggerOnlineEvent = () => {
  mockOnlineStatus = true;
  if (mockEventListeners['online']) {
    mockEventListeners['online'].forEach(listener => listener(new Event('online')));
  }
};

const triggerOfflineEvent = () => {
  mockOnlineStatus = false;
  if (mockEventListeners['offline']) {
    mockEventListeners['offline'].forEach(listener => listener(new Event('offline')));
  }
};

// Test data generators
const generateTripPreferences = (): TripPreferences => {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() + Math.floor(Math.random() * 30) + 1);
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + Math.floor(Math.random() * 14) + 1);

  const destinations = ['Paris', 'Tokyo', 'New York', 'London', 'Mumbai', 'Sydney', 'Dubai'];
  const travelTypes = Object.values(TravelType);
  const budgetLevels = Object.values(BudgetLevel);
  const allInterests = Object.values(Interest);

  return {
    destination: destinations[Math.floor(Math.random() * destinations.length)],
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
    travelDays: Math.floor(Math.random() * 14) + 1,
    travelType: travelTypes[Math.floor(Math.random() * travelTypes.length)],
    budgetPreference: budgetLevels[Math.floor(Math.random() * budgetLevels.length)],
    maxBudgetInr: Math.floor(Math.random() * 100000) + 10000,
    interests: allInterests.slice(0, Math.floor(Math.random() * allInterests.length) + 1)
  };
};

const generateTripPlan = (): TripPlan => {
  const preferences = generateTripPreferences();
  const tripId = `trip_${Math.random().toString(36).substr(2, 9)}`;
  const userId = `user_${Math.random().toString(36).substr(2, 9)}`;

  return {
    id: tripId,
    userId: userId,
    preferences: preferences,
    itinerary: {
      tripId: tripId,
      days: [],
      totalCostInr: Math.floor(Math.random() * 50000) + 5000,
      createdAt: new Date().toISOString()
    },
    costBreakdown: {
      flightCostInr: Math.floor(Math.random() * 20000) + 5000,
      hotelCostInr: Math.floor(Math.random() * 15000) + 3000,
      attractionsCostInr: Math.floor(Math.random() * 5000) + 1000,
      eventsCostInr: Math.floor(Math.random() * 3000) + 500,
      localExpensesInr: Math.floor(Math.random() * 7000) + 2000,
      totalCostInr: Math.floor(Math.random() * 50000) + 5000
    },
    budgetStatus: {
      status: 'Within Budget',
      differenceInr: Math.floor(Math.random() * 10000) - 5000,
      suggestions: []
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
};

describe('Offline Cache Service Property Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorageMock.clear();
    
    // Reset navigator.onLine to true
    mockOnlineStatus = true;
    
    // Clear event listeners
    Object.keys(mockEventListeners).forEach(key => {
      mockEventListeners[key] = [];
    });
    
    // Trigger online event to ensure service starts in online state
    triggerOnlineEvent();
  });

  afterEach(() => {
    // Restore original event listeners
    window.addEventListener = originalAddEventListener;
    window.removeEventListener = originalRemoveEventListener;
  });

  /**
   * Feature: ai-trip-planner, Property 22: Offline Data Availability
   * For any offline scenario, the last generated itinerary should be accessible from local cache
   * **Validates: Requirements 7.4**
   */
  describe('Property 22: Offline Data Availability', () => {
    const runPropertyTest = (iterations: number = 100) => {
      for (let i = 0; i < iterations; i++) {
        // Generate random trip data
        const tripPlan = generateTripPlan();
        const preferences = generateTripPreferences();

        // Test caching when online
        (offlineCacheService as any)._setOnlineStatusForTesting(true);
        
        // Cache the trip plan
        offlineCacheService.cacheLastItinerary(tripPlan, preferences);
        
        // Verify data is cached
        const cachedData = offlineCacheService.getLastCachedItinerary();
        expect(cachedData).not.toBeNull();
        expect(cachedData!.tripPlan.id).toBe(tripPlan.id);
        expect(cachedData!.preferences.destination).toBe(preferences.destination);
        
        // Simulate going offline
        (offlineCacheService as any)._setOnlineStatusForTesting(false);
        
        // Verify service detects offline status
        expect(offlineCacheService.isOnline()).toBe(false);
        
        // Verify data is still accessible offline
        const offlineCachedData = offlineCacheService.getLastCachedItinerary();
        expect(offlineCachedData).not.toBeNull();
        expect(offlineCachedData!.tripPlan.id).toBe(tripPlan.id);
        expect(offlineCachedData!.preferences.destination).toBe(preferences.destination);
        
        // Verify offline status indicates cached data is available
        const offlineStatus = offlineCacheService.getOfflineStatus();
        expect(offlineStatus.isOffline).toBe(true);
        expect(offlineStatus.hasCachedData).toBe(true);
        
        // Verify cache info reflects available data
        const cacheInfo = offlineCacheService.getCacheInfo();
        expect(cacheInfo.hasLastItinerary).toBe(true);
        expect(cacheInfo.isExpired).toBe(false);
        
        // Clean up for next iteration
        offlineCacheService.clearLastCachedItinerary();
        
        // Reset to online state for next iteration
        (offlineCacheService as any)._setOnlineStatusForTesting(true);
      }
    };

    test('should maintain data integrity across online/offline transitions', () => {
      runPropertyTest(100);
    });

    test('should preserve all trip plan components in cache', () => {
      for (let i = 0; i < 50; i++) {
        const tripPlan = generateTripPlan();
        const preferences = generateTripPreferences();

        // Cache the data
        offlineCacheService.cacheLastItinerary(tripPlan, preferences);
        
        // Retrieve and verify all components are preserved
        const cached = offlineCacheService.getLastCachedItinerary();
        expect(cached).not.toBeNull();
        
        // Verify trip plan structure
        expect(cached!.tripPlan).toMatchObject({
          id: tripPlan.id,
          userId: tripPlan.userId,
          preferences: expect.objectContaining({
            destination: tripPlan.preferences.destination,
            travelDays: tripPlan.preferences.travelDays,
            travelType: tripPlan.preferences.travelType,
            budgetPreference: tripPlan.preferences.budgetPreference,
            maxBudgetInr: tripPlan.preferences.maxBudgetInr
          }),
          itinerary: expect.objectContaining({
            tripId: tripPlan.itinerary.tripId,
            totalCostInr: tripPlan.itinerary.totalCostInr
          }),
          costBreakdown: expect.objectContaining({
            flightCostInr: tripPlan.costBreakdown.flightCostInr,
            hotelCostInr: tripPlan.costBreakdown.hotelCostInr,
            attractionsCostInr: tripPlan.costBreakdown.attractionsCostInr,
            eventsCostInr: tripPlan.costBreakdown.eventsCostInr,
            localExpensesInr: tripPlan.costBreakdown.localExpensesInr,
            totalCostInr: tripPlan.costBreakdown.totalCostInr
          }),
          budgetStatus: expect.objectContaining({
            status: tripPlan.budgetStatus.status,
            differenceInr: tripPlan.budgetStatus.differenceInr
          })
        });

        // Verify preferences structure
        expect(cached!.preferences).toMatchObject({
          destination: preferences.destination,
          startDate: preferences.startDate,
          endDate: preferences.endDate,
          travelDays: preferences.travelDays,
          travelType: preferences.travelType,
          budgetPreference: preferences.budgetPreference,
          maxBudgetInr: preferences.maxBudgetInr,
          interests: preferences.interests
        });

        // Verify timestamp is recent
        expect(cached!.timestamp).toBeGreaterThan(Date.now() - 5000); // Within last 5 seconds
        
        offlineCacheService.clearLastCachedItinerary();
      }
    });

    test('should handle multiple trip plans caching correctly', () => {
      for (let i = 0; i < 30; i++) {
        const tripPlans = Array.from({ length: Math.floor(Math.random() * 5) + 1 }, generateTripPlan);
        
        // Start online
        (offlineCacheService as any)._setOnlineStatusForTesting(true);
        
        // Cache multiple trip plans
        offlineCacheService.cacheTripPlans(tripPlans);
        
        // Simulate offline mode
        (offlineCacheService as any)._setOnlineStatusForTesting(false);
        
        // Verify service detects offline status
        expect(offlineCacheService.isOnline()).toBe(false);
        
        // Verify all plans are accessible offline
        const cachedPlans = offlineCacheService.getCachedTripPlans();
        expect(cachedPlans).toHaveLength(tripPlans.length);
        
        // Verify each plan is correctly cached
        for (let j = 0; j < tripPlans.length; j++) {
          const original = tripPlans[j];
          const cached = cachedPlans.find(plan => plan.id === original.id);
          
          expect(cached).toBeDefined();
          expect(cached!.id).toBe(original.id);
          expect(cached!.userId).toBe(original.userId);
          expect(cached!.preferences.destination).toBe(original.preferences.destination);
          expect(cached!.costBreakdown.totalCostInr).toBe(original.costBreakdown.totalCostInr);
        }
        
        // Verify offline status reflects cached data
        const offlineStatus = offlineCacheService.getOfflineStatus();
        expect(offlineStatus.isOffline).toBe(true);
        expect(offlineStatus.hasCachedData).toBe(true);
        
        const cacheInfo = offlineCacheService.getCacheInfo();
        expect(cacheInfo.cachedPlansCount).toBe(tripPlans.length);
        
        offlineCacheService.clearCachedTripPlans();
        
        // Reset to online for next iteration
        (offlineCacheService as any)._setOnlineStatusForTesting(true);
      }
    });

    test('should handle cache expiration correctly', () => {
      const tripPlan = generateTripPlan();
      const preferences = generateTripPreferences();
      
      // Start online
      (offlineCacheService as any)._setOnlineStatusForTesting(true);
      
      // Cache data
      offlineCacheService.cacheLastItinerary(tripPlan, preferences);
      
      // Verify data is initially available
      expect(offlineCacheService.getLastCachedItinerary()).not.toBeNull();
      expect(offlineCacheService.getCacheInfo().isExpired).toBe(false);
      
      // Mock expired timestamp (25 hours ago)
      const expiredTimestamp = Date.now() - (25 * 60 * 60 * 1000);
      const expiredData = {
        tripPlan,
        preferences,
        timestamp: expiredTimestamp
      };
      
      localStorage.setItem('ai_trip_planner_last_itinerary', JSON.stringify(expiredData));
      localStorage.setItem('ai_trip_planner_cache_timestamp', expiredTimestamp.toString());
      
      // Verify expired cache is handled correctly
      const cacheInfoBeforeCheck = offlineCacheService.getCacheInfo();
      expect(cacheInfoBeforeCheck.isExpired).toBe(true);
      
      expect(offlineCacheService.getLastCachedItinerary()).toBeNull();
      
      // Verify offline status reflects no available data when expired
      (offlineCacheService as any)._setOnlineStatusForTesting(false);
      expect(offlineCacheService.isOnline()).toBe(false);
      const offlineStatus = offlineCacheService.getOfflineStatus();
      expect(offlineStatus.isOffline).toBe(true);
      expect(offlineStatus.hasCachedData).toBe(false);
    });

    test('should maintain data consistency across cache operations', () => {
      for (let i = 0; i < 25; i++) {
        const tripPlan = generateTripPlan();
        const preferences = generateTripPreferences();
        
        // Perform multiple cache operations
        offlineCacheService.cacheLastItinerary(tripPlan, preferences);
        
        // Verify consistency after each operation
        let cached = offlineCacheService.getLastCachedItinerary();
        expect(cached).not.toBeNull();
        expect(cached!.tripPlan.id).toBe(tripPlan.id);
        
        // Cache additional trip plans
        const additionalPlans = [generateTripPlan(), generateTripPlan()];
        offlineCacheService.cacheTripPlans(additionalPlans);
        
        // Verify last itinerary is still available
        cached = offlineCacheService.getLastCachedItinerary();
        expect(cached).not.toBeNull();
        expect(cached!.tripPlan.id).toBe(tripPlan.id);
        
        // Verify additional plans are cached
        const cachedPlans = offlineCacheService.getCachedTripPlans();
        expect(cachedPlans).toHaveLength(additionalPlans.length);
        
        // Clear specific cache and verify others remain
        offlineCacheService.clearCachedTripPlans();
        expect(offlineCacheService.getCachedTripPlans()).toHaveLength(0);
        expect(offlineCacheService.getLastCachedItinerary()).not.toBeNull();
        
        offlineCacheService.clearAllCache();
      }
    });
  });
});