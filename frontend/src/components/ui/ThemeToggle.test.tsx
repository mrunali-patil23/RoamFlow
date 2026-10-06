import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fc from 'fast-check';
import ThemeToggle from './ThemeToggle';
import { ThemeProvider } from '../../contexts/ThemeContext';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

const ThemeToggleWrapper: React.FC = () => (
  <ThemeProvider>
    <ThemeToggle />
  </ThemeProvider>
);

describe('ThemeToggle Property Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset document classes
    document.documentElement.classList.remove('dark');
  });

  // Feature: ai-trip-planner, Property 25: Theme Toggle Consistency
  it('should consistently toggle between light and dark themes for any number of clicks', () => {
    fc.assert(
      fc.property(
        fc.array(fc.boolean(), { minLength: 1, maxLength: 20 }), // Array of clicks
        (clicks) => {
          const { container } = render(<ThemeToggleWrapper />);
          const toggleButton = container.querySelector('button');
          expect(toggleButton).toBeTruthy();

          // Track expected theme state
          let expectedTheme = 'light'; // Default theme
          
          // Perform all clicks and verify consistency
          clicks.forEach((_, index) => {
            fireEvent.click(toggleButton!);
            expectedTheme = expectedTheme === 'light' ? 'dark' : 'light';
            
            // Verify document class matches expected theme
            if (expectedTheme === 'dark') {
              expect(document.documentElement.classList.contains('dark')).toBe(true);
            } else {
              expect(document.documentElement.classList.contains('dark')).toBe(false);
            }
            
            // Verify localStorage is called with correct theme
            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', expectedTheme);
            
            // Verify button shows correct icon (sun for dark mode, moon for light mode)
            const svgElement = toggleButton!.querySelector('svg');
            expect(svgElement).toBeTruthy();
            
            // Check aria-label for accessibility
            const expectedLabel = `Switch to ${expectedTheme === 'light' ? 'dark' : 'light'} mode`;
            expect(toggleButton!.getAttribute('aria-label')).toBe(expectedLabel);
          });
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should maintain theme consistency across component remounts', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('light', 'dark'),
        fc.integer({ min: 1, max: 10 }),
        (initialTheme, toggleCount) => {
          // Set initial theme in localStorage
          localStorageMock.getItem.mockReturnValue(initialTheme);
          
          // First render
          const { container, unmount } = render(<ThemeToggleWrapper />);
          let toggleButton = container.querySelector('button');
          expect(toggleButton).toBeTruthy();
          
          // Perform toggles
          let expectedTheme = initialTheme;
          for (let i = 0; i < toggleCount; i++) {
            fireEvent.click(toggleButton!);
            expectedTheme = expectedTheme === 'light' ? 'dark' : 'light';
          }
          
          // Unmount and remount
          unmount();
          
          // Mock localStorage to return the last theme
          localStorageMock.getItem.mockReturnValue(expectedTheme);
          
          const { container: newContainer } = render(<ThemeToggleWrapper />);
          const newToggleButton = newContainer.querySelector('button');
          
          // Verify theme is consistent after remount
          if (expectedTheme === 'dark') {
            expect(document.documentElement.classList.contains('dark')).toBe(true);
          } else {
            expect(document.documentElement.classList.contains('dark')).toBe(false);
          }
          
          // Verify button shows correct state
          const expectedLabel = `Switch to ${expectedTheme === 'light' ? 'dark' : 'light'} mode`;
          expect(newToggleButton!.getAttribute('aria-label')).toBe(expectedLabel);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});