import React, { useState } from 'react';

const AdvancedInput = ({ 
  label, 
  type = 'text', 
  value, 
  onChange, 
  placeholder,
  icon,
  disabled = false,
  required = false,
  error,
  hint,
  validation,
  mask,
  className = '',
  size = 'md'
}) => {
  const [focused, setFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-5 py-4 text-lg'
  };

  const handleChange = (e) => {
    let newValue = e.target.value;
    
    // Apply mask if provided
    if (mask) {
      newValue = applyMask(newValue, mask);
    }
    
    onChange(newValue);
  };

  const applyMask = (value, maskPattern) => {
    // Simple mask implementation
    if (maskPattern === 'phone') {
      return value.replace(/\D/g, '').replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    }
    // Add more mask patterns as needed
    return value;
  };

  const inputType = type === 'password' && showPassword ? 'text' : type;

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label */}
      {label && (
        <label className="flex items-center space-x-1 text-sm font-semibold text-gray-700">
          <span>{label}</span>
          {required && <span className="text-red-500">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        {/* Icon */}
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {typeof icon === 'string' ? <span>{icon}</span> : icon}
          </div>
        )}

        {/* Input Field */}
        <input
          type={inputType}
          value={value}
          onChange={handleChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full ${sizeClasses[size]} ${icon ? 'pl-10' : ''} 
            ${type === 'password' ? 'pr-10' : ''}
            border-2 rounded-xl transition-all duration-200
            ${focused 
              ? 'border-blue-500 ring-4 ring-blue-500 ring-opacity-20' 
              : error 
                ? 'border-red-400 ring-4 ring-red-400 ring-opacity-20' 
                : 'border-gray-200 hover:border-gray-300'
            }
            ${disabled 
              ? 'bg-gray-50 text-gray-500 cursor-not-allowed' 
              : 'bg-white text-gray-900'
            }
            focus:outline-none placeholder-gray-400
          `}
        />

        {/* Password Toggle */}
        {type === 'password' && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            {showPassword ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.543 7-1.275 4.057-5.065 7-9.543 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            )}
          </button>
        )}

        {/* Loading State */}
        {validation?.isValidating && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
          </div>
        )}

        {/* Validation Success */}
        {validation?.isValid && !validation.isValidating && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-green-500">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
      </div>

      {/* Helper Text */}
      <div className="space-y-1">
        {error && (
          <p className="text-sm text-red-600 flex items-center space-x-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </p>
        )}
        
        {hint && !error && (
          <p className="text-sm text-gray-500">{hint}</p>
        )}

        {validation?.message && !error && (
          <p className={`text-sm ${validation.isValid ? 'text-green-600' : 'text-orange-600'}`}>
            {validation.message}
          </p>
        )}
      </div>
    </div>
  );
};

// Advanced Select Component
const AdvancedSelect = ({ 
  label, 
  value, 
  onChange, 
  options = [], 
  placeholder = 'Select an option',
  icon,
  disabled = false,
  required = false,
  error,
  hint,
  searchable = false,
  multiple = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredOptions = searchable 
    ? options.filter(option => 
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  const selectedOption = options.find(opt => opt.value === value);

  return (
    <div className={`space-y-2 relative ${className}`}>
      {label && (
        <label className="flex items-center space-x-1 text-sm font-semibold text-gray-700">
          <span>{label}</span>
          {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            w-full px-4 py-3 text-left border-2 rounded-xl transition-all duration-200
            ${isOpen 
              ? 'border-blue-500 ring-4 ring-blue-500 ring-opacity-20' 
              : error 
                ? 'border-red-400' 
                : 'border-gray-200 hover:border-gray-300'
            }
            ${disabled 
              ? 'bg-gray-50 text-gray-500 cursor-not-allowed' 
              : 'bg-white text-gray-900 cursor-pointer'
            }
            focus:outline-none flex items-center justify-between
          `}
        >
          <div className="flex items-center space-x-2">
            {icon && <span className="text-gray-400">{icon}</span>}
            <span>{selectedOption ? selectedOption.label : placeholder}</span>
          </div>
          <svg 
            className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto">
            {searchable && (
              <div className="p-2 border-b border-gray-100">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
            
            <div className="py-1">
              {filteredOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    onChange(option.value);
                    setIsOpen(false);
                    setSearchTerm('');
                  }}
                  className={`
                    w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors
                    ${value === option.value ? 'bg-blue-50 text-blue-700' : 'text-gray-900'}
                  `}
                >
                  {option.label}
                </button>
              ))}
              
              {filteredOptions.length === 0 && (
                <div className="px-4 py-3 text-gray-500 text-center">
                  No options found
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-600 flex items-center space-x-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </p>
      )}
      
      {hint && !error && (
        <p className="text-sm text-gray-500">{hint}</p>
      )}
    </div>
  );
};

export { AdvancedInput, AdvancedSelect };
export default AdvancedInput;