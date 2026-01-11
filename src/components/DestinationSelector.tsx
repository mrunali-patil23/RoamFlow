'use client';

import { useState, useRef, useEffect } from 'react';

interface DestinationSelectorProps {
  value: string;
  onChange: (destination: string) => void;
  error?: string;
}

// Popular destinations list for dropdown
const POPULAR_DESTINATIONS = [
  'Paris, France',
  'Tokyo, Japan',
  'New York, USA',
  'London, England',
  'Rome, Italy',
  'Barcelona, Spain',
  'Amsterdam, Netherlands',
  'Berlin, Germany',
  'Sydney, Australia',
  'Bangkok, Thailand',
  'Istanbul, Turkey',
  'Dubai, UAE',
  'Singapore',
  'Hong Kong',
  'Los Angeles, USA',
  'San Francisco, USA',
  'Miami, USA',
  'Las Vegas, USA',
  'Prague, Czech Republic',
  'Vienna, Austria',
  'Budapest, Hungary',
  'Lisbon, Portugal',
  'Athens, Greece',
  'Cairo, Egypt',
  'Mumbai, India',
  'Delhi, India',
  'Seoul, South Korea',
  'Beijing, China',
  'Shanghai, China',
  'Melbourne, Australia'
];

export default function DestinationSelector({ value, onChange, error }: DestinationSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredDestinations, setFilteredDestinations] = useState(POPULAR_DESTINATIONS);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter destinations based on search term
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredDestinations(POPULAR_DESTINATIONS);
    } else {
      const filtered = POPULAR_DESTINATIONS.filter(destination =>
        destination.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredDestinations(filtered);
    }
  }, [searchTerm]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setSearchTerm(inputValue);
    onChange(inputValue);
    setIsOpen(true);
  };

  const handleDestinationSelect = (destination: string) => {
    onChange(destination);
    setSearchTerm(destination);
    setIsOpen(false);
  };

  const handleInputFocus = () => {
    setIsOpen(true);
    setSearchTerm(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      inputRef.current?.blur();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredDestinations.length > 0) {
        handleDestinationSelect(filteredDestinations[0]);
      }
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={searchTerm || value}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          className={`w-full px-4 py-3 pr-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Search destinations or type your own..."
          aria-label="Destination selection"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          role="combobox"
        />
        
        {/* Dropdown arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <svg
            className={`h-5 w-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">{error}</p>
      )}

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredDestinations.length > 0 ? (
            <ul role="listbox" className="py-1">
              {filteredDestinations.map((destination, index) => (
                <li
                  key={destination}
                  role="option"
                  aria-selected={destination === value}
                  className={`px-4 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 ${
                    destination === value ? 'bg-blue-100 text-blue-700' : 'text-gray-900'
                  }`}
                  onClick={() => handleDestinationSelect(destination)}
                >
                  {destination}
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-2 text-gray-500 text-sm">
              No destinations found. You can still type your own destination.
            </div>
          )}
        </div>
      )}
    </div>
  );
}