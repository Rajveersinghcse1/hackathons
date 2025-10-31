import React from 'react';

const ActivityTimeline = ({ activities, maxItems = 10 }) => {
  const getActivityIcon = (type) => {
    const icons = {
      login: { icon: '🔐', color: 'bg-green-500' },
      logout: { icon: '🚪', color: 'bg-gray-500' },
      report: { icon: '📊', color: 'bg-blue-500' },
      prediction: { icon: '🔮', color: 'bg-purple-500' },
      inspection: { icon: '🔍', color: 'bg-orange-500' },
      analytics: { icon: '📈', color: 'bg-indigo-500' },
      security: { icon: '🛡️', color: 'bg-red-500' },
      settings: { icon: '⚙️', color: 'bg-gray-600' },
      export: { icon: '📤', color: 'bg-cyan-500' },
      import: { icon: '📥', color: 'bg-teal-500' },
      collaboration: { icon: '👥', color: 'bg-pink-500' },
      notification: { icon: '🔔', color: 'bg-yellow-500' },
      default: { icon: '📋', color: 'bg-gray-400' }
    };
    return icons[type] || icons.default;
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return time.toLocaleDateString();
  };

  const displayActivities = activities.slice(0, maxItems);

  return (
    <div className="space-y-4">
      {displayActivities.map((activity, index) => {
        const activityData = getActivityIcon(activity.type);
        const isLast = index === displayActivities.length - 1;

        return (
          <div key={activity.id || index} className="relative group">
            {/* Timeline Line */}
            {!isLast && (
              <div className="absolute left-6 top-12 w-0.5 h-8 bg-gradient-to-b from-gray-300 to-transparent"></div>
            )}

            <div className="flex items-start space-x-4 p-4 rounded-xl hover:bg-gray-50 transition-all duration-200 group-hover:shadow-md">
              {/* Activity Icon */}
              <div className={`relative flex-shrink-0 w-12 h-12 ${activityData.color} rounded-full flex items-center justify-center text-white shadow-lg`}>
                <span className="text-lg">{activityData.icon}</span>
                
                {/* Pulse Animation for Recent Activities */}
                {index < 3 && (
                  <div className={`absolute inset-0 ${activityData.color} rounded-full opacity-75 animate-ping`}></div>
                )}
              </div>

              {/* Activity Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                      {activity.title || activity.action}
                    </p>
                    {activity.description && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {activity.description}
                      </p>
                    )}
                    
                    {/* Tags */}
                    {activity.tags && activity.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {activity.tags.map((tag, tagIndex) => (
                          <span
                            key={tagIndex}
                            className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-end space-y-1 ml-4">
                    <span className="text-xs text-gray-500 whitespace-nowrap">
                      {formatTimeAgo(activity.timestamp || activity.time)}
                    </span>
                    
                    {/* Priority/Status Indicator */}
                    {activity.priority && (
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        activity.priority === 'high' ? 'bg-red-100 text-red-700' :
                        activity.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {activity.priority}
                      </span>
                    )}

                    {activity.status && (
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        activity.status === 'completed' ? 'bg-green-100 text-green-700' :
                        activity.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                        activity.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {activity.status}
                      </span>
                    )}
                  </div>
                </div>

                {/* Additional Details */}
                {activity.details && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(activity.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-500 capitalize">{key}:</span>
                          <span className="text-gray-900 font-medium">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {/* Load More Button */}
      {activities.length > maxItems && (
        <div className="text-center pt-4">
          <button className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
            Load More Activities ({activities.length - maxItems} remaining)
          </button>
        </div>
      )}

      {/* Empty State */}
      {activities.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-gray-900 mb-1">No activity yet</h3>
          <p className="text-xs text-gray-500">Your recent activities will appear here</p>
        </div>
      )}
    </div>
  );
};

export default ActivityTimeline;