/**
 * Integration test setup and configuration
 */

import { beforeAll, afterAll, beforeEach, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Global test setup
beforeAll(() => {
  // Mock window.matchMedia for CSS media queries
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => {},
    }),
  });

  // Mock IntersectionObserver
  global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  };

  // Mock ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  };

  // Mock scrollTo
  window.scrollTo = () => {};

  // Mock alert
  window.alert = () => {};

  // Mock console methods to reduce noise in tests
  const originalConsoleError = console.error;
  console.error = (...args: any[]) => {
    // Only show console.error for actual test failures, not React warnings
    if (typeof args[0] === 'string' && args[0].includes('Warning:')) {
      return;
    }
    originalConsoleError(...args);
  };
});

// Cleanup after each test
afterEach(() => {
  cleanup();
  
  // Clear all mocks
  vi.clearAllMocks();
  
  // Reset localStorage
  localStorage.clear();
  
  // Reset navigator.onLine
  Object.defineProperty(navigator, 'onLine', {
    writable: true,
    value: true,
  });
});

// Global cleanup
afterAll(() => {
  // Restore console methods
  vi.restoreAllMocks();
});