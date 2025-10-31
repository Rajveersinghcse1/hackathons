import React, { useState, useEffect, useRef } from 'react';

const DroneProgressModal = ({ isOpen, onClose, device }) => {
  const [activeTab, setActiveTab] = useState('progress');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Ready to start analysis');
  const [processedImages, setProcessedImages] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isComplete, setIsComplete] = useState(false);
  const [droneImage, setDroneImage] = useState(null);
  const [isLoadingImage, setIsLoadingImage] = useState(false);
  const [autoStartTriggered, setAutoStartTriggered] = useState(false);
  const progressInterval = useRef(null);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab('progress');
      setIsProcessing(false);
      setProgress(0);
      setStatus('Loading drone image...');
      setProcessedImages([]);
      setAnalysisResults(null);
      setIsComplete(false);
      setDroneImage(null);
      setIsLoadingImage(true);
      setAutoStartTriggered(false);
      
      // Auto-load drone image when modal opens
      loadDroneImage();
    }
  }, [isOpen]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, []);

  const loadDroneImage = async () => {
    try {
      setIsLoadingImage(true);
      setStatus('Loading drone image...');
      
      // Simulate image loading delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Set a placeholder drone image
      setDroneImage('https://via.placeholder.com/800x450/8B4513/FFFFFF?text=Mining+Site+Drone+View');
      setStatus('Drone image loaded successfully');
      setIsLoadingImage(false);
      
      // Auto-trigger analysis after image loads
      setTimeout(() => {
        if (!autoStartTriggered) {
          setAutoStartTriggered(true);
          startAnalysis();
        }
      }, 1000);
      
    } catch (error) {
      console.error('Error loading drone image:', error);
      setStatus('Error loading drone image');
      setIsLoadingImage(false);
    }
  };

  const startAnalysis = async () => {
    try {
      setIsProcessing(true);
      setProgress(0);
      setStatus('Initializing deep mining analysis...');
      setIsComplete(false);
      setProcessedImages([]);
      setAnalysisResults(null);

      // Start the comprehensive mining analysis
      const response = await fetch('http://localhost:5002/api/start-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id: device?.id || 'drone-1',
          analysis_type: 'deep_mining_analysis',
          include_charts: true,
          include_tables: true,
          generate_multiple_outputs: true
        })
      });

      if (response.ok) {
        // Start polling for progress updates
        progressInterval.current = setInterval(async () => {
          try {
            const progressResponse = await fetch('http://localhost:5002/api/progress');
            const progressData = await progressResponse.json();
            
            setProgress(progressData.progress || 0);
            setStatus(progressData.status || 'Processing...');
            
            if (progressData.complete) {
              clearInterval(progressInterval.current);
              setIsProcessing(false);
              setIsComplete(true);
              
              if (progressData.results) {
                setAnalysisResults(progressData.results);
              }
              
              if (progressData.processed_images) {
                setProcessedImages(progressData.processed_images);
              }
              
              // Auto-switch to results tab when complete
              setTimeout(() => {
                setActiveTab('table');
              }, 1000);
            }
          } catch (error) {
            console.error('Error fetching progress:', error);
          }
        }, 800);
      } else {
        setIsProcessing(false);
        setStatus('Failed to start analysis');
      }
    } catch (error) {
      console.error('Error starting analysis:', error);
      setIsProcessing(false);
      setStatus('Connection error - Make sure the analysis server is running');
    }
  };

  const resetAnalysis = () => {
    setIsProcessing(false);
    setProgress(0);
    setStatus('Ready to start new analysis');
    setProcessedImages([]);
    setAnalysisResults(null);
    setIsComplete(false);
    setAutoStartTriggered(false);
    setActiveTab('progress');
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
    }
  };

  // Tab configurations
  const tabs = [
    { id: 'progress', name: 'Progress', icon: '📊' },
    { id: 'table', name: 'Data Table', icon: '📋' },
    { id: 'charts', name: 'Charts', icon: '📈' }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-red-600 px-6 py-4 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">Deep Mining Analysis</h2>
              <p className="text-orange-100 text-sm">{device?.name || 'Drone Camera System'}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <div className="flex space-x-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-orange-600 text-white'
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {activeTab === 'progress' && (
            <div className="space-y-6">
              {/* Drone Image Display */}
              {(isLoadingImage || droneImage) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Drone View</h3>
                  <div className="aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                    {isLoadingImage ? (
                      <div className="flex items-center space-x-3">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
                        <span className="text-gray-600">Loading drone image...</span>
                      </div>
                    ) : droneImage ? (
                      <img
                        src={droneImage}
                        alt="Drone view"
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <div className="text-gray-400">
                        <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p>No image available</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {!isProcessing && !isComplete && !isLoadingImage && (
                <div className="text-center py-8">
                  <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-10 h-10 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Auto-Starting Deep Analysis</h3>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto">
                    Comprehensive AI-powered analysis will begin automatically after image loading completes.
                  </p>
                  <button
                    onClick={startAnalysis}
                    disabled={autoStartTriggered}
                    className={`px-8 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2 mx-auto ${
                      autoStartTriggered 
                        ? 'bg-gray-400 text-white cursor-not-allowed' 
                        : 'bg-orange-600 hover:bg-orange-700 text-white'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{autoStartTriggered ? 'Auto-Starting...' : 'Start Manual Analysis'}</span>
                  </button>
                </div>
              )}

              {isProcessing && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Deep Mining Analysis in Progress</h3>
                    <p className="text-gray-600">AI is processing drone footage with advanced algorithms...</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Analysis Progress</span>
                      <span className="text-sm font-bold text-orange-600">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-orange-500 to-red-600 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600">{status}</p>
                  </div>

                  <div className="text-center">
                    <button
                      onClick={resetAnalysis}
                      className="px-6 py-2 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors"
                    >
                      Cancel Analysis
                    </button>
                  </div>
                </div>
              )}

              {isComplete && (
                <div className="space-y-6">
                  <div className="text-center py-4">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-green-800">Deep Analysis Complete!</h3>
                    <p className="text-gray-600">Mining site analysis completed successfully. Check other tabs for detailed results.</p>
                  </div>

                  {processedImages.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Generated Output Images</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {processedImages.map((imagePath, index) => (
                          <div key={index} className="bg-gray-100 rounded-lg p-3">
                            <div className="aspect-video bg-gray-200 rounded-lg mb-2 flex items-center justify-center">
                              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                            <p className="text-xs text-gray-600 truncate" title={imagePath}>
                              {imagePath.split('\\').pop() || imagePath.split('/').pop()}
                            </p>
                            <button
                              onClick={() => window.open(`file:///${imagePath}`, '_blank')}
                              className="w-full mt-2 px-3 py-1 bg-orange-600 text-white text-xs rounded hover:bg-orange-700 transition-colors"
                            >
                              View Full Image
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3 pt-4">
                    <button
                      onClick={resetAnalysis}
                      className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium"
                    >
                      Run New Analysis
                    </button>
                    <button
                      onClick={() => setActiveTab('table')}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      View Data Table
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'table' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Analysis Data Table</h3>
              {analysisResults ? (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Analysis Summary</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          <tr>
                            <td className="px-4 py-2 text-sm font-medium text-gray-900">Overall Quality Score</td>
                            <td className="px-4 py-2 text-sm text-gray-600">{analysisResults.average_quality?.toFixed(1) || 'N/A'}/100</td>
                            <td className="px-4 py-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                (analysisResults.average_quality || 0) > 80 ? 'bg-green-100 text-green-800' : 
                                (analysisResults.average_quality || 0) > 60 ? 'bg-yellow-100 text-yellow-800' : 
                                'bg-red-100 text-red-800'
                              }`}>
                                {(analysisResults.average_quality || 0) > 80 ? 'Excellent' : 
                                 (analysisResults.average_quality || 0) > 60 ? 'Good' : 'Needs Attention'}
                              </span>
                            </td>
                          </tr>
                          <tr>
                            <td className="px-4 py-2 text-sm font-medium text-gray-900">Features Detected</td>
                            <td className="px-4 py-2 text-sm text-gray-600">{analysisResults.total_features || 0}</td>
                            <td className="px-4 py-2">
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                Detected
                              </span>
                            </td>
                          </tr>
                          <tr>
                            <td className="px-4 py-2 text-sm font-medium text-gray-900">Potential Issues</td>
                            <td className="px-4 py-2 text-sm text-gray-600">{analysisResults.total_issues || 0}</td>
                            <td className="px-4 py-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                (analysisResults.total_issues || 0) === 0 ? 'bg-green-100 text-green-800' : 
                                (analysisResults.total_issues || 0) < 5 ? 'bg-yellow-100 text-yellow-800' : 
                                'bg-red-100 text-red-800'
                              }`}>
                                {(analysisResults.total_issues || 0) === 0 ? 'Safe' : 
                                 (analysisResults.total_issues || 0) < 5 ? 'Monitor' : 'Critical'}
                              </span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Available</h3>
                  <p className="text-gray-600">Complete an analysis to view detailed data tables.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'charts' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Analysis Charts & Visualizations</h3>
              {analysisResults ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Quality Distribution</h4>
                    <div className="h-48 flex items-center justify-center bg-white rounded">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-orange-600 mb-2">
                          {analysisResults.average_quality?.toFixed(1) || '0'}%
                        </div>
                        <div className="text-sm text-gray-600">Average Quality Score</div>
                        <div className="mt-4 w-32 h-2 bg-gray-200 rounded-full mx-auto">
                          <div 
                            className="h-2 bg-gradient-to-r from-orange-500 to-red-600 rounded-full"
                            style={{ width: `${analysisResults.average_quality || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Detection Summary</h4>
                    <div className="h-48 flex items-center justify-center bg-white rounded">
                      <div className="flex space-x-8">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600 mb-1">
                            {analysisResults.total_features || 0}
                          </div>
                          <div className="text-xs text-gray-600">Features</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600 mb-1">
                            {analysisResults.total_issues || 0}
                          </div>
                          <div className="text-xs text-gray-600">Issues</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Charts Available</h3>
                  <p className="text-gray-600">Complete an analysis to view charts and visualizations.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DroneProgressModal;