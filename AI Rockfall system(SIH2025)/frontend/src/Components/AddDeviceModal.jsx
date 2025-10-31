import React, { useState } from 'react';

const AddDeviceModal = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    status: 'Online',
    importType: '',
    apiUrl: '',
    method: 'GET',
    tabs: []
  });

  const deviceTypes = [
    'Ground Radar',
    'Optical Scanner',
    'Subsurface Monitor',
    'Hydrological Monitor',
    'Environmental Monitor',
    'Seismic Monitor',
    'Aerial Survey'
  ];

  const importTypes = ['CSV', 'JSON', 'XML', 'LAS', 'Images'];
  const availableTabs = ['Table', 'Different Charts', '3D View', 'Processing'];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.tabs.length === 0) {
      alert('Please select at least one tab');
      return;
    }
    onAdd(formData);
    // Reset form
    setFormData({
      name: '',
      type: '',
      status: 'Online',
      importType: '',
      apiUrl: '',
      method: 'GET',
      tabs: []
    });
  };

  const handleTabToggle = (tab) => {
    setFormData(prev => ({
      ...prev,
      tabs: prev.tabs.includes(tab)
        ? prev.tabs.filter(t => t !== tab)
        : [...prev.tabs, tab]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto relative shadow-2xl transform transition-all">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white sticky top-0">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Add New Device</h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors cursor-pointer"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-purple-100 mt-1">Configure your new monitoring device</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Device Name *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
                placeholder="Enter device name"
                required
              />
            </div>

            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-2">
                Device Type *
              </label>
              <select
                id="type"
                value={formData.type}
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
                required
              >
                <option value="">Select device type</option>
                {deviceTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
              >
                <option value="Online">Online</option>
                <option value="Offline">Offline</option>
              </select>
            </div>

            <div>
              <label htmlFor="importType" className="block text-sm font-medium text-gray-700 mb-2">
                Import Type *
              </label>
              <select
                id="importType"
                value={formData.importType}
                onChange={(e) => setFormData(prev => ({ ...prev, importType: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
                required
              >
                <option value="">Select import type</option>
                {importTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          {/* API Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">API Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label htmlFor="apiUrl" className="block text-sm font-medium text-gray-700 mb-2">
                  API URL *
                </label>
                <input
                  type="url"
                  id="apiUrl"
                  value={formData.apiUrl}
                  onChange={(e) => setFormData(prev => ({ ...prev, apiUrl: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
                  placeholder="https://api.example.com/device"
                  required
                />
              </div>

              <div>
                <label htmlFor="method" className="block text-sm font-medium text-gray-700 mb-2">
                  HTTP Method
                </label>
                <select
                  id="method"
                  value={formData.method}
                  onChange={(e) => setFormData(prev => ({ ...prev, method: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent cursor-pointer"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="DELETE">DELETE</option>
                </select>
              </div>
            </div>
          </div>

          {/* Available Tabs */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Tabs *</h3>
            <div className="grid grid-cols-2 gap-3">
              {availableTabs.map(tab => (
                <label key={tab} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.tabs.includes(tab)}
                    onChange={() => handleTabToggle(tab)}
                    className="mr-3 rounded focus:ring-2 focus:ring-purple-500 cursor-pointer"
                  />
                  <span className="text-sm font-medium text-gray-700">{tab}</span>
                </label>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">Select at least one tab for the device view</p>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-all cursor-pointer"
            >
              Add Device
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddDeviceModal;