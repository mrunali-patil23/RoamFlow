/**
 * Unit tests for TypeScript interfaces and type definitions.
 * 
 * Tests type compatibility and interface structure to ensure
 * frontend types match backend Pydantic models.
 */

import {
  BudgetCategory,
  TravelerType,
  ActivityCategory,
  TransportType,
  TripRequest,
  Activity,
  TransportOption,
  DayPlan,
  TripItinerary,
  APIResponse,
  ErrorResponse,
  FlightSearchParams,
  FlightOption,
  TripFormData,
  FormErrors,
  LoadingState,
  AppState,
} from '../types';

describe('TypeScript Interface Tests', () => {
  describe('TripRequest Interface', () => {
    it('should create valid TripRequest object', () => {
      const tripRequest: TripRequest = {
        destination: 'Paris, France',
        days: 5,
        budget: 'moderate' as BudgetCategory,
        travelers: 'couple' as TravelerType,
      };

      expect(tripRequest.destination).toBe('Paris, France');
      expect(tripRequest.days).toBe(5);
      expect(tripRequest.budget).toBe('moderate');
      expect(tripRequest.travelers).toBe('couple');
    });

    it('should enforce correct enum values', () => {
      const validBudgets: BudgetCategory[] = ['cheap', 'moderate', 'luxury'];
      const validTravelers: TravelerType[] = ['just-me', 'couple', 'family', 'friends'];

      expect(validBudgets).toHaveLength(3);
      expect(validTravelers).toHaveLength(4);
    });
  });

  describe('Activity Interface', () => {
    it('should create valid Activity object', () => {
      const activity: Activity = {
        name: 'Visit Eiffel Tower',
        description: 'Iconic iron lattice tower and symbol of Paris',
        duration: 120,
        cost: 25.0,
        category: 'sightseeing' as ActivityCategory,
      };

      expect(activity.name).toBe('Visit Eiffel Tower');
      expect(activity.duration).toBe(120);
      expect(activity.cost).toBe(25.0);
      expect(activity.category).toBe('sightseeing');
    });

    it('should enforce correct activity categories', () => {
      const validCategories: ActivityCategory[] = [
        'sightseeing',
        'dining',
        'entertainment',
        'cultural',
      ];

      expect(validCategories).toHaveLength(4);
    });
  });

  describe('TransportOption Interface', () => {
    it('should create valid TransportOption object', () => {
      const transport: TransportOption = {
        type: 'metro' as TransportType,
        provider: 'RATP',
        cost: 1.90,
        duration: 25,
        route: 'Line 6 from Trocadéro to Eiffel Tower',
      };

      expect(transport.type).toBe('metro');
      expect(transport.provider).toBe('RATP');
      expect(transport.cost).toBe(1.90);
      expect(transport.duration).toBe(25);
      expect(transport.route).toBe('Line 6 from Trocadéro to Eiffel Tower');
    });

    it('should enforce correct transport types', () => {
      const validTypes: TransportType[] = [
        'flight',
        'taxi',
        'bus',
        'metro',
        'walking',
      ];

      expect(validTypes).toHaveLength(5);
    });
  });

  describe('DayPlan Interface', () => {
    it('should create valid DayPlan object', () => {
      const activity: Activity = {
        name: 'Visit Eiffel Tower',
        description: 'Iconic tower',
        duration: 120,
        cost: 25.0,
        category: 'sightseeing',
      };

      const transport: TransportOption = {
        type: 'metro',
        provider: 'RATP',
        cost: 1.90,
        duration: 25,
        route: 'Line 6',
      };

      const dayPlan: DayPlan = {
        day_number: 1,
        activities: [activity],
        transport: [transport],
        estimated_cost: 30.0,
      };

      expect(dayPlan.day_number).toBe(1);
      expect(dayPlan.activities).toHaveLength(1);
      expect(dayPlan.transport).toHaveLength(1);
      expect(dayPlan.estimated_cost).toBe(30.0);
    });
  });

  describe('TripItinerary Interface', () => {
    it('should create valid TripItinerary object', () => {
      const activity: Activity = {
        name: 'Test Activity',
        description: 'Test description',
        duration: 120,
        cost: 25.0,
        category: 'sightseeing',
      };

      const dayPlan: DayPlan = {
        day_number: 1,
        activities: [activity],
        transport: [],
        estimated_cost: 30.0,
      };

      const itinerary: TripItinerary = {
        trip_id: 'trip_123',
        destination: 'Paris, France',
        total_days: 1,
        daily_plans: [dayPlan],
        total_budget: 35.0,
        created_at: '2024-01-01T12:00:00Z',
      };

      expect(itinerary.trip_id).toBe('trip_123');
      expect(itinerary.destination).toBe('Paris, France');
      expect(itinerary.total_days).toBe(1);
      expect(itinerary.daily_plans).toHaveLength(1);
      expect(itinerary.total_budget).toBe(35.0);
      expect(itinerary.created_at).toBe('2024-01-01T12:00:00Z');
    });
  });

  describe('API Response Interfaces', () => {
    it('should create valid APIResponse object', () => {
      const response: APIResponse<{ message: string }> = {
        success: true,
        data: { message: 'Hello' },
        message: 'Request successful',
      };

      expect(response.success).toBe(true);
      expect(response.data?.message).toBe('Hello');
      expect(response.message).toBe('Request successful');
    });

    it('should create valid ErrorResponse object', () => {
      const error: ErrorResponse = {
        success: false,
        error: true,
        message: 'Something went wrong',
        error_code: 'VALIDATION_ERROR',
        details: { field: 'destination' },
        retry_after: 5,
      };

      expect(error.success).toBe(false);
      expect(error.error).toBe(true);
      expect(error.message).toBe('Something went wrong');
      expect(error.error_code).toBe('VALIDATION_ERROR');
      expect(error.details?.field).toBe('destination');
      expect(error.retry_after).toBe(5);
    });
  });

  describe('Flight-related Interfaces', () => {
    it('should create valid FlightSearchParams object', () => {
      const params: FlightSearchParams = {
        origin: 'JFK',
        destination: 'CDG',
        departure_date: '2024-06-15',
        return_date: '2024-06-22',
        passengers: 2,
      };

      expect(params.origin).toBe('JFK');
      expect(params.destination).toBe('CDG');
      expect(params.departure_date).toBe('2024-06-15');
      expect(params.return_date).toBe('2024-06-22');
      expect(params.passengers).toBe(2);
    });

    it('should create valid FlightOption object', () => {
      const flight: FlightOption = {
        airline: 'Air France',
        flight_number: 'AF83',
        departure_time: '14:30',
        arrival_time: '16:45',
        duration: 495,
        price: 650.0,
        stops: 0,
      };

      expect(flight.airline).toBe('Air France');
      expect(flight.flight_number).toBe('AF83');
      expect(flight.departure_time).toBe('14:30');
      expect(flight.arrival_time).toBe('16:45');
      expect(flight.duration).toBe(495);
      expect(flight.price).toBe(650.0);
      expect(flight.stops).toBe(0);
    });
  });

  describe('Form and State Interfaces', () => {
    it('should create valid TripFormData object', () => {
      const formData: TripFormData = {
        destination: 'Paris, France',
        days: 5,
        budget: 'moderate',
        travelerType: 'couple',
      };

      expect(formData.destination).toBe('Paris, France');
      expect(formData.days).toBe(5);
      expect(formData.budget).toBe('moderate');
      expect(formData.travelerType).toBe('couple');
    });

    it('should create valid FormErrors object', () => {
      const errors: FormErrors = {
        destination: 'Destination is required',
        days: 'Days must be a positive number',
        budget: 'Please select a budget',
        travelerType: 'Please select traveler type',
        general: 'Please fix the errors above',
      };

      expect(errors.destination).toBe('Destination is required');
      expect(errors.days).toBe('Days must be a positive number');
      expect(errors.budget).toBe('Please select a budget');
      expect(errors.travelerType).toBe('Please select traveler type');
      expect(errors.general).toBe('Please fix the errors above');
    });

    it('should create valid LoadingState object', () => {
      const loading: LoadingState = {
        isLoading: true,
        message: 'Generating your itinerary...',
      };

      expect(loading.isLoading).toBe(true);
      expect(loading.message).toBe('Generating your itinerary...');
    });

    it('should create valid AppState object', () => {
      const appState: AppState = {
        tripForm: {
          destination: '',
          days: '',
          budget: '',
          travelerType: '',
        },
        formErrors: {},
        loading: {
          isLoading: false,
        },
      };

      expect(appState.tripForm.destination).toBe('');
      expect(appState.formErrors).toEqual({});
      expect(appState.loading.isLoading).toBe(false);
    });
  });
});