-- Migration: Create trip plans, itineraries, and cost breakdowns tables
-- This migration creates the complete schema for trip planning data persistence

-- Create trip_plans table
CREATE TABLE IF NOT EXISTS trip_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    destination VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    travel_days INTEGER NOT NULL,
    travel_type VARCHAR(20) NOT NULL,
    budget_preference VARCHAR(10) NOT NULL,
    max_budget_inr DECIMAL(10,2) NOT NULL,
    interests JSONB NOT NULL,
    total_cost_inr DECIMAL(10,2) NOT NULL,
    budget_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT trip_plans_travel_days_positive CHECK (travel_days > 0),
    CONSTRAINT trip_plans_max_budget_positive CHECK (max_budget_inr > 0),
    CONSTRAINT trip_plans_total_cost_positive CHECK (total_cost_inr >= 0),
    CONSTRAINT trip_plans_start_before_end CHECK (start_date < end_date),
    CONSTRAINT trip_plans_travel_type_valid CHECK (travel_type IN ('Solo', 'Friends', 'Family', 'Couple')),
    CONSTRAINT trip_plans_budget_preference_valid CHECK (budget_preference IN ('low', 'medium', 'high')),
    CONSTRAINT trip_plans_budget_status_valid CHECK (budget_status IN ('Within Budget', 'Slightly Over Budget', 'Over Budget'))
);

-- Create itineraries table for day-by-day data
CREATE TABLE IF NOT EXISTS itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_plan_id UUID REFERENCES trip_plans(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    date DATE NOT NULL,
    activities JSONB NOT NULL,
    weather_info JSONB NOT NULL,
    daily_cost_inr DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT itineraries_day_number_positive CHECK (day_number > 0),
    CONSTRAINT itineraries_daily_cost_positive CHECK (daily_cost_inr >= 0),
    CONSTRAINT itineraries_unique_day_per_trip UNIQUE (trip_plan_id, day_number)
);

-- Create cost_breakdowns table for cost analysis
CREATE TABLE IF NOT EXISTS cost_breakdowns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_plan_id UUID REFERENCES trip_plans(id) ON DELETE CASCADE,
    flight_cost_inr DECIMAL(10,2) NOT NULL,
    hotel_cost_inr DECIMAL(10,2) NOT NULL,
    attractions_cost_inr DECIMAL(10,2) NOT NULL,
    events_cost_inr DECIMAL(10,2) NOT NULL,
    local_expenses_inr DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT cost_breakdowns_flight_cost_positive CHECK (flight_cost_inr >= 0),
    CONSTRAINT cost_breakdowns_hotel_cost_positive CHECK (hotel_cost_inr >= 0),
    CONSTRAINT cost_breakdowns_attractions_cost_positive CHECK (attractions_cost_inr >= 0),
    CONSTRAINT cost_breakdowns_events_cost_positive CHECK (events_cost_inr >= 0),
    CONSTRAINT cost_breakdowns_local_expenses_positive CHECK (local_expenses_inr >= 0),
    CONSTRAINT cost_breakdowns_unique_per_trip UNIQUE (trip_plan_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trip_plans_user_id ON trip_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_trip_plans_destination ON trip_plans(destination);
CREATE INDEX IF NOT EXISTS idx_trip_plans_start_date ON trip_plans(start_date);
CREATE INDEX IF NOT EXISTS idx_trip_plans_created_at ON trip_plans(created_at);

CREATE INDEX IF NOT EXISTS idx_itineraries_trip_plan_id ON itineraries(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_date ON itineraries(date);
CREATE INDEX IF NOT EXISTS idx_itineraries_day_number ON itineraries(day_number);

CREATE INDEX IF NOT EXISTS idx_cost_breakdowns_trip_plan_id ON cost_breakdowns(trip_plan_id);

-- Create updated_at trigger for trip_plans
CREATE TRIGGER update_trip_plans_updated_at 
    BEFORE UPDATE ON trip_plans 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE trip_plans IS 'Main trip planning data with user preferences and summary information';
COMMENT ON COLUMN trip_plans.id IS 'Unique trip plan identifier (UUID)';
COMMENT ON COLUMN trip_plans.user_id IS 'Reference to the user who created this trip plan';
COMMENT ON COLUMN trip_plans.destination IS 'Trip destination city/country';
COMMENT ON COLUMN trip_plans.start_date IS 'Trip start date';
COMMENT ON COLUMN trip_plans.end_date IS 'Trip end date';
COMMENT ON COLUMN trip_plans.travel_days IS 'Number of travel days';
COMMENT ON COLUMN trip_plans.travel_type IS 'Type of travel: Solo, Friends, Family, Couple';
COMMENT ON COLUMN trip_plans.budget_preference IS 'Budget preference: low, medium, high';
COMMENT ON COLUMN trip_plans.max_budget_inr IS 'Maximum budget in Indian Rupees';
COMMENT ON COLUMN trip_plans.interests IS 'JSON array of user interests';
COMMENT ON COLUMN trip_plans.total_cost_inr IS 'Total calculated trip cost in Indian Rupees';
COMMENT ON COLUMN trip_plans.budget_status IS 'Budget status classification';

COMMENT ON TABLE itineraries IS 'Day-by-day itinerary data for trip plans';
COMMENT ON COLUMN itineraries.id IS 'Unique itinerary entry identifier (UUID)';
COMMENT ON COLUMN itineraries.trip_plan_id IS 'Reference to the parent trip plan';
COMMENT ON COLUMN itineraries.day_number IS 'Day number in the trip sequence';
COMMENT ON COLUMN itineraries.date IS 'Specific date for this day';
COMMENT ON COLUMN itineraries.activities IS 'JSON array of activities for this day';
COMMENT ON COLUMN itineraries.weather_info IS 'JSON object with weather information';
COMMENT ON COLUMN itineraries.daily_cost_inr IS 'Estimated cost for this day in Indian Rupees';

COMMENT ON TABLE cost_breakdowns IS 'Detailed cost breakdown by category for trip plans';
COMMENT ON COLUMN cost_breakdowns.id IS 'Unique cost breakdown identifier (UUID)';
COMMENT ON COLUMN cost_breakdowns.trip_plan_id IS 'Reference to the parent trip plan';
COMMENT ON COLUMN cost_breakdowns.flight_cost_inr IS 'Flight costs in Indian Rupees';
COMMENT ON COLUMN cost_breakdowns.hotel_cost_inr IS 'Hotel costs in Indian Rupees';
COMMENT ON COLUMN cost_breakdowns.attractions_cost_inr IS 'Attractions costs in Indian Rupees';
COMMENT ON COLUMN cost_breakdowns.events_cost_inr IS 'Events costs in Indian Rupees';
COMMENT ON COLUMN cost_breakdowns.local_expenses_inr IS 'Local expenses in Indian Rupees';