import React from 'react';

const AdvancedToggle = ({ 
  enabled, 
  onChange, 
  label, 
  description, 
  icon, 
  color = 'blue',
  size = 'md',
  disabled = false 
}) => {
  const sizeClasses = {
    sm: 'w-9 h-5',
    md: 'w-11 h-6',
    lg: 'w-14 h-7'
  };

  const thumbSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const colorClasses = {
    blue: enabled ? 'bg-blue-600' : 'bg-gray-200',
    green: enabled ? 'bg-green-600' : 'bg-gray-200',
    purple: enabled ? 'bg-purple-600' : 'bg-gray-200',
    red: enabled ? 'bg-red-600' : 'bg-gray-200',
    orange: enabled ? 'bg-orange-600' : 'bg-gray-200'
  };

  return (
    <div className={`flex items-center justify-between p-4 rounded-xl border border-gray-200 hover:border-gray-300 transition-all duration-200 ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}`}>
      <div className="flex items-start space-x-3">
        {icon && (
          <div className={`w-10 h-10 rounded-lg ${enabled ? `bg-${color}-100` : 'bg-gray-100'} flex items-center justify-center text-xl`}>
            {icon}
          </div>
        )}
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h4 className="text-sm font-semibold text-gray-900">{label}</h4>
            {enabled && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full bg-${color}-100 text-${color}-800`}>
                Active
              </span>
            )}
          </div>
          {description && (
            <p className="text-xs text-gray-500 mt-1 leading-relaxed">{description}</p>
          )}
        </div>
      </div>
      
      <button
        onClick={() => !disabled && onChange(!enabled)}
        disabled={disabled}
        className={`relative inline-flex ${sizeClasses[size]} rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${color}-500 ${colorClasses[color]} ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
        role="switch"
        aria-checked={enabled}
      >
        <span
          className={`${thumbSizeClasses[size]} bg-white rounded-full shadow-lg ring-0 transition-transform duration-200 ease-in-out flex items-center justify-center ${
            enabled ? `translate-x-${size === 'sm' ? '4' : size === 'md' ? '5' : '7'}` : 'translate-x-0.5'
          }`}
        >
          {enabled ? (
            <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </span>
      </button>
    </div>
  );
};

export default AdvancedToggle;