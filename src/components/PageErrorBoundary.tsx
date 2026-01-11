'use client';

import React, { ReactNode } from 'react';
import { ErrorBoundary } from './ErrorBoundary';
import { useRouter } from 'next/navigation';

interface PageErrorBoundaryProps {
  children: ReactNode;
  showNavigation?: boolean;
}

interface PageErrorFallbackProps {
  error: Error | null;
  onRetry: () => void;
  onGoHome: () => void;
  showNavigation: boolean;
}

function PageErrorFallback({ error, onRetry, onGoHome, showNavigation }: PageErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          {/* Error Icon */}
          <div className="flex items-center justify-center w-16 h-16 mx-auto bg-red-100 rounded-full mb-6">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>

          {/* Error Message */}
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Oops! Something went wrong
          </h1>
          <p className="text-gray-600 mb-8">
            We encountered an unexpected error while loading this page. 
            Don't worry, our team has been notified and we're working to fix it.
          </p>

          {/* Development Error Details */}
          {process.env.NODE_ENV === 'development' && error && (
            <div className="mb-8 p-4 bg-red-50 rounded-lg text-left">
              <h3 className="text-sm font-medium text-red-800 mb-2">
                Error Details (Development Mode):
              </h3>
              <div className="text-xs text-red-700 font-mono bg-red-100 p-2 rounded overflow-auto max-h-32">
                <p className="break-all">{error.message}</p>
                {error.stack && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-red-600 hover:text-red-800">
                      Stack Trace
                    </summary>
                    <pre className="mt-1 text-xs whitespace-pre-wrap">
                      {error.stack}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={onRetry}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Try Again
            </button>
            
            {showNavigation && (
              <button
                onClick={onGoHome}
                className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                Go Home
              </button>
            )}
          </div>

          {/* Help Text */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Still having trouble?</strong> Try refreshing the page or clearing your browser cache.
              If the problem persists, please contact our support team.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function PageErrorBoundary({ children, showNavigation = true }: PageErrorBoundaryProps) {
  const router = useRouter();

  const handleGoHome = () => {
    router.push('/');
  };

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <ErrorBoundary
      fallback={
        <PageErrorFallback
          error={null}
          onRetry={handleRetry}
          onGoHome={handleGoHome}
          showNavigation={showNavigation}
        />
      }
      onError={(error, errorInfo) => {
        // Log page-level errors
        console.error('Page Error caught by boundary:', {
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          url: window.location.href,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
        });

        // In production, you might want to send this to an error tracking service
        // Example: sendErrorToService({ error, errorInfo, context: 'page' });
      }}
      resetOnPropsChange={true}
      resetKeys={[typeof window !== 'undefined' ? window.location.pathname : '']} // Reset when route changes
    >
      {children}
    </ErrorBoundary>
  );
}

export default PageErrorBoundary;