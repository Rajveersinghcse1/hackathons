import React, { useState } from 'react';
import DroneDeviceCard from '../Components/DroneDeviceCard';
import DroneProgressModal from '../Components/DroneProgressModal';

const DroneDashboard = () => {
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [selectedDrone, setSelectedDrone] = useState(null);

  // Sample drone devices
  const droneDevices = [
    {
      id: 'drone-001',
      name: 'SkyMiner Alpha',
      type: 'Aerial Surveillance Drone',
      description: 'High-altitude mining site surveillance with thermal imaging and AI-powered crack detection',
      apiEnabled: true,
      csvEnabled: true,
      batteryLevel: 85,
      flightTime: '2h 15m',
      lastFlight: '2025-10-02T10:30:00Z'
    },
    {
      id: 'drone-002', 
      name: 'TerraScan Beta',
      type: 'Geological Survey Drone',
      description: 'Specialized geological analysis drone with LIDAR scanning and 4K camera array',
      apiEnabled: false,
      csvEnabled: true,
      batteryLevel: 92,
      flightTime: '1h 45m',
      lastFlight: '2025-10-02T08:15:00Z'
    },
    {
      id: 'drone-003',
      name: 'RockWatch Gamma',
      type: 'Safety Monitoring Drone',
      description: 'Continuous safety monitoring with real-time hazard detection and emergency response',
      apiEnabled: true,
      csvEnabled: false,
      batteryLevel: 67,
      flightTime: '3h 20m',
      lastFlight: '2025-10-01T16:45:00Z'
    }
  ];

  const handleViewDrone = (drone) => {
    setSelectedDrone(drone);
    setShowProgressModal(true);
  };

  const handleCloseModal = () => {
    setShowProgressModal(false);
    setSelectedDrone(null);
  };

  const handleConfig = (drone) => {
    alert(`Opening configuration for ${drone.name}`);
  };

  const handleDetails = (drone) => {
    alert(`Showing details for ${drone.name}`);
  };

  const handleDelete = (drone) => {
    if (window.confirm(`Are you sure you want to remove ${drone.name}?`)) {
      alert(`${drone.name} would be removed`);
    }
  };

  const handleImport = (drone) => {
    alert(`Importing data for ${drone.name}`);
  };

  const handleApiTest = (drone) => {
    alert(`Testing API connection for ${drone.name}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Drone Fleet Management</h1>
        <p className="text-gray-600">Monitor and control your mining site surveillance drones</p>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Drones</p>
              <p className="text-2xl font-bold text-gray-900">{droneDevices.filter(d => d.batteryLevel > 20).length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Flight Time</p>
              <p className="text-2xl font-bold text-gray-900">7h 20m</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.986-.833-2.764 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-600">Issues Detected</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-600">Images Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">1,247</p>
            </div>
          </div>
        </div>
      </div>

      {/* Drone Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {droneDevices.map((drone) => (
          <DroneDeviceCard
            key={drone.id}
            device={drone}
            onView={handleViewDrone}
            onConfig={handleConfig}
            onDetails={handleDetails}
            onDelete={handleDelete}
            onImport={handleImport}
            onApiTest={handleApiTest}
          />
        ))}
      </div>

      {/* Instructions */}
      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">🚁 How to Use Drone Analysis</h3>
        <div className="space-y-2 text-blue-800">
          <p>1. <strong>Click the orange "View" button</strong> on any drone card to open the analysis interface</p>
          <p>2. <strong>Click "Start Analysis"</strong> in the progress modal to begin mining image analysis</p>
          <p>3. <strong>Watch real-time progress</strong> as the AI processes drone footage</p>
          <p>4. <strong>View results</strong> including annotated images with detected issues</p>
        </div>
        <div className="mt-4 p-3 bg-blue-100 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>Note:</strong> Make sure the mining analysis API server is running on port 5002 
            for the analysis to work properly.
          </p>
        </div>
      </div>

      {/* Progress Modal */}
      <DroneProgressModal
        isOpen={showProgressModal}
        onClose={handleCloseModal}
        device={selectedDrone}
      />
    </div>
  );
};

export default DroneDashboard;