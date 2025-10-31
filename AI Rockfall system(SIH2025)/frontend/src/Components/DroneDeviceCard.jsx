import React, { useState, useEffect, useRef } from 'react';

const DroneDeviceCard = ({ 
  device, 
  onView,
  onConfig, 
  onDetails, 
  onDelete, 
  onImport, 
  onApiTest 
}) => {
  const [apiEnabled, setApiEnabled] = useState(device?.apiEnabled || false);
  const [csvEnabled, setCsvEnabled] = useState(device?.csvEnabled || true);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all duration-300 w-200 h-150 flex flex-col mx-auto">
      {/* Top accent bar - Orange for drone */}
      <div className="h-1.5 bg-gradient-to-r from-orange-500 to-red-600 rounded-t-xl flex-shrink-0"></div>
      
      {/* Device Header - Drone Specific */}
      <div className="p-5 pb-3 flex-shrink-0">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center flex-shrink-0">
            {/* Drone Icon */}
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-bold text-gray-900 truncate">{device?.name || 'Drone Camera System'}</h3>
            <p className="text-sm text-orange-600 truncate font-medium">Aerial Mining Surveillance</p>
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">
              {device?.description || 'Advanced drone system for mining site surveillance, crack detection, and geological analysis with AI-powered image processing.'}
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons Section - Drone Specific */}
      <div className="px-5 py-4 border-b border-gray-100 flex-1">
        <div className="grid grid-cols-2 gap-3 h-full">
          <button
            onClick={() => onImport && onImport(device)}
            className="flex flex-col items-center justify-center p-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors"
          >
            <svg className="w-5 h-5 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            <span className="text-xs font-medium">Import</span>
          </button>
          
          <button
            onClick={() => onApiTest && onApiTest(device)}
            className="flex flex-col items-center justify-center p-2 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-colors"
          >
            <svg className="w-5 h-5 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span className="text-xs font-medium">API</span>
          </button>
          
          <button
            onClick={() => onConfig && onConfig(device)}
            className="flex flex-col items-center justify-center p-2 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg hover:bg-amber-100 hover:border-amber-300 transition-colors"
          >
            <svg className="w-5 h-5 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-xs font-medium">Config</span>
          </button>
          
          <button
            onClick={() => onView && onView(device)}
            className="flex flex-col items-center justify-center p-2 bg-orange-600 text-white border border-orange-600 rounded-lg hover:bg-orange-700 hover:border-orange-700 transition-colors"
          >
            <svg className="w-5 h-5 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span className="text-xs font-medium">View</span>
          </button>
        </div>
      </div>

      {/* Controls Section - Drone Specific */}
      <div className="p-4 border-b border-gray-100 flex-shrink-0">
        <div className="flex items-center justify-center space-x-4">
          {/* Flight Mode Control */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-gray-700">Flight:</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={apiEnabled}
                onChange={(e) => setApiEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-8 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:bg-orange-600 transition-colors">
                <div className="absolute top-0.5 left-0.5 w-3 h-3 bg-white border border-gray-300 rounded-full transition-transform peer-checked:translate-x-4 peer-checked:border-white"></div>
              </div>
            </label>
            <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${apiEnabled ? 'text-green-700 bg-green-100' : 'text-gray-500 bg-gray-100'}`}>
              {apiEnabled ? 'AUTO' : 'MANUAL'}
            </span>
          </div>
          
          {/* Divider */}
          <div className="w-px h-4 bg-gray-300"></div>
          
          {/* Recording Control */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-gray-700">Record:</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={csvEnabled}
                onChange={(e) => setCsvEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-8 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:bg-red-600 transition-colors">
                <div className="absolute top-0.5 left-0.5 w-3 h-3 bg-white border border-gray-300 rounded-full transition-transform peer-checked:translate-x-4 peer-checked:border-white"></div>
              </div>
            </label>
            <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${csvEnabled ? 'text-red-700 bg-red-100' : 'text-gray-500 bg-gray-100'}`}>
              {csvEnabled ? 'REC' : 'OFF'}
            </span>
          </div>
        </div>
      </div>

      {/* Management Section - Drone Specific */}
      <div className="p-4 flex-shrink-0">
        <div className="flex gap-3">
          <button
            onClick={() => onDetails && onDetails({
              ...device,
              fullDescription: device?.fullDescription || 'Advanced drone surveillance system for mining operations. Features high-resolution cameras, AI-powered image analysis, real-time crack detection, geological assessment, and automated flight patterns. Includes GPS mapping, weather sensors, and emergency landing protocols for comprehensive mining site monitoring.'
            })}
            className="flex-1 px-3 py-2 text-orange-600 hover:text-orange-800 hover:bg-orange-50 border border-orange-200 hover:border-orange-300 rounded-lg font-medium text-xs transition-colors group relative"
            title={`View detailed information about ${device?.name || 'this drone'} including flight logs, camera specifications, and analysis capabilities`}
          >
            <span className="flex items-center justify-center space-x-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Flight Details</span>
            </span>
            <span className="text-[10px] text-gray-500 group-hover:text-orange-600 transition-colors block mt-0.5">
              {device?.name || 'Drone'} Status
            </span>
          </button>
          <button
            onClick={() => onDelete && onDelete(device)}
            className="flex-1 px-3 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 border border-red-200 hover:border-red-300 rounded-lg font-medium text-xs transition-colors flex items-center justify-center space-x-1"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>Remove</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DroneDeviceCard;