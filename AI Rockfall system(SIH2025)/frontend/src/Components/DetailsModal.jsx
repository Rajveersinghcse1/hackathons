import React from "react";

const DetailsModal = ({ isOpen, device, onClose }) => {
  if (!isOpen || !device) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-4xl max-h-90vh relative overflow-hidden shadow-2xl">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">{device.name} Details</h2>
            <button onClick={onClose} className="text-white hover:text-red-200 cursor-pointer">
              Close
            </button>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-2">Device Information</h3>
              <p>Name: {device.name}</p>
              <p>Type: {device.type}</p>
              <p>Status: {device.status}</p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">API Configuration</h3>
              <p>URL: {device.apiUrl}</p>
              <p>Method: {device.method}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailsModal;