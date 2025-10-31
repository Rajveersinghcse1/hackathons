import React from 'react';

const StatCard = ({ 
  title, 
  value, 
  trend, 
  trendDirection, 
  icon, 
  color = 'blue',
  description,
  onClick,
  isClickable = false,
  size = 'md'
}) => {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-500',
      text: 'text-blue-600',
      light: 'bg-blue-50',
      border: 'border-blue-200'
    },
    green: {
      bg: 'bg-green-500',
      text: 'text-green-600',
      light: 'bg-green-50',
      border: 'border-green-200'
    },
    purple: {
      bg: 'bg-purple-500',
      text: 'text-purple-600',
      light: 'bg-purple-50',
      border: 'border-purple-200'
    },
    orange: {
      bg: 'bg-orange-500',
      text: 'text-orange-600',
      light: 'bg-orange-50',
      border: 'border-orange-200'
    },
    red: {
      bg: 'bg-red-500',
      text: 'text-red-600',
      light: 'bg-red-50',
      border: 'border-red-200'
    },
    indigo: {
      bg: 'bg-indigo-500',
      text: 'text-indigo-600',
      light: 'bg-indigo-50',
      border: 'border-indigo-200'
    }
  };

  const sizeClasses = {
    sm: {
      padding: 'p-4',
      iconSize: 'w-8 h-8',
      valueText: 'text-xl',
      titleText: 'text-xs'
    },
    md: {
      padding: 'p-6',
      iconSize: 'w-12 h-12',
      valueText: 'text-3xl',
      titleText: 'text-sm'
    },
    lg: {
      padding: 'p-8',
      iconSize: 'w-16 h-16',
      valueText: 'text-4xl',
      titleText: 'text-base'
    }
  };

  const colors = colorClasses[color] || colorClasses.blue; // Fallback to blue if color doesn't exist
  const sizes = sizeClasses[size] || sizeClasses.md; // Fallback to md if size doesn't exist

  const getTrendIcon = () => {
    if (trendDirection === 'up') {
      return (
        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" transform="rotate(90 12 12)" />
        </svg>
      );
    } else if (trendDirection === 'down') {
      return (
        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" transform="rotate(-90 12 12)" />
        </svg>
      );
    }
    return (
      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
      </svg>
    );
  };

  return (
    <div 
      className={`
        bg-white rounded-2xl shadow-lg border ${colors.border} ${sizes.padding}
        transition-all duration-300 hover:shadow-xl hover:scale-105 
        ${isClickable ? 'cursor-pointer hover:border-opacity-60' : ''}
        group relative overflow-hidden
      `}
      onClick={isClickable ? onClick : undefined}
    >
      {/* Background Pattern */}
      <div className={`absolute inset-0 ${colors.light} opacity-50 rounded-2xl`}></div>
      <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 rounded-full bg-white bg-opacity-10"></div>
      
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className={`${sizes.iconSize} ${colors.bg} rounded-xl flex items-center justify-center text-white shadow-md`}>
            {typeof icon === 'string' ? (
              <span className="text-2xl">{icon}</span>
            ) : (
              icon
            )}
          </div>
          
          {trend && (
            <div className="flex items-center space-x-1 px-2 py-1 rounded-full bg-white bg-opacity-60 backdrop-blur-sm">
              {getTrendIcon()}
              <span className={`text-xs font-medium ${
                trendDirection === 'up' ? 'text-green-600' : 
                trendDirection === 'down' ? 'text-red-600' : 
                'text-gray-600'
              }`}>
                {trend}
              </span>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="space-y-2">
          <div className={`${sizes.valueText} font-bold text-gray-900 leading-tight`}>
            {value}
          </div>
          
          <div className={`${sizes.titleText} font-semibold ${colors.text} uppercase tracking-wide`}>
            {title}
          </div>
          
          {description && (
            <p className="text-xs text-gray-500 leading-relaxed">
              {description}
            </p>
          )}
        </div>

        {/* Action Indicator */}
        {isClickable && (
          <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        )}
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl"></div>
    </div>
  );
};

// Grid Container Component
const StatsGrid = ({ stats, columns = 'auto' }) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    auto: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  };

  return (
    <div className={`grid ${gridClasses[columns]} gap-6`}>
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export { StatCard, StatsGrid };
export default StatCard;