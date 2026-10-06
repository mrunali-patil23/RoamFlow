/**
 * React hook for offline caching functionality.
 * 
 * This hook provides a React-friendly interface to the offline cache service
 * and manages offline state and cached data.
 */

import { useState, useEffect, useCallback } from 'react';
import { offlineCacheService, CachedTripPlan, OfflineStatus, TripPlan } from '../services/offlineCacheService';
import { TripPreferences } from '../types/trip';

export interface UseOfflineCacheReturn {
  // Offline status
  isOnline: boolean;
  offlineStatus: OfflineStatus;
  
  // Cache operations
  cacheLastItinerary: (tripPlan: TripPlan, preferences: TripPreferences) => void;
  getLastCachedItinerary: () => CachedTripPlan | null;
  clearLastCachedItinerary: () => void;
  
  // Trip plans cache
  cacheTripPlans: (tripPlans: TripPlan[]) => void;
  getCachedTripPlans: () => TripPlan[];
  clearCachedTripPlans: () => void;
  
  // Cache info
  cacheInfo: {
    hasLastItinerary: boolean;
    cachedPlansCount: number;
    cacheAge?: number;
    isExpired: boolean;
  };
  
  // Utility functions
  clearAllCache: () => void;
  syncWhenOnline: () => Promise<void>;
  refreshCacheInfo: () => void;
}

export const useOfflineCache = (): UseOfflineCacheReturn => {
  const [isOnline, setIsOnline] = useState<boolean>(offlineCacheService.isOnline());
  const [offlineStatus, setOfflineStatus] = useState<OfflineStatus>(
    offlineCacheService.getOfflineStatus()
  );
  const [cacheInfo, setCacheInfo] = useState(offlineCacheService.getCacheInfo());

  // Update online status when it changes
  useEffect(() => {
    const handleOnlineStatusChange = (online: boolean) => {
      setIsOnline(online);
      setOfflineStatus(offlineCacheService.getOfflineStatus());
      setCacheInfo(offlineCacheService.getCacheInfo());
      
      // Auto-sync when coming back online
      if (online) {
        offlineCacheService.syncWhenOnline().catch(console.error);
      }
    };

    offlineCacheService.addOnlineStatusListener(handleOnlineStatusChange);

    return () => {
      offlineCacheService.removeOnlineStatusListener(handleOnlineStatusChange);
    };
  }, []);

  // Refresh cache info periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setCacheInfo(offlineCacheService.getCacheInfo());
      setOfflineStatus(offlineCacheService.getOfflineStatus());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Cache operations with state updates
  const cacheLastItinerary = useCallback((tripPlan: TripPlan, preferences: TripPreferences) => {
    offlineCacheService.cacheLastItinerary(tripPlan, preferences);
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const getLastCachedItinerary = useCallback(() => {
    return offlineCacheService.getLastCachedItinerary();
  }, []);

  const clearLastCachedItinerary = useCallback(() => {
    offlineCacheService.clearLastCachedItinerary();
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const cacheTripPlans = useCallback((tripPlans: TripPlan[]) => {
    offlineCacheService.cacheTripPlans(tripPlans);
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const getCachedTripPlans = useCallback(() => {
    return offlineCacheService.getCachedTripPlans();
  }, []);

  const clearCachedTripPlans = useCallback(() => {
    offlineCacheService.clearCachedTripPlans();
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const clearAllCache = useCallback(() => {
    offlineCacheService.clearAllCache();
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const syncWhenOnline = useCallback(async () => {
    await offlineCacheService.syncWhenOnline();
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  const refreshCacheInfo = useCallback(() => {
    setCacheInfo(offlineCacheService.getCacheInfo());
    setOfflineStatus(offlineCacheService.getOfflineStatus());
  }, []);

  return {
    isOnline,
    offlineStatus,
    cacheLastItinerary,
    getLastCachedItinerary,
    clearLastCachedItinerary,
    cacheTripPlans,
    getCachedTripPlans,
    clearCachedTripPlans,
    cacheInfo,
    clearAllCache,
    syncWhenOnline,
    refreshCacheInfo
  };
};

export default useOfflineCache;