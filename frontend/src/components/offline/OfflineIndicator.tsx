/**
 * Offline indicator component for the AI Trip Planner.
 * 
 * This component displays the current online/offline status and provides
 * information about cached data availability.
 */

import React from 'react';
import { useOfflineCache } from '../../hooks/useOfflineCache';

interface OfflineIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ 
  className = '', 
  showDetails = false 
}) => {
  const { isOnline, offlineStatus, cacheInfo } = useOfflineCache();

  if (isOnline && !showDetails) {
    return null; // Don't show anything when online unless details are requested
  }

  const formatCacheAge = (ageMs?: number): string => {
    if (!ageMs) return 'Unknown';
    
    const minutes = Math.floor(ageMs / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  const getStatusColor = (): string => {
    if (isOnline) return 'bg-green-500';
    if (offlineStatus.hasCachedData) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusText = (): string => {
    if (isOnline) return 'Online';
    if (offlineStatus.hasCachedData) return 'Offline (Cached data available)';
    return 'Offline (No cached data)';
  };

  const getStatusIcon = (): string => {
    if (isOnline) return '🟢';
    if (offlineStatus.hasCachedData) return '🟡';
    return '🔴';
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Status indicator */}
      <div className="flex items-center space-x-2">
        <div 
          className={`w-3 h-3 rounded-full ${getStatusColor()}`}
          title={getStatusText()}
        />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>

      {/* Offline details */}
      {!isOnline && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {offlineStatus.hasCachedData ? (
            <span className="text-yellow-600 dark:text-yellow-400">
              📦 Cached data available
            </span>
          ) : (
            <span className="text-red-600 dark:text-red-400">
              ⚠️ No cached data
            </span>
          )}
        </div>
      )}

      {/* Detailed cache information */}
      {showDetails && (
        <div className="ml-4 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex flex-col space-y-1">
            {cacheInfo.hasLastItinerary && (
              <div>📋 Last itinerary cached</div>
            )}
            {cacheInfo.cachedPlansCount > 0 && (
              <div>💾 {cacheInfo.cachedPlansCount} trip plans cached</div>
            )}
            {cacheInfo.cacheAge && (
              <div>🕒 Cache age: {formatCacheAge(cacheInfo.cacheAge)}</div>
            )}
            {cacheInfo.isExpired && (
              <div className="text-orange-500">⏰ Cache expired</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OfflineIndicator;