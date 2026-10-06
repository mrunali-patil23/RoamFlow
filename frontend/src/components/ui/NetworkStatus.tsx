/**
 * Network Status Indicator Component
 * Shows connection status and provides retry functionality
 */

import React from 'react';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';

interface NetworkStatusProps {
  showWhenOnline?: boolean;
  className?: string;
}

const NetworkStatus: React.FC<NetworkStatusProps> = ({ 
  showWhenOnline = false, 
  className = '' 
}) => {
  const { isOnline, isApiConnected, checkConnection } = useNetworkStatus();

  // Don't show anything if online and showWhenOnline is false
  if (isOnline && isApiConnected && !showWhenOnline) {
    return null;
  }

  const getStatusInfo = () => {
    if (!isOnline) {
      return {
        color: 'bg-red-500',
        textColor: 'text-red-700 dark:text-red-300',
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        borderColor: 'border-red-200 dark:border-red-800',
        icon: '🔴',
        title: 'No Internet Connection',
        message: 'Please check your internet connection and try again.'
      };
    }

    if (!isApiConnected) {
      return {
        color: 'bg-yellow-500',
        textColor: 'text-yellow-700 dark:text-yellow-300',
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        borderColor: 'border-yellow-200 dark:border-yellow-800',
        icon: '⚠️',
        title: 'Server Connection Issues',
        message: 'Unable to connect to our servers. Some features may not work properly.'
      };
    }

    return {
      color: 'bg-green-500',
      textColor: 'text-green-700 dark:text-green-300',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-200 dark:border-green-800',
      icon: '🟢',
      title: 'Connected',
      message: 'All systems are working normally.'
    };
  };

  const status = getStatusInfo();
  const showRetryButton = !isOnline || !isApiConnected;

  return (
    <div className={`rounded-md border p-4 ${status.bgColor} ${status.borderColor} ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-lg" role="img" aria-label="status">
            {status.icon}
          </span>
        </div>
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${status.textColor}`}>
            {status.title}
          </h3>
          <p className={`mt-1 text-sm ${status.textColor}`}>
            {status.message}
          </p>
          {showRetryButton && (
            <div className="mt-3">
              <button
                onClick={checkConnection}
                className="text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded px-3 py-1 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Retry Connection
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Compact version for header/status bar
export const NetworkStatusIndicator: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { isOnline, isApiConnected } = useNetworkStatus();

  if (isOnline && isApiConnected) {
    return null;
  }

  const getIndicatorInfo = () => {
    if (!isOnline) {
      return { icon: '🔴', title: 'Offline' };
    }
    if (!isApiConnected) {
      return { icon: '⚠️', title: 'Connection Issues' };
    }
    return { icon: '🟢', title: 'Online' };
  };

  const indicator = getIndicatorInfo();

  return (
    <div className={`flex items-center space-x-1 text-sm ${className}`}>
      <span role="img" aria-label="network status">
        {indicator.icon}
      </span>
      <span className="text-gray-600 dark:text-gray-400">
        {indicator.title}
      </span>
    </div>
  );
};

export default NetworkStatus;