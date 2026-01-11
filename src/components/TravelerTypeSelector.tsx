'use client';

import { TravelerType } from '@/types';

interface TravelerTypeSelectorProps {
  value: TravelerType | '';
  onChange: (travelerType: TravelerType) => void;
  error?: string;
}

interface TravelerOption {
  value: TravelerType;
  label: string;
  description: string;
  icon: string;
}

const TRAVELER_OPTIONS: TravelerOption[] = [
  {
    value: 'just-me',
    label: 'Just Me',
    description: 'Solo travel, flexible schedule',
    icon: '🧳'
  },
  {
    value: 'couple',
    label: 'Couple',
    description: 'Romantic getaway, shared experiences',
    icon: '💕'
  },
  {
    value: 'family',
    label: 'Family',
    description: 'Family-friendly activities, kid-safe options',
    icon: '👨‍👩‍👧‍👦'
  },
  {
    value: 'friends',
    label: 'Friends',
    description: 'Group activities, nightlife, adventures',
    icon: '👥'
  }
];

export default function TravelerTypeSelector({ value, onChange, error }: TravelerTypeSelectorProps) {
  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {TRAVELER_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              value === option.value
                ? 'border-black bg-gray-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            aria-pressed={value === option.value}
            aria-label={`Select ${option.label} traveler type`}
          >
            <div className="text-center">
              <span className="text-3xl block mb-2" role="img" aria-hidden="true">
                {option.icon}
              </span>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {option.label}
              </h3>
              <p className="text-sm text-gray-600">
                {option.description}
              </p>
            </div>
            
            {/* Selection indicator */}
            {value === option.value && (
              <div className="mt-3 flex items-center justify-center text-sm text-gray-700">
                <svg className="w-4 h-4 mr-1 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Selected
              </div>
            )}
          </button>
        ))}
      </div>
      
      {/* Error message */}
      {error && (
        <p className="mt-2 text-sm text-red-600" role="alert">{error}</p>
      )}
    </div>
  );
}