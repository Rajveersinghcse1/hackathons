import React, { useState, useEffect, useRef } from "react";

const DeviceCard = ({
  device,
  onView,
  onConfig,
  onDetails,
  onDelete,
  onImport,
  onApiTest,
}) => {
  const [apiEnabled, setApiEnabled] = useState(device?.apiEnabled || false);
  const [csvEnabled, setCsvEnabled] = useState(device?.csvEnabled || true);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [processedImage, setProcessedImage] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const progressInterval = useRef(null);

  // Function to start drone image processing
  const startDroneProcessing = async () => {
    try {
      setProcessing(true);
      setProgress(0);
      setStatus("Initializing...");
      setShowResults(false);
      setProcessedImage(null);

      // Start the processing
      const response = await fetch("http://localhost:5001/api/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        // Start polling for progress updates
        progressInterval.current = setInterval(async () => {
          try {
            const progressResponse = await fetch(
              "http://localhost:5001/api/progress"
            );
            const progressData = await progressResponse.json();

            setProgress(progressData.progress);
            setStatus(progressData.status);

            if (progressData.complete) {
              clearInterval(progressInterval.current);
              setProcessing(false);
              setShowResults(true);

              if (progressData.processed_image) {
                setProcessedImage(progressData.processed_image);
              }
            }
          } catch (error) {
            console.error("Error fetching progress:", error);
          }
        }, 500); // Poll every 500ms
      } else {
        setProcessing(false);
        setStatus("Failed to start processing");
      }
    } catch (error) {
      console.error("Error starting processing:", error);
      setProcessing(false);
      setStatus("Connection error");
    }
  };

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, []);

  // Function to reset processing state
  const resetProcessing = () => {
    setProcessing(false);
    setProgress(0);
    setStatus("");
    setShowResults(false);
    setProcessedImage(null);
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all duration-300 flex flex-col h-full max-w-sm">
      {/* Top accent bar */}
      <div className="h-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-t-xl flex-shrink-0"></div>

      {/* Device Header */}
      <div className="p-4 pb-3 flex-shrink-0">
        <div className="flex items-start space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-md">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-bold text-gray-900 leading-tight mb-0.5">
              {device?.name || "Device Name"}
            </h3>
            <p className="text-xs text-gray-600 font-medium">
              {device?.type || "IoT Sensor Device"}
            </p>
            <p className="text-xs text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">
              {device?.description ||
                "Real-time environmental monitoring with automated alerts and cloud connectivity."}
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons Section */}
      <div className="px-4 py-3 border-b border-gray-100 flex-1">
        {processing || showResults ? (
          /* Processing/Results Section */
          <div className="space-y-2.5">
            {processing && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium text-gray-700">
                    Processing Drone Image
                  </span>
                  <span className="text-xs font-bold text-blue-600">
                    {progress}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600">{status}</p>
                <button
                  onClick={resetProcessing}
                  className="w-full px-3 py-2 text-red-600 hover:text-red-800 hover:bg-red-50 border border-red-200 hover:border-red-300 rounded-lg font-medium text-xs transition-colors"
                >
                  Cancel Processing
                </button>
              </div>
            )}

            {showResults && !processing && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <svg
                    className="w-4 h-4 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span className="text-xs font-medium text-green-700">
                    Processing Complete!
                  </span>
                </div>
                {processedImage && (
                  <div className="text-xs text-gray-600 space-y-1">
                    <p>✅ Image analyzed</p>
                    <p className="truncate text-[10px]">
                      📁 {processedImage.split("\\").pop()}
                    </p>
                  </div>
                )}
                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      processedImage &&
                      window.open(`file:///${processedImage}`, "_blank")
                    }
                    className="flex-1 px-3 py-1.5 bg-green-600 text-white border border-green-600 rounded-lg hover:bg-green-700 hover:border-green-700 font-medium text-xs transition-colors"
                  >
                    View
                  </button>
                  <button
                    onClick={resetProcessing}
                    className="flex-1 px-3 py-1.5 text-gray-600 hover:text-gray-800 hover:bg-gray-50 border border-gray-200 hover:border-gray-300 rounded-lg font-medium text-xs transition-colors"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Normal Action Buttons */
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => onImport && onImport(device.importType)}
              className="flex flex-col items-center justify-center p-3 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors group"
            >
              <svg
                className="w-5 h-5 mb-1.5 group-hover:scale-110 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                />
              </svg>
              <span className="text-xs font-semibold">Import</span>
            </button>

            <button
              onClick={startDroneProcessing}
              className="flex flex-col items-center justify-center p-3 bg-orange-50 text-orange-700 border border-orange-200 rounded-lg hover:bg-orange-100 hover:border-orange-300 transition-colors group"
            >
              <svg
                className="w-5 h-5 mb-1.5 group-hover:scale-110 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
              <span className="text-xs font-semibold">Process</span>
            </button>

            <button
              onClick={() => onConfig && onConfig(device)}
              className="flex flex-col items-center justify-center p-3 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg hover:bg-amber-100 hover:border-amber-300 transition-colors group"
            >
              <svg
                className="w-5 h-5 mb-1.5 group-hover:rotate-90 transition-transform duration-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span className="text-xs font-semibold">Config</span>
            </button>

            <button
              onClick={() => onView && onView(device)}
              className="flex flex-col items-center justify-center p-3 bg-green-600 text-white border border-green-600 rounded-lg hover:bg-green-700 hover:border-green-700 transition-colors group shadow-md hover:shadow-lg"
            >
              <svg
                className="w-5 h-5 mb-1.5 group-hover:scale-110 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
              <span className="text-xs font-semibold">View</span>
            </button>
          </div>
        )}
      </div>

      {/* Controls Section */}
      <div className="px-4 py-3 border-b border-gray-100 flex-shrink-0">
        <div className="flex items-center justify-center space-x-4">
          {/* API Control */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-gray-700">API:</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={apiEnabled}
                onChange={(e) => setApiEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:bg-blue-600 transition-colors">
                <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white border border-gray-300 rounded-full transition-transform peer-checked:translate-x-4 peer-checked:border-white shadow-sm"></div>
              </div>
            </label>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded min-w-[32px] text-center ${
                apiEnabled
                  ? "text-green-700 bg-green-100"
                  : "text-gray-500 bg-gray-100"
              }`}
            >
              {apiEnabled ? "ON" : "OFF"}
            </span>
          </div>

          {/* Divider */}
          <div className="w-px h-5 bg-gray-300"></div>

          {/* CSV Control */}
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-gray-700">CSV:</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={csvEnabled}
                onChange={(e) => setCsvEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-green-300 rounded-full peer peer-checked:bg-green-600 transition-colors">
                <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white border border-gray-300 rounded-full transition-transform peer-checked:translate-x-4 peer-checked:border-white shadow-sm"></div>
              </div>
            </label>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded min-w-[32px] text-center ${
                csvEnabled
                  ? "text-green-700 bg-green-100"
                  : "text-gray-500 bg-gray-100"
              }`}
            >
              {csvEnabled ? "ON" : "OFF"}
            </span>
          </div>
        </div>
      </div>

      {/* Management Section */}
      <div className="p-4 pt-3 flex-shrink-0">
        <div className="flex gap-2">
          <button
            onClick={() =>
              onDetails &&
              onDetails({
                ...device,
                fullDescription:
                  device?.fullDescription ||
                  "This IoT device provides comprehensive environmental monitoring capabilities including temperature, humidity, air quality, and motion detection. Features real-time data transmission, automated alerting system, cloud connectivity, and advanced analytics dashboard for predictive maintenance and operational insights.",
              })
            }
            className="flex-1 px-3 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 border-2 border-blue-200 hover:border-blue-300 rounded-lg font-semibold text-xs transition-all duration-200 group relative flex items-center justify-center space-x-1.5"
            title={`View detailed information about ${
              device?.name || "this device"
            }`}
          >
            <svg
              className="w-3.5 h-3.5 group-hover:scale-110 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Details</span>
          </button>
          <button
            onClick={() => onDelete && onDelete(device)}
            className="flex-1 px-3 py-2 text-red-600 hover:text-white hover:bg-red-600 border-2 border-red-200 hover:border-red-600 rounded-lg font-semibold text-xs transition-all duration-200 flex items-center justify-center space-x-1.5 group"
          >
            <svg
              className="w-3.5 h-3.5 group-hover:scale-110 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            <span>Delete</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeviceCard;
