/**
 * Offline cache service for the AI Trip Planner.
 * 
 * This service handles local storage caching for trip plans and provides
 * offline mode detection and fallback functionality.
 */

import { TripPreferences } from '../types/trip';

// Extended interfaces for offline caching
export interface TripPlan {
  id: string;
  userId: string;
  preferences: TripPreferences;
  itinerary: Itinerary;
  costBreakdown: CostBreakdown;
  budgetStatus: BudgetStatus;
  createdAt?: string;
  updatedAt?: string;
}

export interface Itinerary {
  tripId: string;
  days: DayPlan[];
  totalCostInr: number;
  createdAt?: string;
}

export interface DayPlan {
  dayNumber: number;
  date: string; // ISO date string
  activities: Activity[];
  weather: WeatherInfo;
  dailyCostInr: number;
  notes?: string;
}

export interface Activity {
  name: string;
  activityType: string;
  description: string;
  durationHours: number;
  costInr: number;
  location?: string;
  rating?: number;
  startTime?: string;
  endTime?: string;
  bookingRequired: boolean;
  sourceData?: any;
}

export interface WeatherInfo {
  date: string; // ISO date string
  temperatureHigh?: number;
  temperatureLow?: number;
  condition: string;
  description: string;
  humidity?: number;
  precipitationChance?: number;
}

export interface CostBreakdown {
  flightCostInr: number;
  hotelCostInr: number;
  attractionsCostInr: number;
  eventsCostInr: number;
  localExpensesInr: number;
  totalCostInr: number;
  dailyBreakdown?: DailyCost[];
}

export interface DailyCost {
  dayNumber: number;
  date: string;
  flightCostInr: number;
  hotelCostInr: number;
  attractionsCostInr: number;
  eventsCostInr: number;
  localExpensesInr: number;
  totalCostInr: number;
}

export interface BudgetStatus {
  status: string; // "Within Budget", "Slightly Over Budget", "Over Budget"
  differenceInr: number;
  suggestions: string[];
}

const CACHE_KEYS = {
  LAST_GENERATED_ITINERARY: 'ai_trip_planner_last_itinerary',
  OFFLINE_MODE: 'ai_trip_planner_offline_mode',
  CACHED_TRIP_PLANS: 'ai_trip_planner_cached_plans',
  CACHE_TIMESTAMP: 'ai_trip_planner_cache_timestamp'
} as const;

const CACHE_EXPIRY_HOURS = 24; // Cache expires after 24 hours

export interface CachedTripPlan {
  tripPlan: TripPlan;
  timestamp: number;
  preferences: TripPreferences;
}

export interface OfflineStatus {
  isOffline: boolean;
  lastOnlineTime?: number;
  hasCachedData: boolean;
}

class OfflineCacheService {
  private isOnlineStatus: boolean = navigator.onLine;
  private onlineStatusListeners: ((isOnline: boolean) => void)[] = [];

  constructor() {
    this.initializeOnlineStatusListener();
  }

  /**
   * Initialize online/offline status detection
   */
  private initializeOnlineStatusListener(): void {
    window.addEventListener('online', () => {
      this.isOnlineStatus = true;
      this.clearOfflineMode();
      this.notifyOnlineStatusChange(true);
    });

    window.addEventListener('offline', () => {
      this.isOnlineStatus = false;
      this.setOfflineMode();
      this.notifyOnlineStatusChange(false);
    });
  }

  /**
   * Add listener for online status changes
   */
  addOnlineStatusListener(callback: (isOnline: boolean) => void): void {
    this.onlineStatusListeners.push(callback);
  }

  /**
   * Remove listener for online status changes
   */
  removeOnlineStatusListener(callback: (isOnline: boolean) => void): void {
    this.onlineStatusListeners = this.onlineStatusListeners.filter(
      listener => listener !== callback
    );
  }

  /**
   * Notify all listeners of online status change
   */
  private notifyOnlineStatusChange(isOnline: boolean): void {
    this.onlineStatusListeners.forEach(callback => callback(isOnline));
  }

  /**
   * Check if the application is currently online
   */
  isOnline(): boolean {
    return this.isOnlineStatus;
  }

  /**
   * FOR TESTING ONLY: Manually set online/offline status
   * This method should only be used in test environments
   */
  _setOnlineStatusForTesting(isOnline: boolean): void {
    if (process.env.NODE_ENV !== 'test' && process.env.VITEST !== 'true') {
      console.warn('_setOnlineStatusForTesting should only be used in tests');
      return;
    }
    
    this.isOnlineStatus = isOnline;
    if (isOnline) {
      this.clearOfflineMode();
    } else {
      this.setOfflineMode();
    }
    this.notifyOnlineStatusChange(isOnline);
  }

  /**
   * Get current offline status with cache information
   */
  getOfflineStatus(): OfflineStatus {
    const hasCachedData = this.hasValidCachedData();
    const lastOnlineTime = this.getLastOnlineTime();

    return {
      isOffline: !this.isOnlineStatus,
      lastOnlineTime,
      hasCachedData
    };
  }

  /**
   * Cache the last generated itinerary
   */
  cacheLastItinerary(tripPlan: TripPlan, preferences: TripPreferences): void {
    try {
      const cachedData: CachedTripPlan = {
        tripPlan,
        preferences,
        timestamp: Date.now()
      };

      localStorage.setItem(
        CACHE_KEYS.LAST_GENERATED_ITINERARY,
        JSON.stringify(cachedData)
      );

      localStorage.setItem(
        CACHE_KEYS.CACHE_TIMESTAMP,
        Date.now().toString()
      );

      console.log('Trip plan cached successfully for offline access');
    } catch (error) {
      console.error('Failed to cache trip plan:', error);
    }
  }

  /**
   * Get the last cached itinerary
   */
  getLastCachedItinerary(): CachedTripPlan | null {
    try {
      const cachedData = localStorage.getItem(CACHE_KEYS.LAST_GENERATED_ITINERARY);
      
      if (!cachedData) {
        return null;
      }

      const parsed: CachedTripPlan = JSON.parse(cachedData);
      
      // Check if cache is still valid
      if (this.isCacheExpired(parsed.timestamp)) {
        this.clearLastCachedItinerary();
        return null;
      }

      return parsed;
    } catch (error) {
      console.error('Failed to retrieve cached trip plan:', error);
      return null;
    }
  }

  /**
   * Clear the last cached itinerary
   */
  clearLastCachedItinerary(): void {
    try {
      localStorage.removeItem(CACHE_KEYS.LAST_GENERATED_ITINERARY);
      localStorage.removeItem(CACHE_KEYS.CACHE_TIMESTAMP);
    } catch (error) {
      console.error('Failed to clear cached trip plan:', error);
    }
  }

  /**
   * Cache multiple trip plans for offline access
   */
  cacheTripPlans(tripPlans: TripPlan[]): void {
    try {
      const cachedPlans = {
        plans: tripPlans,
        timestamp: Date.now()
      };

      localStorage.setItem(
        CACHE_KEYS.CACHED_TRIP_PLANS,
        JSON.stringify(cachedPlans)
      );

      console.log(`Cached ${tripPlans.length} trip plans for offline access`);
    } catch (error) {
      console.error('Failed to cache trip plans:', error);
    }
  }

  /**
   * Get cached trip plans
   */
  getCachedTripPlans(): TripPlan[] {
    try {
      const cachedData = localStorage.getItem(CACHE_KEYS.CACHED_TRIP_PLANS);
      
      if (!cachedData) {
        return [];
      }

      const parsed = JSON.parse(cachedData);
      
      // Check if cache is still valid
      if (this.isCacheExpired(parsed.timestamp)) {
        this.clearCachedTripPlans();
        return [];
      }

      return parsed.plans || [];
    } catch (error) {
      console.error('Failed to retrieve cached trip plans:', error);
      return [];
    }
  }

  /**
   * Clear cached trip plans
   */
  clearCachedTripPlans(): void {
    try {
      localStorage.removeItem(CACHE_KEYS.CACHED_TRIP_PLANS);
    } catch (error) {
      console.error('Failed to clear cached trip plans:', error);
    }
  }

  /**
   * Set offline mode flag
   */
  private setOfflineMode(): void {
    try {
      localStorage.setItem(CACHE_KEYS.OFFLINE_MODE, Date.now().toString());
    } catch (error) {
      console.error('Failed to set offline mode:', error);
    }
  }

  /**
   * Clear offline mode flag
   */
  private clearOfflineMode(): void {
    try {
      localStorage.removeItem(CACHE_KEYS.OFFLINE_MODE);
    } catch (error) {
      console.error('Failed to clear offline mode:', error);
    }
  }

  /**
   * Get the last time the application was online
   */
  private getLastOnlineTime(): number | undefined {
    try {
      const offlineTime = localStorage.getItem(CACHE_KEYS.OFFLINE_MODE);
      return offlineTime ? parseInt(offlineTime, 10) : undefined;
    } catch (error) {
      console.error('Failed to get last online time:', error);
      return undefined;
    }
  }

  /**
   * Check if cache has expired
   */
  private isCacheExpired(timestamp: number): boolean {
    const now = Date.now();
    const expiryTime = CACHE_EXPIRY_HOURS * 60 * 60 * 1000; // Convert to milliseconds
    return (now - timestamp) > expiryTime;
  }

  /**
   * Check if there is valid cached data available
   */
  private hasValidCachedData(): boolean {
    const lastItinerary = this.getLastCachedItinerary();
    const cachedPlans = this.getCachedTripPlans();
    
    return lastItinerary !== null || cachedPlans.length > 0;
  }

  /**
   * Get cache storage usage information
   */
  getCacheInfo(): {
    hasLastItinerary: boolean;
    cachedPlansCount: number;
    cacheAge?: number;
    isExpired: boolean;
  } {
    const lastItinerary = this.getLastCachedItinerary();
    const cachedPlans = this.getCachedTripPlans();
    const cacheTimestamp = localStorage.getItem(CACHE_KEYS.CACHE_TIMESTAMP);
    
    let cacheAge: number | undefined;
    let isExpired = false;
    
    if (cacheTimestamp) {
      const timestamp = parseInt(cacheTimestamp, 10);
      cacheAge = Date.now() - timestamp;
      isExpired = this.isCacheExpired(timestamp);
    }

    return {
      hasLastItinerary: lastItinerary !== null,
      cachedPlansCount: cachedPlans.length,
      cacheAge,
      isExpired
    };
  }

  /**
   * Clear all cached data
   */
  clearAllCache(): void {
    this.clearLastCachedItinerary();
    this.clearCachedTripPlans();
    this.clearOfflineMode();
    console.log('All cached data cleared');
  }

  /**
   * Sync cached data when coming back online
   */
  async syncWhenOnline(): Promise<void> {
    if (!this.isOnline()) {
      console.log('Cannot sync - still offline');
      return;
    }

    try {
      // This method can be extended to sync cached data with the server
      // when the application comes back online
      console.log('Syncing cached data with server...');
      
      // For now, we just log that sync would happen here
      // In a full implementation, this would:
      // 1. Check for cached trip plans that need to be uploaded
      // 2. Download any new data from the server
      // 3. Resolve any conflicts between local and server data
      
    } catch (error) {
      console.error('Failed to sync cached data:', error);
    }
  }
}

// Export singleton instance
export const offlineCacheService = new OfflineCacheService();
export default offlineCacheService;