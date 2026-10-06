import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ItineraryDisplay, CostBreakdown, BudgetStatus } from './index';
import { TripPlan, ActivityType, TravelType, BudgetLevel, Interest } from '../../types/trip';

// Mock data for testing
const mockTripPlan: TripPlan = {
  id: 'test-trip-1',
  userId: 'user-1',
  preferences: {
    destination: 'Paris, France',
    startDate: '2024-06-01',
    endDate: '2024-06-05',
    travelDays: 4,
    travelType: TravelType.COUPLE,
    budgetPreference: BudgetLevel.MEDIUM,
    maxBudgetInr: 150000,
    interests: [Interest.CULTURE, Interest.FOOD, Interest.NATURE]
  },
  itinerary: {
    tripId: 'test-trip-1',
    days: [
      {
        dayNumber: 1,
        date: '2024-06-01',
        activities: [
          {
            name: 'Eiffel Tower Visit',
            activityType: ActivityType.ATTRACTION,
            description: 'Visit the iconic Eiffel Tower and enjoy panoramic views of Paris.',
            durationHours: 3,
            costInr: 2500,
            location: 'Champ de Mars, Paris',
            rating: 4.8,
            bookingRequired: false
          }
        ],
        weather: {
          date: '2024-06-01',
          temperatureHigh: 22,
          temperatureLow: 15,
          condition: 'Partly Cloudy',
          description: 'Pleasant weather with some clouds',
          humidity: 65,
          precipitationChance: 20
        },
        dailyCostInr: 5000
      }
    ],
    totalCostInr: 120000
  },
  costBreakdown: {
    flightCostInr: 60000,
    hotelCostInr: 40000,
    attractionsCostInr: 15000,
    eventsCostInr: 5000,
    localExpensesInr: 10000,
    totalCostInr: 130000,
    dailyBreakdown: [
      {
        dayNumber: 1,
        date: '2024-06-01',
        flightCostInr: 60000,
        hotelCostInr: 10000,
        attractionsCostInr: 2500,
        eventsCostInr: 0,
        localExpensesInr: 2500,
        totalCostInr: 75000
      }
    ]
  },
  budgetStatus: {
    status: 'Within Budget',
    differenceInr: -20000,
    suggestions: []
  },
  createdAt: '2024-05-01T10:00:00Z'
};

describe('Trip Display Components', () => {
  describe('ItineraryDisplay', () => {
    it('should render itinerary with trip details', () => {
      render(<ItineraryDisplay itinerary={mockTripPlan.itinerary} />);
      
      expect(screen.getByText('Your Trip Itinerary')).toBeInTheDocument();
      expect(screen.getByText('Day 1')).toBeInTheDocument();
      expect(screen.getByText('Eiffel Tower Visit')).toBeInTheDocument();
      expect(screen.getByText('Partly Cloudy')).toBeInTheDocument();
    });

    it('should display weather information correctly', () => {
      render(<ItineraryDisplay itinerary={mockTripPlan.itinerary} />);
      
      expect(screen.getByText('22° / 15°')).toBeInTheDocument();
      expect(screen.getByText('💧 65%')).toBeInTheDocument();
      expect(screen.getByText('🌧️ 20%')).toBeInTheDocument();
    });

    it('should show activity details with cost and duration', () => {
      render(<ItineraryDisplay itinerary={mockTripPlan.itinerary} />);
      
      expect(screen.getByText('₹2,500')).toBeInTheDocument();
      expect(screen.getAllByText('3h')).toHaveLength(2); // One in summary, one in activity
      expect(screen.getByText('⭐ 4.8')).toBeInTheDocument();
    });
  });

  describe('CostBreakdown', () => {
    it('should render cost breakdown with all categories', () => {
      render(<CostBreakdown costBreakdown={mockTripPlan.costBreakdown} />);
      
      expect(screen.getByText('Cost Breakdown')).toBeInTheDocument();
      expect(screen.getByText('₹1,30,000')).toBeInTheDocument();
      expect(screen.getByText('Flights')).toBeInTheDocument();
      expect(screen.getByText('Hotels')).toBeInTheDocument();
      expect(screen.getByText('Attractions')).toBeInTheDocument();
    });

    it('should show section-wise and daily views', () => {
      render(<CostBreakdown costBreakdown={mockTripPlan.costBreakdown} />);
      
      expect(screen.getByText('Section-wise')).toBeInTheDocument();
      expect(screen.getByText('Day-wise')).toBeInTheDocument();
    });

    it('should display cost percentages correctly', () => {
      render(<CostBreakdown costBreakdown={mockTripPlan.costBreakdown} />);
      
      // Flight cost should be 46.2% of total (60000/130000)
      expect(screen.getByText('46.2% of total')).toBeInTheDocument();
    });
  });

  describe('BudgetStatus', () => {
    it('should render budget status with correct styling', () => {
      render(
        <BudgetStatus 
          budgetStatus={mockTripPlan.budgetStatus}
          maxBudget={mockTripPlan.preferences.maxBudgetInr}
          totalCost={mockTripPlan.costBreakdown.totalCostInr}
        />
      );
      
      expect(screen.getByText('Within Budget')).toBeInTheDocument();
      expect(screen.getAllByText('₹20,000')).toHaveLength(2); // One in header, one in breakdown
      expect(screen.getByText('Under Budget')).toBeInTheDocument();
    });

    it('should show budget breakdown correctly', () => {
      render(
        <BudgetStatus 
          budgetStatus={mockTripPlan.budgetStatus}
          maxBudget={mockTripPlan.preferences.maxBudgetInr}
          totalCost={mockTripPlan.costBreakdown.totalCostInr}
        />
      );
      
      expect(screen.getAllByText('₹1,50,000')).toHaveLength(2); // One in progress bar, one in breakdown
      expect(screen.getByText('₹1,30,000')).toBeInTheDocument(); // Estimated cost
    });

    it('should display budget usage percentage', () => {
      render(
        <BudgetStatus 
          budgetStatus={mockTripPlan.budgetStatus}
          maxBudget={mockTripPlan.preferences.maxBudgetInr}
          totalCost={mockTripPlan.costBreakdown.totalCostInr}
        />
      );
      
      // 130000/150000 = 86.7%
      expect(screen.getByText('86.7%')).toBeInTheDocument();
    });
  });
});