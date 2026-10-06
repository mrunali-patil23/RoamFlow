import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import SkeletonLoader, { 
  SkeletonText, 
  SkeletonCard, 
  SkeletonButton, 
  SkeletonAvatar, 
  SkeletonTable, 
  SkeletonItinerary 
} from './SkeletonLoader';

describe('SkeletonLoader Property Tests', () => {
  // Feature: ai-trip-planner, Property 26: Loading State Display
  it('should display skeleton loaders with consistent structure for any configuration', () => {
    fc.assert(
      fc.property(
        fc.record({
          width: fc.constantFrom('w-full', 'w-1/2', 'w-1/3', 'w-1/4', 'w-3/4'),
          height: fc.constantFrom('h-4', 'h-6', 'h-8', 'h-10', 'h-12'),
          rounded: fc.boolean(),
        }),
        (config) => {
          const { container } = render(
            <SkeletonLoader 
              width={config.width}
              height={config.height}
              rounded={config.rounded}
            />
          );
          
          const skeletonElement = container.firstChild as HTMLElement;
          expect(skeletonElement).toBeTruthy();
          
          // Verify skeleton has required classes
          expect(skeletonElement.classList.contains('animate-pulse')).toBe(true);
          expect(skeletonElement.classList.contains('bg-gray-300')).toBe(true);
          expect(skeletonElement.classList.contains('dark:bg-gray-600')).toBe(true);
          expect(skeletonElement.classList.contains(config.width)).toBe(true);
          expect(skeletonElement.classList.contains(config.height)).toBe(true);
          
          // Verify rounded class is applied correctly
          if (config.rounded) {
            expect(skeletonElement.classList.contains('rounded')).toBe(true);
          }
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonText with correct number of lines', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 10 }),
        (lines) => {
          const { container } = render(<SkeletonText lines={lines} />);
          
          const skeletonLines = container.querySelectorAll('.animate-pulse');
          expect(skeletonLines.length).toBe(lines);
          
          // Verify last line has different width (3/4) for natural text appearance
          if (lines > 1) {
            const lastLine = skeletonLines[skeletonLines.length - 1];
            expect(lastLine.classList.contains('w-3/4')).toBe(true);
          }
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonTable with correct grid structure', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 10 }),
        fc.integer({ min: 1, max: 8 }),
        (rows, columns) => {
          const { container } = render(
            <SkeletonTable rows={rows} columns={columns} />
          );
          
          // Count grid containers (header + rows)
          const gridContainers = container.querySelectorAll('.grid');
          expect(gridContainers.length).toBe(rows + 1); // +1 for header
          
          // Verify each grid has correct number of skeleton elements
          gridContainers.forEach((grid) => {
            const skeletonElements = grid.querySelectorAll('.animate-pulse');
            expect(skeletonElements.length).toBe(columns);
          });
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonItinerary with correct day structure', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 7 }),
        (days) => {
          const { container } = render(<SkeletonItinerary days={days} />);
          
          // Count day containers
          const dayContainers = container.querySelectorAll('.bg-white, .dark\\:bg-gray-800');
          expect(dayContainers.length).toBe(days);
          
          // Verify each day has the expected structure
          dayContainers.forEach((dayContainer) => {
            // Should have skeleton elements for day header, weather, and activities
            const skeletonElements = dayContainer.querySelectorAll('.animate-pulse');
            expect(skeletonElements.length).toBeGreaterThan(0);
            
            // Should have activity structure (border-l-4 indicates activities)
            const activities = dayContainer.querySelectorAll('.border-l-4');
            expect(activities.length).toBe(3); // Default 3 activities per day
          });
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonAvatar with correct size classes', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('sm', 'md', 'lg'),
        (size) => {
          const { container } = render(<SkeletonAvatar size={size} />);
          
          const avatarElement = container.firstChild as HTMLElement;
          expect(avatarElement).toBeTruthy();
          
          // Verify size classes
          const sizeClasses = {
            sm: ['w-8', 'h-8'],
            md: ['w-12', 'h-12'],
            lg: ['w-16', 'h-16']
          };
          
          sizeClasses[size].forEach(sizeClass => {
            expect(avatarElement.classList.contains(sizeClass)).toBe(true);
          });
          
          // Verify it's rounded (avatar should be circular)
          expect(avatarElement.classList.contains('rounded-full')).toBe(true);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonCard with consistent structure', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 0, maxLength: 50 }),
        (className) => {
          const { container } = render(<SkeletonCard className={className} />);
          
          const cardElement = container.firstChild as HTMLElement;
          expect(cardElement).toBeTruthy();
          
          // Verify card structure
          expect(cardElement.classList.contains('bg-white')).toBe(true);
          expect(cardElement.classList.contains('dark:bg-gray-800')).toBe(true);
          expect(cardElement.classList.contains('rounded-lg')).toBe(true);
          expect(cardElement.classList.contains('shadow-md')).toBe(true);
          expect(cardElement.classList.contains('p-6')).toBe(true);
          
          // Verify it contains skeleton elements
          const skeletonElements = cardElement.querySelectorAll('.animate-pulse');
          expect(skeletonElements.length).toBeGreaterThan(0);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should render SkeletonButton with button-like appearance', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 0, maxLength: 50 }),
        (className) => {
          const { container } = render(<SkeletonButton className={className} />);
          
          const buttonElement = container.firstChild as HTMLElement;
          expect(buttonElement).toBeTruthy();
          
          // Verify button-like structure
          expect(buttonElement.classList.contains('animate-pulse')).toBe(true);
          expect(buttonElement.classList.contains('w-24')).toBe(true);
          expect(buttonElement.classList.contains('h-10')).toBe(true);
          expect(buttonElement.classList.contains('rounded-md')).toBe(true);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});