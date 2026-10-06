import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  width?: string;
  height?: string;
  rounded?: boolean;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  width = 'w-full',
  height = 'h-4',
  rounded = true
}) => {
  const baseClasses = `animate-pulse bg-gray-300 dark:bg-gray-600 ${width} ${height}`;
  const roundedClasses = rounded ? 'rounded' : '';
  
  return (
    <div className={`${baseClasses} ${roundedClasses} ${className}`} />
  );
};

// Specific skeleton components for common use cases
export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({ 
  lines = 3, 
  className = '' 
}) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <SkeletonLoader
        key={index}
        width={index === lines - 1 ? 'w-3/4' : 'w-full'}
        height="h-4"
      />
    ))}
  </div>
);

export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
    <SkeletonLoader width="w-3/4" height="h-6" className="mb-4" />
    <SkeletonText lines={3} className="mb-4" />
    <div className="flex space-x-4">
      <SkeletonLoader width="w-20" height="h-8" />
      <SkeletonLoader width="w-24" height="h-8" />
    </div>
  </div>
);

export const SkeletonButton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <SkeletonLoader
    width="w-24"
    height="h-10"
    className={`rounded-md ${className}`}
  />
);

export const SkeletonAvatar: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };
  
  return (
    <SkeletonLoader
      width={sizeClasses[size]}
      height={sizeClasses[size]}
      className={`rounded-full ${className}`}
    />
  );
};

export const SkeletonTable: React.FC<{ rows?: number; columns?: number; className?: string }> = ({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) => (
  <div className={`space-y-4 ${className}`}>
    {/* Table header */}
    <div className="grid grid-cols-4 gap-4">
      {Array.from({ length: columns }).map((_, index) => (
        <SkeletonLoader key={`header-${index}`} width="w-full" height="h-6" />
      ))}
    </div>
    
    {/* Table rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={`row-${rowIndex}`} className="grid grid-cols-4 gap-4">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <SkeletonLoader key={`cell-${rowIndex}-${colIndex}`} width="w-full" height="h-4" />
        ))}
      </div>
    ))}
  </div>
);

export const SkeletonItinerary: React.FC<{ days?: number; className?: string }> = ({ 
  days = 3, 
  className = '' 
}) => (
  <div className={`space-y-6 ${className}`}>
    {Array.from({ length: days }).map((_, dayIndex) => (
      <div key={`day-${dayIndex}`} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        {/* Day header */}
        <SkeletonLoader width="w-48" height="h-6" className="mb-4" />
        
        {/* Weather info */}
        <div className="flex items-center space-x-4 mb-4">
          <SkeletonLoader width="w-16" height="h-16" className="rounded-full" />
          <div className="space-y-2">
            <SkeletonLoader width="w-32" height="h-4" />
            <SkeletonLoader width="w-24" height="h-4" />
          </div>
        </div>
        
        {/* Activities */}
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, activityIndex) => (
            <div key={`activity-${dayIndex}-${activityIndex}`} className="border-l-4 border-blue-500 pl-4">
              <SkeletonLoader width="w-40" height="h-5" className="mb-2" />
              <SkeletonText lines={2} />
              <div className="flex space-x-4 mt-2">
                <SkeletonLoader width="w-16" height="h-4" />
                <SkeletonLoader width="w-20" height="h-4" />
              </div>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
);

export default SkeletonLoader;