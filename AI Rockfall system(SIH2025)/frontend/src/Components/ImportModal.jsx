import React, { useState, useRef } from "react";

const ImportModal = ({
  isOpen,
  onClose,
  device,
  importType,
  onFileUploaded,
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const uploadCallbackRef = useRef(false); // Track if callback was called

  if (!isOpen) return null;

  const getImportTypeInfo = () => {
    switch (importType) {
      case "CSV":
        return {
          title: "Import CSV Data",
          accept: ".csv",
          description: "Upload CSV files containing measurement data",
          icon: "📊",
          maxSize: "10MB",
        };
      case "LAS":
        return {
          title: "Import LAS Files",
          accept: ".las",
          description: "Upload LiDAR point cloud data files (.las format only)",
          icon: "🌐",
          maxSize: "100MB",
        };
      case "Images":
        return {
          title: "Import Images",
          accept: "image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp,.tiff,.tif",
          description:
            "Upload aerial or survey images (all image formats supported)",
          icon: "📸",
          maxSize: "50MB",
        };
      default:
        return {
          title: "Import Files",
          accept: ".csv",
          description: "Upload CSV data files",
          icon: "📁",
          maxSize: "10MB",
        };
    }
  };

  const typeInfo = getImportTypeInfo();

  const validateFileType = (file) => {
    const fileName = file.name.toLowerCase();

    switch (importType) {
      case "CSV":
        return fileName.endsWith(".csv");
      case "LAS":
        return fileName.endsWith(".las");
      case "Images":
        // Accept all common image formats
        const imageExtensions = [
          ".jpg",
          ".jpeg",
          ".png",
          ".gif",
          ".bmp",
          ".webp",
          ".tiff",
          ".tif",
        ];
        return imageExtensions.some((ext) => fileName.endsWith(ext));
      default:
        return fileName.endsWith(".csv");
    }
  };

  const getFileTypeError = () => {
    switch (importType) {
      case "CSV":
        return "Please select a valid CSV file (.csv)";
      case "LAS":
        return "Please select a valid LAS file (.las)";
      case "Images":
        return "Please select a valid image file (jpg, png, gif, bmp, webp, tiff)";
      default:
        return "Please select a valid CSV file (.csv)";
    }
  };

  const handleFileSelect = (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (validateFileType(file)) {
        setSelectedFile(file);
      } else {
        alert(getFileTypeError());
        event.target.value = ""; // Reset input
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFileType(file)) {
        setSelectedFile(file);
      } else {
        alert(getFileTypeError());
      }
    }
  };

  const parseCSV = (text) => {
    const lines = text.split("\n").filter((line) => line.trim());
    if (lines.length === 0) return { headers: [], rows: [] };

    const headers = lines[0].split(",").map((h) => h.trim());
    const rows = lines.slice(1).map((line) => {
      const values = line.split(",").map((v) => v.trim());
      return headers.reduce((obj, header, index) => {
        obj[header] = values[index];
        return obj;
      }, {});
    });

    return { headers, rows };
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    uploadCallbackRef.current = false; // Reset flag before upload

    // Read file content for CSV files
    if (importType === "CSV") {
      const reader = new FileReader();

      reader.onload = (e) => {
        const text = e.target.result;
        const parsedData = parseCSV(text);

        // Continue with upload after parsing
        completeUpload(parsedData);
      };

      reader.onerror = () => {
        alert("Error reading file. Please try again.");
        setIsUploading(false);
        setUploadProgress(0);
      };

      reader.readAsText(selectedFile);
    } else {
      // For non-CSV files, upload immediately
      completeUpload(null);
    }
  };

  const completeUpload = (parsedData) => {
    // Create file data object
    const fileData = {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type,
      uploadedAt: new Date().toISOString(),
      importType: importType,
      // For images, create a preview URL
      preview:
        importType === "Images" ? URL.createObjectURL(selectedFile) : null,
      // Add parsed data for CSV files
      parsedData: parsedData,
    };

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);

          // Call the onFileUploaded callback with device ID and file data ONCE using ref
          if (onFileUploaded && device && !uploadCallbackRef.current) {
            uploadCallbackRef.current = true;
            onFileUploaded(device.id, fileData);
          }

          // Close modal and reset state
          setTimeout(() => {
            onClose();
            setSelectedFile(null);
            setUploadProgress(0);
            uploadCallbackRef.current = false; // Reset for next upload
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{typeInfo.icon}</span>
              <div>
                <h3 className="text-xl font-bold">{typeInfo.title}</h3>
                <p className="text-blue-100 text-sm">{device?.name}</p>
              </div>
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

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-600 mb-6">{typeInfo.description}</p>

          {/* File Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
              dragActive
                ? "border-blue-500 bg-blue-50"
                : selectedFile
                ? "border-green-500 bg-green-50"
                : "border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {selectedFile ? (
              <div className="space-y-3">
                <div className="text-green-600">
                  <svg
                    className="w-12 h-12 mx-auto mb-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-800">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-red-500 hover:text-red-700 text-sm font-medium"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-gray-400">
                  <svg
                    className="w-12 h-12 mx-auto mb-2"
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
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-700">
                    Drop files here or click to browse
                  </p>
                  <p className="text-sm text-gray-500">
                    Accepted formats: {typeInfo.accept} • Max size:{" "}
                    {typeInfo.maxSize}
                  </p>
                </div>
                <input
                  type="file"
                  accept={typeInfo.accept}
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-input"
                />
                <label
                  htmlFor="file-input"
                  className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200 cursor-pointer"
                >
                  Browse Files
                </label>
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Uploading...
                </span>
                <span className="text-sm text-gray-500">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3 mt-6">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              disabled={isUploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isUploading ? "Uploading..." : "Upload File"}
            </button>
          </div>

          {/* File Info */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">
              Import Guidelines:
            </h4>
            <ul className="text-sm text-gray-600 space-y-1">
              {importType === "CSV" && (
                <>
                  <li>
                    • <strong>File format:</strong> Only .csv files accepted
                  </li>
                  <li>• First row should contain column headers</li>
                  <li>• Include timestamp, location, and measurement data</li>
                  <li>• Use standard date format (YYYY-MM-DD)</li>
                </>
              )}
              {importType === "LAS" && (
                <>
                  <li>
                    • <strong>File format:</strong> Only .las files accepted
                  </li>
                  <li>• Ensure coordinate system is specified</li>
                  <li>• Include point classification if available</li>
                  <li>• Verify file integrity before upload</li>
                </>
              )}
              {importType === "Images" && (
                <>
                  <li>
                    • <strong>File formats:</strong> All image formats supported
                    (jpg, png, gif, bmp, webp, tiff)
                  </li>
                  <li>• Include GPS metadata if available</li>
                  <li>• Use high resolution for better analysis</li>
                  <li>• Organize by date and location</li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportModal;
