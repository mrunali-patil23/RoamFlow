import React, { useState, useEffect } from 'react';
import { TripFormData, TravelType, BudgetLevel, Interest, ValidationErrors } from '../../types/trip';

interface TripInputFormProps {
  onSubmit: (tripData: TripFormData) => void;
  loading?: boolean;
  error?: string | null;
}

const TripInputForm: React.FC<TripInputFormProps> = ({ onSubmit, loading = false, error = null }) => {
  const [formData, setFormData] = useState<TripFormData>({
    destination: '',
    startDate: '',
    endDate: '',
    travelDays: 1,
    travelType: TravelType.SOLO,
    budgetPreference: BudgetLevel.MEDIUM,
    maxBudgetInr: '',
    interests: []
  });

  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  // Calculate travel days when dates change
  useEffect(() => {
    if (formData.startDate && formData.endDate) {
      const start = new Date(formData.startDate);
      const end = new Date(formData.endDate);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays > 0 && diffDays !== formData.travelDays) {
        setFormData(prev => ({ ...prev, travelDays: diffDays }));
      }
    }
  }, [formData.startDate, formData.endDate]);

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Destination validation
    if (!formData.destination.trim()) {
      errors.destination = 'Destination is required';
    } else if (formData.destination.trim().length < 2) {
      errors.destination = 'Destination must be at least 2 characters';
    }

    // Date validation
    if (!formData.startDate) {
      errors.startDate = 'Start date is required';
    } else {
      const startDate = new Date(formData.startDate);
      if (startDate < today) {
        errors.startDate = 'Start date must be in the future';
      }
    }

    if (!formData.endDate) {
      errors.endDate = 'End date is required';
    } else if (formData.startDate) {
      const startDate = new Date(formData.startDate);
      const endDate = new Date(formData.endDate);
      if (endDate <= startDate) {
        errors.endDate = 'End date must be after start date';
      }
    }

    // Travel days validation
    if (formData.travelDays <= 0) {
      errors.travelDays = 'Travel days must be positive';
    } else if (formData.travelDays > 365) {
      errors.travelDays = 'Travel days cannot exceed 365';
    }

    // Budget validation
    if (!formData.maxBudgetInr.trim()) {
      errors.maxBudgetInr = 'Maximum budget is required';
    } else {
      const budget = parseFloat(formData.maxBudgetInr.replace(/[₹,\s]/g, ''));
      if (isNaN(budget) || budget <= 0) {
        errors.maxBudgetInr = 'Budget must be a positive number';
      } else if (budget > 10000000) {
        errors.maxBudgetInr = 'Budget cannot exceed ₹1,00,00,000';
      }
    }

    // Interests validation
    if (formData.interests.length === 0) {
      errors.interests = 'Please select at least one interest';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    onSubmit(formData);
  };

  const handleInputChange = (field: keyof TripFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleInterestToggle = (interest: Interest) => {
    const newInterests = formData.interests.includes(interest)
      ? formData.interests.filter(i => i !== interest)
      : [...formData.interests, interest];
    
    handleInputChange('interests', newInterests);
  };

  const formatBudgetInput = (value: string) => {
    // Remove all non-numeric characters except decimal point
    const numericValue = value.replace(/[^\d.]/g, '');
    
    // Parse and format with Indian number system
    const number = parseFloat(numericValue);
    if (isNaN(number)) return '';
    
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(number);
  };

  const handleBudgetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value;
    const formattedValue = formatBudgetInput(rawValue);
    handleInputChange('maxBudgetInr', formattedValue);
  };

  // Get today's date in YYYY-MM-DD format for min date
  const getTodayDate = () => {
    const today = new Date();
    today.setDate(today.getDate() + 1); // Tomorrow as minimum
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg px-8 pt-6 pb-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white text-center">
            Plan Your Perfect Trip
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-center mt-2">
            Tell us about your travel preferences and we'll create an amazing itinerary for you
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Destination */}
          <div>
            <label htmlFor="destination" className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Destination *
            </label>
            <input
              id="destination"
              type="text"
              value={formData.destination}
              onChange={(e) => handleInputChange('destination', e.target.value)}
              className={`shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                validationErrors.destination ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="e.g., Paris, France or Tokyo, Japan"
              disabled={loading}
            />
            {validationErrors.destination && (
              <p className="text-red-500 text-xs italic mt-1">{validationErrors.destination}</p>
            )}
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="startDate" className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                Start Date *
              </label>
              <input
                id="startDate"
                type="date"
                value={formData.startDate}
                onChange={(e) => handleInputChange('startDate', e.target.value)}
                min={getTodayDate()}
                className={`shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  validationErrors.startDate ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                disabled={loading}
              />
              {validationErrors.startDate && (
                <p className="text-red-500 text-xs italic mt-1">{validationErrors.startDate}</p>
              )}
            </div>

            <div>
              <label htmlFor="endDate" className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
                End Date *
              </label>
              <input
                id="endDate"
                type="date"
                value={formData.endDate}
                onChange={(e) => handleInputChange('endDate', e.target.value)}
                min={formData.startDate || getTodayDate()}
                className={`shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  validationErrors.endDate ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                disabled={loading}
              />
              {validationErrors.endDate && (
                <p className="text-red-500 text-xs italic mt-1">{validationErrors.endDate}</p>
              )}
            </div>
          </div>

          {/* Travel Days */}
          <div>
            <label htmlFor="travelDays" className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Number of Travel Days *
            </label>
            <input
              id="travelDays"
              type="number"
              value={formData.travelDays}
              onChange={(e) => handleInputChange('travelDays', parseInt(e.target.value) || 1)}
              min="1"
              max="365"
              className={`shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                validationErrors.travelDays ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              disabled={loading}
            />
            {validationErrors.travelDays && (
              <p className="text-red-500 text-xs italic mt-1">{validationErrors.travelDays}</p>
            )}
            <p className="text-gray-500 text-xs mt-1">
              This will be automatically calculated based on your selected dates
            </p>
          </div>

          {/* Travel Type */}
          <div>
            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Travel Type *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.values(TravelType).map((type) => (
                <label
                  key={type}
                  className={`flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    formData.travelType === type
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                  } ${loading ? 'cursor-not-allowed opacity-50' : ''}`}
                >
                  <input
                    type="radio"
                    name="travelType"
                    value={type}
                    checked={formData.travelType === type}
                    onChange={(e) => handleInputChange('travelType', e.target.value as TravelType)}
                    className="sr-only"
                    disabled={loading}
                  />
                  <span className="text-sm font-medium">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Budget Preference */}
          <div>
            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Budget Preference *
            </label>
            <div className="grid grid-cols-3 gap-3">
              {Object.values(BudgetLevel).map((level) => (
                <label
                  key={level}
                  className={`flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    formData.budgetPreference === level
                      ? 'border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                  } ${loading ? 'cursor-not-allowed opacity-50' : ''}`}
                >
                  <input
                    type="radio"
                    name="budgetPreference"
                    value={level}
                    checked={formData.budgetPreference === level}
                    onChange={(e) => handleInputChange('budgetPreference', e.target.value as BudgetLevel)}
                    className="sr-only"
                    disabled={loading}
                  />
                  <span className="text-sm font-medium capitalize">{level}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Maximum Budget */}
          <div>
            <label htmlFor="maxBudget" className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Maximum Budget (₹ INR) *
            </label>
            <input
              id="maxBudget"
              type="text"
              value={formData.maxBudgetInr}
              onChange={handleBudgetChange}
              className={`shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                validationErrors.maxBudgetInr ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="₹50,000"
              disabled={loading}
            />
            {validationErrors.maxBudgetInr && (
              <p className="text-red-500 text-xs italic mt-1">{validationErrors.maxBudgetInr}</p>
            )}
            <p className="text-gray-500 text-xs mt-1">
              Enter your maximum budget in Indian Rupees
            </p>
          </div>

          {/* Interests */}
          <div>
            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Interests * (Select all that apply)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.values(Interest).map((interest) => (
                <label
                  key={interest}
                  className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                    formData.interests.includes(interest)
                      ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                  } ${loading ? 'cursor-not-allowed opacity-50' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={formData.interests.includes(interest)}
                    onChange={() => handleInterestToggle(interest)}
                    className="mr-2"
                    disabled={loading}
                  />
                  <span className="text-sm font-medium capitalize">{interest}</span>
                </label>
              ))}
            </div>
            {validationErrors.interests && (
              <p className="text-red-500 text-xs italic mt-1">{validationErrors.interests}</p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center pt-6">
            <button
              type="submit"
              disabled={loading}
              className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg focus:outline-none focus:shadow-outline transition-colors ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Creating Your Trip Plan...' : 'Create Trip Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TripInputForm;