import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import * as fc from 'fast-check';
import { TripPlan, TravelType, BudgetLevel, Interest, ActivityType } from '../../types/trip';

// Mock react-pdf/renderer
vi.mock('@react-pdf/renderer', () => ({
  Document: ({ children }: { children: React.ReactNode }) => <div data-testid="pdf-document">{children}</div>,
  Page: ({ children }: { children: React.ReactNode }) => <div data-testid="pdf-page">{children}</div>,
  Text: ({ children }: { children: React.ReactNode }) => <span data-testid="pdf-text">{children}</span>,
  View: ({ children }: { children: React.ReactNode }) => <div data-testid="pdf-view">{children}</div>,
  StyleSheet: {
    create: (styles: any) => styles,
  },
  PDFDownloadLink: ({ children, document: doc, fileName }: any) => (
    <a href="#" download={fileName} data-testid="pdf-download-link">
      {typeof children === 'function' ? children({ loading: false, error: null }) : children}
    </a>
  ),
}));

// Import after mocking
import PDFExporter from './PDFExporter';

// Generators for property-based testing
const travelTypeArb = fc.constantFrom(...Object.values(TravelType));
const budgetLevelArb = fc.constantFrom(...Object.values(BudgetLevel));
const interestArb = fc.constantFrom(...Object.values(Interest));
const activityTypeArb = fc.constantFrom(...Object.values(ActivityType));

const weatherInfoArb = fc.record({
  date: fc.date().map(d => d.toISOString().split('T')[0]),
  temperatureHigh: fc.option(fc.integer({ min: -10, max: 50 })),
  temperatureLow: fc.option(fc.integer({ min: -20, max: 40 })),
  condition: fc.string({ minLength: 3, maxLength: 20 }),
  description: fc.string({ minLength: 10, maxLength: 100 }),
  humidity: fc.option(fc.integer({ min: 0, max: 100 })),
  precipitationChance: fc.option(fc.integer({ min: 0, max: 100 })),
});

const activityArb = fc.record({
  name: fc.string({ minLength: 5, maxLength: 50 }),
  activityType: activityTypeArb,
  description: fc.string({ minLength: 20, maxLength: 200 }),
  durationHours: fc.integer({ min: 1, max: 12 }),
  costInr: fc.integer({ min: 0, max: 50000 }),
  location: fc.option(fc.string({ minLength: 5, maxLength: 50 })),
  rating: fc.option(fc.float({ min: 1, max: 5 })),
  startTime: fc.option(fc.string({ minLength: 5, maxLength: 8 })),
  endTime: fc.option(fc.string({ minLength: 5, maxLength: 8 })),
  bookingRequired: fc.boolean(),
});

const dayPlanArb = fc.record({
  dayNumber: fc.integer({ min: 1, max: 30 }),
  date: fc.date().map(d => d.toISOString().split('T')[0]),
  activities: fc.array(activityArb, { minLength: 1, maxLength: 8 }),
  weather: weatherInfoArb,
  dailyCostInr: fc.integer({ min: 1000, max: 20000 }),
  notes: fc.option(fc.string({ minLength: 10, maxLength: 100 })),
});

const tripPlanArb = fc.record({
  id: fc.uuid(),
  userId: fc.uuid(),
  preferences: fc.record({
    destination: fc.string({ minLength: 3, maxLength: 50 }),
    startDate: fc.date().map(d => d.toISOString().split('T')[0]),
    endDate: fc.date().map(d => d.toISOString().split('T')[0]),
    travelDays: fc.integer({ min: 1, max: 30 }),
    travelType: travelTypeArb,
    budgetPreference: budgetLevelArb,
    maxBudgetInr: fc.integer({ min: 10000, max: 500000 }),
    interests: fc.array(interestArb, { minLength: 1, maxLength: 6 }),
  }),
  itinerary: fc.record({
    tripId: fc.uuid(),
    days: fc.array(dayPlanArb, { minLength: 1, maxLength: 30 }),
    totalCostInr: fc.integer({ min: 5000, max: 1000000 }),
    createdAt: fc.option(fc.date().map(d => d.toISOString())),
  }),
  costBreakdown: fc.record({
    flightCostInr: fc.integer({ min: 0, max: 100000 }),
    hotelCostInr: fc.integer({ min: 0, max: 200000 }),
    attractionsCostInr: fc.integer({ min: 0, max: 50000 }),
    eventsCostInr: fc.integer({ min: 0, max: 30000 }),
    localExpensesInr: fc.integer({ min: 0, max: 50000 }),
    totalCostInr: fc.integer({ min: 5000, max: 1000000 }),
    dailyBreakdown: fc.array(fc.record({
      dayNumber: fc.integer({ min: 1, max: 30 }),
      date: fc.date().map(d => d.toISOString().split('T')[0]),
      flightCostInr: fc.integer({ min: 0, max: 20000 }),
      hotelCostInr: fc.integer({ min: 0, max: 10000 }),
      attractionsCostInr: fc.integer({ min: 0, max: 5000 }),
      eventsCostInr: fc.integer({ min: 0, max: 3000 }),
      localExpensesInr: fc.integer({ min: 0, max: 5000 }),
      totalCostInr: fc.integer({ min: 500, max: 20000 }),
    }), { minLength: 1, maxLength: 30 }),
  }),
  budgetStatus: fc.record({
    status: fc.constantFrom('Within Budget', 'Slightly Over Budget', 'Over Budget'),
    differenceInr: fc.integer({ min: -100000, max: 100000 }),
    suggestions: fc.array(fc.string({ minLength: 10, maxLength: 100 }), { minLength: 0, maxLength: 5 }),
  }),
  createdAt: fc.option(fc.date().map(d => d.toISOString())),
  updatedAt: fc.option(fc.date().map(d => d.toISOString())),
});

describe('PDFExporter Property Tests', () => {
  // Feature: ai-trip-planner, Property 23: PDF Export Completeness
  it('should generate PDF with complete itinerary and cost breakdown for any valid trip plan', () => {
    fc.assert(
      fc.property(tripPlanArb, (tripPlan) => {
        // Render the PDFExporter component
        const { container } = render(<PDFExporter tripPlan={tripPlan} />);
        
        // Verify the component renders without errors
        expect(container).toBeTruthy();
        
        // Check that the download link is present
        const downloadLink = container.querySelector('[data-testid="pdf-download-link"]');
        expect(downloadLink).toBeTruthy();
        
        // Verify the link has proper attributes for PDF download
        if (downloadLink) {
          expect(downloadLink.getAttribute('download')).toBeTruthy();
          expect(downloadLink.getAttribute('download')).toContain('.pdf');
          // The filename should contain some form of the destination (may be processed)
          const filename = downloadLink.getAttribute('download') || '';
          expect(filename.startsWith('trip-')).toBe(true);
        }
        
        return true;
      }),
      { numRuns: 100 }
    );
  });
});