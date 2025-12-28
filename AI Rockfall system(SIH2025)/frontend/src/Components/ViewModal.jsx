import React, { useState, useEffect } from "react";
import Papa from "papaparse";

const ViewModal = ({ isOpen, device, onClose, onDeleteFile }) => {
  const [activeTab, setActiveTab] = useState("Uploaded Files");
  const [images, setImages] = useState([]);
  const [csvFiles, setCsvFiles] = useState([]);
  const [selectedCsv, setSelectedCsv] = useState(null);
  const [csvData, setCsvData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && device) {
      loadDeviceData();
    }
  }, [isOpen, device]);

  const loadDeviceData = async () => {
    if (!device?.folderName) return;

    setLoading(true);
    try {
      // Load images from the Images folder
      await loadImages();
      // Load CSV files from the Analysis folder
      await loadCsvFiles();
    } catch (error) {
      console.error("Error loading device data:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadImages = async () => {
    if (!device?.folderName) return;

    try {
      // Use relative path to the public Upload folder for Vite dev server
      const basePath = `/Upload/${device.folderName}`;

      // Try both 'Images' and 'images' folder names (capital I first for most devices)
      const possiblePaths = [`${basePath}/Images/`, `${basePath}/images/`];

      // Define actual image names based on device type from Upload folder
      let commonImageNames = [];

      if (device.folderName === "Extensometer") {
        commonImageNames = [
          "alert_system_dashboard.png",
          "comprehensive_dashboard.png",
          "correlation_analysis.png",
          "crack_opening_analysis.png",
          "crack_opening_analysis_1.png",
          "crack_rate_analysis.png",
          "ml_analysis.png",
          "statistical_analysis.png",
        ];
      } else if (device.folderName === "Geophone") {
        commonImageNames = [
          "alert_system.png",
          "comprehensive_dashboard.png",
          "comprehensive_dashboard_1.png",
          "correlation_analysis.png",
          "frequency_analysis.png",
          "frequency_analysis_1.png",
          "magnitude_analysis.png",
          "ml_models.png",
          "ml_models_1.png",
        ];
      } else if (device.folderName === "Piezometer") {
        commonImageNames = [
          "3d_spatial_distribution.png",
          "correlation_heatmap.png",
          "feature_importance.png",
          "model_performance.png",
          "pressure_change_rate.png",
          "pressure_trends.png",
          "realtime_readings.png",
          "risk_dashboard.png",
          "risk_distribution.png",
        ];
      } else if (device.folderName === "Auto_Weather_station") {
        // Auto_Weather_station doesn't have images folder
        commonImageNames = [];
      } else if (device.folderName === "GB-InSAR") {
        commonImageNames = [
          "comprehensive_dashboard.png",
          "confusion_matrix.png",
          "correlation_heatmap.png",
          "displacement_rate_analysis.png",
          "displacement_trends.png",
          "feature_importance.png",
          "realtime_monitoring.png",
          "risk_distribution.png",
          "risk_probability_heatmap.png",
          "risk_probability_trends.png",
          "risk_zones.png",
          "slope_analysis.png",
          "velocity_vector_field.png",
        ];
      } else if (device.folderName === "LiDAR") {
        commonImageNames = [
          "clustering_results.png",
          "eda_analysis.png",
          "final_summary.png",
          "ml_results.png",
          "ml_results_1.png",
        ];
      }

      const availableImages = [];

      // Determine which path to use based on device type
      let imagePath = possiblePaths[0]; // Default to Images/ (capital I)

      // Devices with lowercase 'images' folder
      if (
        ["Geophone", "Piezometer", "GB-InSAR", "LiDAR"].includes(
          device.folderName
        )
      ) {
        imagePath = possiblePaths[1]; // Use images/ (lowercase i)
      }

      console.log(`Loading images for ${device.name} from: ${imagePath}`);

      // Build image URLs
      if (commonImageNames.length > 0) {
        for (const imageName of commonImageNames) {
          const imgUrl = `${imagePath}${imageName}`;
          availableImages.push({
            name: imageName,
            url: imgUrl,
            path: imgUrl,
          });
        }
      }

      setImages(availableImages);
    } catch (error) {
      console.error("Error loading images:", error);
      setImages([]);
    }
  };
  const loadCsvFiles = async () => {
    if (!device?.folderName) return;

    try {
      // Use relative path to the public Upload folder for Vite dev server
      const analysisPath = `/Upload/${device.folderName}/Analysis/`;

      // Common CSV file patterns based on device type
      let commonCsvNames = [];

      if (device.folderName === "Extensometer") {
        commonCsvNames = [
          "extensometer_alerts.csv",
          "extensometer_alerts_1.csv",
          "extensometer_alerts_2.csv",
          "extensometer_predictions.csv",
          "extensometer_predictions_1.csv",
          "extensometer_processed_data.csv",
          "extensometer_processed_data_1.csv",
          "extensometer_processed_data_2.csv",
        ];
      } else if (device.folderName === "Geophone") {
        commonCsvNames = ["processed_geophone_data.csv"];
      } else if (device.folderName === "Piezometer") {
        commonCsvNames = ["prediction.csv"];
      } else if (device.folderName === "Auto_Weather_station") {
        commonCsvNames = [
          "processed_weather_data.csv",
          "weather_predictions.csv",
        ];
      } else if (device.folderName === "GB-InSAR") {
        commonCsvNames = ["rockfall_predictions.csv"];
      } else if (device.folderName === "LiDAR") {
        commonCsvNames = ["analysis_log.csv", "current_features.csv"];
      }

      // Create CSV file objects
      const availableCsvFiles = commonCsvNames.map((name) => ({
        name: name,
        path: `${analysisPath}${name}`,
      }));

      setCsvFiles(availableCsvFiles);
    } catch (error) {
      console.error("Error loading CSV files:", error);
      setCsvFiles([]);
    }
  };

  const loadCsvData = async (csvFile) => {
    setLoading(true);
    try {
      const response = await fetch(csvFile.path);
      const csvText = await response.text();

      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          setCsvData({
            headers: results.meta.fields || [],
            rows: results.data || [],
            fileName: csvFile.name,
          });
          setSelectedCsv(csvFile);
          setLoading(false);
        },
        error: (error) => {
          console.error("Error parsing CSV:", error);
          alert(`Failed to load CSV file: ${error.message}`);
          setLoading(false);
        },
      });
    } catch (error) {
      console.error("Error fetching CSV:", error);
      alert(`Failed to fetch CSV file: ${error.message}`);
      setLoading(false);
    }
  };

  if (!isOpen || !device) return null;

  const renderTabContent = () => {
    switch (activeTab) {
      case "Uploaded Files":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Uploaded Files
            </h3>
            {device.uploadedFiles && device.uploadedFiles.length > 0 ? (
              <div className="space-y-2">
                {device.uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-blue-600">
                        <svg
                          className="w-8 h-8"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(file.uploadedAt).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => onDeleteFile(device.id, index)}
                      className="text-red-500 hover:text-red-700 p-2"
                    >
                      <svg
                        className="w-5 h-5"
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
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <svg
                  className="w-16 h-16 mx-auto mb-3 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <p>No files uploaded yet</p>
              </div>
            )}
          </div>
        );

      case "Table":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Data Table View
            </h3>

            {/* CSV File Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select CSV File:
              </label>
              <select
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => {
                  const csvFile = csvFiles.find(
                    (f) => f.name === e.target.value
                  );
                  if (csvFile) loadCsvData(csvFile);
                }}
                value={selectedCsv?.name || ""}
              >
                <option value="">-- Select a CSV file --</option>
                {csvFiles.map((file, index) => (
                  <option key={index} value={file.name}>
                    {file.name}
                  </option>
                ))}
              </select>
            </div>

            {loading && (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading CSV data...</p>
              </div>
            )}

            {csvData && !loading && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      {csvData.headers.map((header, index) => (
                        <th
                          key={index}
                          className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b"
                        >
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {csvData.rows.slice(0, 50).map((row, rowIndex) => (
                      <tr key={rowIndex} className="hover:bg-gray-50">
                        {csvData.headers.map((header, colIndex) => (
                          <td
                            key={colIndex}
                            className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap"
                          >
                            {row[header]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {csvData.rows.length > 50 && (
                  <p className="text-sm text-gray-500 mt-2 text-center">
                    Showing first 50 rows of {csvData.rows.length} total rows
                  </p>
                )}
              </div>
            )}

            {!csvData && !loading && csvFiles.length > 0 && (
              <div className="text-center py-8 text-gray-500">
                <p>Please select a CSV file to view its data</p>
              </div>
            )}

            {csvFiles.length === 0 && !loading && (
              <div className="text-center py-8 text-gray-500">
                <p>No CSV files found in the Analysis folder</p>
              </div>
            )}
          </div>
        );

      case "Images":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Images Gallery
            </h3>
            {loading && (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading images...</p>
              </div>
            )}

            {!loading && images.length > 0 && (
              <div className="grid grid-cols-2 gap-4">
                {images.map((image, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-2 hover:shadow-lg transition-shadow cursor-pointer group"
                    onClick={() => window.open(image.url, "_blank")}
                  >
                    <div className="relative overflow-hidden rounded-lg mb-2">
                      <img
                        src={image.url}
                        alt={image.name}
                        className="w-full h-48 object-cover rounded-lg group-hover:scale-105 transition-transform duration-200"
                        onError={(e) => {
                          e.target.style.display = "none";
                          e.target.nextElementSibling.style.display = "flex";
                        }}
                      />
                      <div className="hidden items-center justify-center h-48 bg-gray-100 rounded-lg flex-col">
                        <svg
                          className="w-12 h-12 text-gray-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        <p className="text-sm text-gray-500 mt-2">
                          Image not found
                        </p>
                      </div>
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg flex items-center justify-center">
                        <svg
                          className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                          />
                        </svg>
                      </div>
                    </div>
                    <p
                      className="text-sm text-gray-600 truncate"
                      title={image.name}
                    >
                      {image.name}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {!loading && images.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <svg
                  className="w-16 h-16 mx-auto mb-3 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <p>No images found in the Images folder</p>
              </div>
            )}
          </div>
        );

      case "Analysis":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Analysis Files
            </h3>
            {csvFiles.length > 0 ? (
              <div className="grid grid-cols-1 gap-3">
                {csvFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => {
                      loadCsvData(file);
                      setActiveTab("Table");
                    }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-green-600">
                        <svg
                          className="w-8 h-8"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          Click to view data
                        </p>
                      </div>
                    </div>
                    <svg
                      className="w-5 h-5 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No analysis files found</p>
              </div>
            )}
          </div>
        );

      case "3D View":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">
              3D Visualization
            </h3>
            <div className="text-center py-8 text-gray-500">
              <svg
                className="w-16 h-16 mx-auto mb-3 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
              <p>3D point cloud view will be available here</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-6xl max-h-[90vh] relative overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">{device.name}</h2>
              <p className="text-blue-100 text-sm mt-1">{device.type}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-red-200 transition-colors duration-200"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-gray-50">
          <div className="flex overflow-x-auto">
            {device.tabs?.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 font-medium text-sm whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? "text-blue-600 border-b-2 border-blue-600 bg-white"
                    : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default ViewModal;
