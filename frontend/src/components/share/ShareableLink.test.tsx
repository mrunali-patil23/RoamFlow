import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import ShareableLink from './ShareableLink';
import { TripPlan, TravelType, BudgetLevel, Interest, ActivityType } from '../../types/trip';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(() => Promise.resolve()),
  },
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    origin: 'https://example.com',
  },
  writable: true,
});

// Generators for property-based testing (reusing from PDFExporter test)
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

describe('ShareableLink Property Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Feature: ai-trip-planner, Property 24: Shareable Link Functionality
  it('should generate valid shareable links that contain complete trip information', async () => {
    await fc.assert(
      fc.asyncProperty(tripPlanArb, async (tripPlan) => {
        // Render the ShareableLink component
        const { container } = render(<ShareableLink tripPlan={tripPlan} />);
        
        // Click the generate link button
        const generateButton = container.querySelector('button');
        expect(generateButton).toBeTruthy();
        expect(generateButton?.textContent).toBe('Generate Shareable Link');
        
        fireEvent.click(generateButton!);
        
        // Wait for the link to be generated
        await waitFor(() => {
          const urlInput = container.querySelector('input[type="text"]') as HTMLInputElement;
          expect(urlInput).toBeTruthy();
          expect(urlInput.value).toBeTruthy();
          
          // Verify the URL structure
          const url = urlInput.value;
          expect(url.startsWith('https://example.com/shared-trip/')).toBe(true);
          
          // Extract and decode the trip data from the URL
          const encodedData = url.split('/shared-trip/')[1];
          expect(encodedData).toBeTruthy();
          
          try {
            const decodedData = atob(encodedData);
            const parsedTripPlan = JSON.parse(decodedData);
            
            // Verify that essential trip information is preserved
            expect(parsedTripPlan.id).toBe(tripPlan.id);
            expect(parsedTripPlan.preferences.destination).toBe(tripPlan.preferences.destination);
            expect(parsedTripPlan.preferences.travelDays).toBe(tripPlan.preferences.travelDays);
            expect(parsedTripPlan.itinerary.days.length).toBe(tripPlan.itinerary.days.length);
            expect(parsedTripPlan.costBreakdown.totalCostInr).toBe(tripPlan.costBreakdown.totalCostInr);
            
            return true;
          } catch (error) {
            throw new Error('Generated URL contains invalid or corrupted trip data');
          }
        });
        
        return true;
      }),
      { numRuns: 100 }
    );
  });
});