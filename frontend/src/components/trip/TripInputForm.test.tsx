import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TripInputForm from './TripInputForm';
import { TravelType, BudgetLevel, Interest } from '../../types/trip';

describe('TripInputForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders all form fields', () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    // Check for main form elements
    expect(screen.getByText('Plan Your Perfect Trip')).toBeInTheDocument();
    expect(screen.getByLabelText(/Destination/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Start Date/)).toBeInTheDocument();
    expect(screen.getByLabelText(/End Date/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Number of Travel Days/)).toBeInTheDocument();
    expect(screen.getByText('Travel Type *')).toBeInTheDocument();
    expect(screen.getByText('Budget Preference *')).toBeInTheDocument();
    expect(screen.getByLabelText(/Maximum Budget/)).toBeInTheDocument();
    expect(screen.getByText('Interests * (Select all that apply)')).toBeInTheDocument();
  });

  it('renders all travel type options', () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    Object.values(TravelType).forEach(type => {
      expect(screen.getByText(type)).toBeInTheDocument();
    });
  });

  it('renders all budget level options', () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    Object.values(BudgetLevel).forEach(level => {
      expect(screen.getByText(level.charAt(0).toUpperCase() + level.slice(1))).toBeInTheDocument();
    });
  });

  it('renders all interest options', () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    Object.values(Interest).forEach(interest => {
      expect(screen.getByText(interest.charAt(0).toUpperCase() + interest.slice(1))).toBeInTheDocument();
    });
  });

  it('shows validation errors for empty required fields', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByText('Create Trip Plan');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Destination is required')).toBeInTheDocument();
      expect(screen.getByText('Start date is required')).toBeInTheDocument();
      expect(screen.getByText('End date is required')).toBeInTheDocument();
      expect(screen.getByText('Maximum budget is required')).toBeInTheDocument();
      expect(screen.getByText('Please select at least one interest')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates destination length', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const destinationInput = screen.getByLabelText(/Destination/);
    fireEvent.change(destinationInput, { target: { value: 'A' } });

    const submitButton = screen.getByText('Create Trip Plan');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Destination must be at least 2 characters')).toBeInTheDocument();
    });
  });

  it('validates future start date', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const startDateInput = screen.getByLabelText(/Start Date/);
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayString = yesterday.toISOString().split('T')[0];
    
    fireEvent.change(startDateInput, { target: { value: yesterdayString } });

    const submitButton = screen.getByText('Create Trip Plan');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Start date must be in the future')).toBeInTheDocument();
    });
  });

  it('validates end date after start date', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 2);
    const tomorrowString = tomorrow.toISOString().split('T')[0];

    const dayAfterTomorrow = new Date();
    dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
    const dayAfterTomorrowString = dayAfterTomorrow.toISOString().split('T')[0];

    const startDateInput = screen.getByLabelText(/Start Date/);
    const endDateInput = screen.getByLabelText(/End Date/);
    
    fireEvent.change(startDateInput, { target: { value: tomorrowString } });
    fireEvent.change(endDateInput, { target: { value: dayAfterTomorrowString } });

    const submitButton = screen.getByText('Create Trip Plan');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('End date must be after start date')).toBeInTheDocument();
    });
  });

  it('formats budget input with INR currency', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const budgetInput = screen.getByLabelText(/Maximum Budget/);
    fireEvent.change(budgetInput, { target: { value: '50000' } });

    await waitFor(() => {
      expect(budgetInput).toHaveValue('₹50,000');
    });
  });

  it('allows selecting and deselecting interests', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const natureCheckbox = screen.getByLabelText(/Nature/i);
    const foodCheckbox = screen.getByLabelText(/Food/i);

    // Select interests
    fireEvent.click(natureCheckbox);
    fireEvent.click(foodCheckbox);

    expect(natureCheckbox).toBeChecked();
    expect(foodCheckbox).toBeChecked();

    // Deselect one interest
    fireEvent.click(natureCheckbox);
    expect(natureCheckbox).not.toBeChecked();
    expect(foodCheckbox).toBeChecked();
  });

  it('calculates travel days automatically from dates', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 4); // 3 days difference

    const startDateInput = screen.getByLabelText(/Start Date/);
    const endDateInput = screen.getByLabelText(/End Date/);
    const travelDaysInput = screen.getByLabelText(/Number of Travel Days/);

    fireEvent.change(startDateInput, { target: { value: startDate.toISOString().split('T')[0] } });
    fireEvent.change(endDateInput, { target: { value: endDate.toISOString().split('T')[0] } });

    await waitFor(() => {
      expect(travelDaysInput).toHaveValue(3);
    });
  });

  it('submits form with valid data', async () => {
    render(<TripInputForm onSubmit={mockOnSubmit} />);

    // Fill in all required fields
    const destinationInput = screen.getByLabelText(/Destination/);
    const startDateInput = screen.getByLabelText(/Start Date/);
    const endDateInput = screen.getByLabelText(/End Date/);
    const budgetInput = screen.getByLabelText(/Maximum Budget/);
    const natureCheckbox = screen.getByLabelText(/Nature/i);

    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1);
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 4);

    fireEvent.change(destinationInput, { target: { value: 'Paris, France' } });
    fireEvent.change(startDateInput, { target: { value: startDate.toISOString().split('T')[0] } });
    fireEvent.change(endDateInput, { target: { value: endDate.toISOString().split('T')[0] } });
    fireEvent.change(budgetInput, { target: { value: '50000' } });
    fireEvent.click(natureCheckbox);

    const submitButton = screen.getByText('Create Trip Plan');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          destination: 'Paris, France',
          startDate: startDate.toISOString().split('T')[0],
          endDate: endDate.toISOString().split('T')[0],
          travelDays: 3,
          travelType: TravelType.SOLO,
          budgetPreference: BudgetLevel.MEDIUM,
          maxBudgetInr: '₹50,000',
          interests: [Interest.NATURE]
        })
      );
    });
  });

  it('shows loading state when loading prop is true', () => {
    render(<TripInputForm onSubmit={mockOnSubmit} loading={true} />);

    const submitButton = screen.getByText('Creating Your Trip Plan...');
    expect(submitButton).toBeDisabled();

    // Check that form inputs are disabled
    const destinationInput = screen.getByLabelText(/Destination/);
    expect(destinationInput).toBeDisabled();
  });

  it('displays error message when error prop is provided', () => {
    const errorMessage = 'Something went wrong';
    render(<TripInputForm onSubmit={mockOnSubmit} error={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });
});