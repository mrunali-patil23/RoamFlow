/**
 * TypeScript interfaces for trip planning data structures.
 * These interfaces mirror the Python data models for type safety.
 */

export enum TravelType {
  SOLO = "Solo",
  FRIENDS = "Friends",
  FAMILY = "Family",
  COUPLE = "Couple"
}

export enum BudgetLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high"
}

export enum Interest {
  NATURE = "nature",
  FOOD = "food",
  ADVENTURE = "adventure",
  CULTURE = "culture",
  SHOPPING = "shopping",
  NIGHTLIFE = "nightlife"
}

export enum ActivityType {
  ATTRACTION = "attraction",
  EVENT = "event",
  MEAL = "meal",
  TRANSPORT = "transport",
  ACCOMMODATION = "accommodation",
  FREE_TIME = "free_time"
}

export interface TripPreferences {
  destination: string;
  startDate: string; // ISO date string
  endDate: string; // ISO date string
  travelDays: number;
  travelType: TravelType;
  budgetPreference: BudgetLevel;
  maxBudgetInr: number;
  interests: Interest[];
}

export interface TripFormData {
  destination: string;
  startDate: string;
  endDate: string;
  travelDays: number;
  travelType: TravelType;
  budgetPreference: BudgetLevel;
  maxBudgetInr: string; // String for form input handling
  interests: Interest[];
}

export interface ValidationErrors {
  [key: string]: string;
}

export interface WeatherInfo {
  date: string; // ISO date string
  temperatureHigh?: number;
  temperatureLow?: number;
  condition: string;
  description: string;
  humidity?: number;
  precipitationChance?: number;
}

export interface Activity {
  name: string;
  activityType: ActivityType;
  description: string;
  durationHours: number;
  costInr: number;
  location?: string;
  rating?: number;
  startTime?: string;
  endTime?: string;
  bookingRequired: boolean;
  sourceData?: any;
}

export interface DayPlan {
  dayNumber: number;
  date: string; // ISO date string
  activities: Activity[];
  weather: WeatherInfo;
  dailyCostInr: number;
  notes?: string;
}

export interface Itinerary {
  tripId: string;
  days: DayPlan[];
  totalCostInr: number;
  createdAt?: string;
}

export interface DailyCost {
  dayNumber: number;
  date: string; // ISO date string
  flightCostInr: number;
  hotelCostInr: number;
  attractionsCostInr: number;
  eventsCostInr: number;
  localExpensesInr: number;
  totalCostInr: number;
}

export interface CostBreakdown {
  flightCostInr: number;
  hotelCostInr: number;
  attractionsCostInr: number;
  eventsCostInr: number;
  localExpensesInr: number;
  totalCostInr: number;
  dailyBreakdown: DailyCost[];
}

export interface BudgetStatus {
  status: string; // "Within Budget", "Slightly Over Budget", "Over Budget"
  differenceInr: number;
  suggestions: string[];
}

export interface TripPlan {
  id: string;
  userId: string;
  preferences: TripPreferences;
  itinerary: Itinerary;
  costBreakdown: CostBreakdown;
  budgetStatus: BudgetStatus;
  createdAt?: string;
  updatedAt?: string;
}