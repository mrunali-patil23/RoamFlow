/**
 * Hook for monitoring network status and API connectivity
 */

import { useState, useEffect } from 'react';
import ApiService from '../services/apiService';

interface NetworkStatus {
  isOnline: boolean;
  isApiConnected: boolean;
  lastChecked: Date | null;
  checkConnection: () => Promise<void>;
}

export const useNetworkStatus = (): NetworkStatus => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isApiConnected, setIsApiConnected] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkConnection = async () => {
    try {
      const apiStatus = await ApiService.checkNetworkStatus();
      setIsApiConnected(apiStatus);
      setLastChecked(new Date());
    } catch (error) {
      setIsApiConnected(false);
      setLastChecked(new Date());
    }
  };

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      checkConnection();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsApiConnected(false);
    };

    // Listen for online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check API connection on mount
    checkConnection();

    // Periodic API health check (every 30 seconds)
    const interval = setInterval(checkConnection, 30000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  return {
    isOnline,
    isApiConnected,
    lastChecked,
    checkConnection
  };
};

export default useNetworkStatus;