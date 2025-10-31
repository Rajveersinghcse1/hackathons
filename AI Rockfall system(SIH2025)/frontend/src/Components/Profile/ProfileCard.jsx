import React from 'react';

const ProfileCard = ({ 
  title, 
  subtitle, 
  icon, 
  gradient = 'from-blue-500 to-purple-600',
  children,
  className = '',
  headerActions,
  stats,
  isLoading = false
}) => {
  return (
    <div className={`bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 ${className}`}>
      {/* Header */}
      <div className={`bg-gradient-to-r ${gradient} px-6 py-4 text-white relative overflow-hidden`}>
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {icon && (
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <span className="text-xl">{icon}</span>
              </div>
            )}
            <div>
              <h3 className="text-lg font-bold">{title}</h3>
              {subtitle && <p className="text-sm opacity-90">{subtitle}</p>}
            </div>
          </div>
          {headerActions && (
            <div className="flex items-center space-x-2">
              {headerActions}
            </div>
          )}
        </div>
        
        {/* Decorative Elements */}
        <div className="absolute -top-4 -right-4 w-20 h-20 bg-white bg-opacity-10 rounded-full"></div>
        <div className="absolute -bottom-2 -left-2 w-16 h-16 bg-white bg-opacity-5 rounded-full"></div>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="border-b border-gray-100">
          <div className="grid grid-cols-2 md:grid-cols-4">
            {stats.map((stat, index) => (
              <div key={index} className="px-4 py-3 text-center border-r border-gray-100 last:border-r-0">
                <div className="text-lg font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-6">
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default ProfileCard;