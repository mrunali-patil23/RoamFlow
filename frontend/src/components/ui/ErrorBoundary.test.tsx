import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import * as fc from 'fast-check';
import ErrorBoundary, { FormErrorBoundary, APIErrorBoundary } from './ErrorBoundary';

// Component that throws an error
const ThrowError: React.FC<{ shouldThrow: boolean; errorMessage?: string }> = ({ 
  shouldThrow, 
  errorMessage = 'Test error' 
}) => {
  if (shouldThrow) {
    throw new Error(errorMessage);
  }
  return <div data-testid="success">No error</div>;
};

// Component that works normally
const WorkingComponent: React.FC<{ content?: string }> = ({ content = 'Working' }) => (
  <div data-testid="working">{content}</div>
);

describe('ErrorBoundary Property Tests', () => {
  // Suppress console.error for these tests
  const originalConsoleError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });
  
  afterEach(() => {
    console.error = originalConsoleError;
  });

  // Feature: ai-trip-planner, Property 27: Error Handling Gracefully
  it('should gracefully handle any error and display fallback UI', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.boolean(),
        (errorMessage, shouldThrow) => {
          const { container, queryByTestId, unmount } = render(
            <ErrorBoundary>
              <ThrowError shouldThrow={shouldThrow} errorMessage={errorMessage} />
            </ErrorBoundary>
          );
          
          try {
            if (shouldThrow) {
              // Should display error UI
              expect(queryByTestId('success')).toBeNull();
              
              // Should contain error message elements
              const errorContainer = container.querySelector('.text-center');
              expect(errorContainer).toBeTruthy();
              
              // Should have error icon
              const errorIcon = container.querySelector('.text-red-500');
              expect(errorIcon).toBeTruthy();
              
              // Should have "Something went wrong" heading
              const heading = container.querySelector('h1');
              expect(heading).toBeTruthy();
              expect(heading?.textContent).toContain('Something went wrong');
              
              // Should have action buttons
              const buttons = container.querySelectorAll('button');
              expect(buttons.length).toBeGreaterThanOrEqual(2); // Refresh and Try Again buttons
              
              // Verify button texts
              const buttonTexts = Array.from(buttons).map(btn => btn.textContent);
              expect(buttonTexts).toContain('Refresh Page');
              expect(buttonTexts).toContain('Try Again');
              
            } else {
              // Should display normal content
              expect(queryByTestId('success')).toBeTruthy();
            }
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should handle custom fallback UI when provided', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 5, maxLength: 50 }),
        fc.string({ minLength: 1, maxLength: 100 }),
        (fallbackText, errorMessage) => {
          const customFallback = <div data-testid="custom-fallback">{fallbackText}</div>;
          
          const { queryByTestId, unmount } = render(
            <ErrorBoundary fallback={customFallback}>
              <ThrowError shouldThrow={true} errorMessage={errorMessage} />
            </ErrorBoundary>
          );
          
          try {
            // Should display custom fallback
            const fallbackElement = queryByTestId('custom-fallback');
            expect(fallbackElement).toBeTruthy();
            expect(fallbackElement?.textContent).toBe(fallbackText);
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render FormErrorBoundary with form-specific error UI', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.boolean(),
        (errorMessage, shouldThrow) => {
          const { container, queryByTestId, unmount } = render(
            <FormErrorBoundary>
              <ThrowError shouldThrow={shouldThrow} errorMessage={errorMessage} />
            </FormErrorBoundary>
          );
          
          try {
            if (shouldThrow) {
              // Should display form-specific error UI
              expect(queryByTestId('success')).toBeNull();
              
              // Should have red background (form error styling)
              const errorContainer = container.querySelector('.bg-red-50, .dark\\:bg-red-900\\/20');
              expect(errorContainer).toBeTruthy();
              
              // Should contain "Form Error" heading
              const heading = container.querySelector('h3');
              expect(heading).toBeTruthy();
              expect(heading?.textContent).toContain('Form Error');
              
              // Should have error icon
              const errorIcon = container.querySelector('.text-red-400');
              expect(errorIcon).toBeTruthy();
              
            } else {
              // Should display normal content
              expect(queryByTestId('success')).toBeTruthy();
            }
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render APIErrorBoundary with API-specific error UI', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.boolean(),
        (errorMessage, shouldThrow) => {
          const { container, queryByTestId, unmount } = render(
            <APIErrorBoundary>
              <ThrowError shouldThrow={shouldThrow} errorMessage={errorMessage} />
            </APIErrorBoundary>
          );
          
          try {
            if (shouldThrow) {
              // Should display API-specific error UI
              expect(queryByTestId('success')).toBeNull();
              
              // Should have yellow background (API error styling)
              const errorContainer = container.querySelector('.bg-yellow-50, .dark\\:bg-yellow-900\\/20');
              expect(errorContainer).toBeTruthy();
              
              // Should contain "Connection Error" heading
              const heading = container.querySelector('h3');
              expect(heading).toBeTruthy();
              expect(heading?.textContent).toContain('Connection Error');
              
              // Should have warning icon
              const warningIcon = container.querySelector('.text-yellow-400');
              expect(warningIcon).toBeTruthy();
              
            } else {
              // Should display normal content
              expect(queryByTestId('success')).toBeTruthy();
            }
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should handle multiple nested components with errors gracefully', () => {
    fc.assert(
      fc.property(
        fc.array(fc.boolean(), { minLength: 1, maxLength: 3 }), // Reduced array size
        fc.array(fc.string({ minLength: 5, maxLength: 30 }), { minLength: 1, maxLength: 3 }),
        (shouldThrowArray, contentArray) => {
          const components = shouldThrowArray.map((shouldThrow, index) => (
            shouldThrow ? 
              <ThrowError key={index} shouldThrow={true} errorMessage={`Error ${index}`} /> :
              <WorkingComponent key={index} content={contentArray[index % contentArray.length]} />
          ));
          
          const { container, queryAllByTestId, unmount } = render(
            <ErrorBoundary>
              <div>
                {components}
              </div>
            </ErrorBoundary>
          );
          
          try {
            const hasAnyError = shouldThrowArray.some(shouldThrow => shouldThrow);
            
            if (hasAnyError) {
              // Should display error UI if any component throws
              const workingElements = queryAllByTestId('working');
              expect(workingElements.length).toBe(0);
              
              // Should have error container
              const errorContainer = container.querySelector('.text-center');
              expect(errorContainer).toBeTruthy();
              
            } else {
              // Should display all working components
              const workingElements = queryAllByTestId('working');
              expect(workingElements.length).toBe(components.length);
            }
            
            return true;
          } finally {
            unmount();
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});