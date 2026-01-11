'use client';

import React, { ReactNode } from 'react';
import { ErrorBoundary } from './ErrorBoundary';
import { ApiError, isApiError, getErrorCode, isRetryableError, getRetryAfter } from '@/lib/api';
import { ErrorResponse } from '@/types';

interface ApiErrorBoundaryProps {
  children: ReactNode;
  onRetry?: () => void;
  fallbackComponent?: React.ComponentType<ApiErrorFallbackProps>;
}

interface ApiErrorFallbackProps {
  error: Error;
  onRetry?: () => void;
  onReset: () => void;
}

function ApiErrorFallback({ error, onRetry, onReset }: ApiErrorFallbackProps) {
  const isApi = isApiError(error);
  const errorCode = getErrorCode(error);
  const canRetry = isRetryableError(error);
  const retryAfter = getRetryAfter(error);

  // Determine error type and appropriate message
  const getErrorInfo = () => {
    if (!isApi) {
      return {
        title: 'Application Error',
        message: 'An unexpected error occurred. Please try again.',
        type: 'general' as const,
      };
    }

    const apiError = error as ApiError;
    
    switch (apiError.status) {
      case 400:
        return {
          title: 'Invalid Request',
          message: 'Please check your input and try again.',
          type: 'validation' as const,
        };
      case 401:
        return {
          title: 'Authentication Required',
          message: 'Please log in to continue.',
          type: 'auth' as const,
        };
      case 403:
        return {
          title: 'Access Denied',
          message: 'You don\'t have permission to perform this action.',
          type: 'auth' as const,
        };
      case 404:
        return {
          title: 'Not Found',
          message: 'The requested resource could not be found.',
          type: 'not-found' as const,
        };
      case 408:
        return {
          title: 'Request Timeout',
          message: 'The request took too long to complete. Please try again.',
          type: 'timeout' as const,
        };
      case 429:
        return {
          title: 'Too Many Requests',
          message: retryAfter 
            ? `Please wait ${retryAfter} seconds before trying again.`
            : 'You\'re making too many requests. Please wait a moment and try again.',
          type: 'rate-limit' as const,
        };
      case 500:
        return {
          title: 'Server Error',
          message: 'Our servers are experiencing issues. Please try again later.',
          type: 'server' as const,
        };
      case 502:
      case 503:
      case 504:
        return {
          title: 'Service Unavailable',
          message: 'Our services are temporarily unavailable. Please try again later.',
          type: 'service' as const,
        };
      default:
        return {
          title: 'Network Error',
          message: 'Unable to connect to our services. Please check your connection and try again.',
          type: 'network' as const,
        };
    }
  };

  const errorInfo = getErrorInfo();

  const getIcon = () => {
    switch (errorInfo.type) {
      case 'validation':
        return (
          <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'auth':
        return (
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        );
      case 'network':
      case 'timeout':
        return (
          <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
          </svg>
        );
      case 'server':
      case 'service':
        return (
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
    }
  };

  const getIconBgColor = () => {
    switch (errorInfo.type) {
      case 'validation':
        return 'bg-yellow-100';
      case 'auth':
        return 'bg-red-100';
      case 'network':
      case 'timeout':
        return 'bg-orange-100';
      default:
        return 'bg-red-100';
    }
  };

  return (
    <div className="min-h-[400px] flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className={`flex items-center justify-center w-12 h-12 mx-auto ${getIconBgColor()} rounded-full mb-4`}>
          {getIcon()}
        </div>

        <div className="text-center">
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            {errorInfo.title}
          </h1>
          <p className="text-gray-600 mb-6">
            {errorInfo.message}
          </p>

          {process.env.NODE_ENV === 'development' && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
              <h3 className="text-sm font-medium text-gray-800 mb-2">
                Debug Information:
              </h3>
              <div className="text-xs text-gray-600 space-y-1">
                <p><strong>Error:</strong> {error.message}</p>
                {isApi && <p><strong>Status:</strong> {(error as ApiError).status}</p>}
                {errorCode && <p><strong>Code:</strong> {errorCode}</p>}
                {retryAfter && <p><strong>Retry After:</strong> {retryAfter}s</p>}
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            {(canRetry || onRetry) && (
              <button
                onClick={onRetry || onReset}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                disabled={retryAfter ? true : false}
              >
                {retryAfter ? `Retry in ${retryAfter}s` : 'Try Again'}
              </button>
            )}
            
            <button
              onClick={onReset}
              className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Go Back
            </button>
          </div>

          {errorInfo.type === 'network' && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Tip:</strong> Check your internet connection and try again.
              </p>
            </div>
          )}

          {errorInfo.type === 'server' && (
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Status:</strong> We're working to resolve this issue. Please try again in a few minutes.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function ApiErrorBoundary({ 
  children, 
  onRetry, 
  fallbackComponent: FallbackComponent = ApiErrorFallback 
}: ApiErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={undefined}
      onError={(error, errorInfo) => {
        // Log API errors for monitoring
        if (isApiError(error)) {
          console.error('API Error caught by boundary:', {
            message: error.message,
            status: error.status,
            errorResponse: error.errorResponse,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
          });
        }
      }}
    >
      <ErrorBoundary
        fallback={
          <FallbackComponent
            error={new Error('Fallback error')}
            onRetry={onRetry}
            onReset={() => window.location.reload()}
          />
        }
      >
        {children}
      </ErrorBoundary>
    </ErrorBoundary>
  );
}

export default ApiErrorBoundary;