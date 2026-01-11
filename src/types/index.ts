// Type definitions for the AI Travel Planner application
// These interfaces match the backend Pydantic models for type-safe API communication

// Enums matching backend enums
export type BudgetCategory = 'cheap' | 'moderate' | 'luxury';
export type TravelerType = 'just-me' | 'couple' | 'family' | 'friends';
export type ActivityCategory = 'sightseeing' | 'dining' | 'entertainment' | 'cultural';
export type TransportType = 'flight' | 'taxi' | 'bus' | 'metro' | 'walking';

// Core trip models matching backend Pydantic models
export interface TripRequest {
  destination: string;
  days: number;
  budget: BudgetCategory;
  travelers: TravelerType;
}

export interface Activity {
  name: string;
  description: string;
  duration: number; // Duration in minutes
  cost: number; // Cost in USD
  category: ActivityCategory;
}

export interface TransportOption {
  type: TransportType;
  provider: string;
  cost: number; // Cost in USD
  duration: number; // Duration in minutes
  route: string;
}

export interface DayPlan {
  day_number: number;
  activities: Activity[];
  transport: TransportOption[];
  estimated_cost: number; // Total estimated cost for the day in USD
}

export interface TripItinerary {
  trip_id: string;
  destination: string;
  total_days: number;
  daily_plans: DayPlan[];
  total_budget: number; // Total estimated budget in USD
  created_at?: string; // ISO datetime string
}

// API-specific interfaces matching backend API models
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

export interface ErrorResponse {
  success: false;
  error: true;
  message: string;
  error_code: string;
  details?: Record<string, any>;
  retry_after?: number;
}

export interface FlightSearchParams {
  origin: string; // IATA airport code
  destination: string; // IATA airport code
  departure_date: string; // YYYY-MM-DD format
  return_date?: string; // YYYY-MM-DD format
  passengers: number;
}

export interface FlightOption {
  airline: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration: number; // Duration in minutes
  price: number; // Price in USD
  stops: number;
}

export interface FlightOptions {
  flights: FlightOption[];
  search_params: FlightSearchParams;
}

export interface TransportRequest {
  location: string;
  transport_type?: string;
}

export interface TransportOptions {
  location: string;
  options: Array<{
    type: string;
    provider: string;
    [key: string]: any; // Additional properties like cost_per_ride, base_fare, etc.
  }>;
}

// Form-specific interfaces for frontend state management
export interface TripFormData {
  destination: string;
  days: number | '';
  budget: BudgetCategory | '';
  travelerType: TravelerType | '';
}

export interface FormErrors {
  destination?: string;
  days?: string;
  budget?: string;
  travelerType?: string;
  general?: string;
}

// UI state interfaces
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface AppState {
  tripForm: TripFormData;
  formErrors: FormErrors;
  loading: LoadingState;
  currentItinerary?: TripItinerary;
  error?: ErrorResponse;
}

// Legacy interface for backward compatibility (can be removed later)
export interface TripPreferences {
  destination: string;
  days: number;
  budget: BudgetCategory;
  travelerType: TravelerType;
}