import React, { useState, useEffect } from "react";
import DashboardNavbar from "../Components/DashboardNavbar";

const Report = () => {
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  // Report categories based on Upload folder structure
  const categories = [
    { id: "all", name: "All Reports", icon: "📋", color: "blue" },
    { id: "extensometer", name: "Extensometer", icon: "📏", color: "purple" },
    { id: "geophone", name: "Geophone", icon: "🔊", color: "green" },
    { id: "piezometer", name: "Piezometer", icon: "💧", color: "cyan" },
    { id: "lidar", name: "LiDAR", icon: "📡", color: "orange" },
    { id: "gb-insar", name: "GB-InSAR", icon: "🛰️", color: "red" },
    { id: "weather", name: "Weather Station", icon: "🌤️", color: "yellow" },
  ];

  // Report data - all reports from Upload folder structure
  const allReports = [
    // Extensometer Reports
    {
      id: 1,
      title: "Extensometer Analysis Report",
      category: "extensometer",
      date: "2024-10-26",
      size: "48 KB",
      type: "PDF",
      path: "/Upload/Extensometer/Report/extensometer_report.pdf",
      description:
        "Comprehensive analysis of extensometer data and displacement measurements",
      status: "completed",
      author: "System",
    },
    {
      id: 2,
      title: "Extensometer Analysis Report #1",
      category: "extensometer",
      date: "2024-10-26",
      size: "48 KB",
      type: "PDF",
      path: "/Upload/Extensometer/Report/extensometer_report_1.pdf",
      description:
        "Historical extensometer data analysis with detailed displacement tracking",
      status: "completed",
      author: "System",
    },
    {
      id: 3,
      title: "Extensometer 3D Interactive Dashboard",
      category: "extensometer",
      date: "2024-10-26",
      size: "4.6 MB",
      type: "HTML",
      path: "/Upload/Extensometer/3-D/interactive_dashboard.html",
      description:
        "Interactive 3D visualization of extensometer measurements and trends",
      status: "completed",
      author: "System",
    },

    // Geophone Reports
    {
      id: 4,
      title: "Geophone Rockfall Analysis",
      category: "geophone",
      date: "2024-10-26",
      size: "76 KB",
      type: "PDF",
      path: "/Upload/Geophone/Report/geophone_rockfall_report.pdf",
      description:
        "Seismic activity monitoring and rockfall prediction analysis",
      status: "completed",
      author: "System",
    },
    {
      id: 5,
      title: "Geophone Analysis Report",
      category: "geophone",
      date: "2024-10-26",
      size: "9 KB",
      type: "JSON",
      path: "/Upload/Geophone/Report/geophone_analysis_report.json",
      description:
        "Detailed geophone data analysis in JSON format for API integration",
      status: "completed",
      author: "System",
    },
    {
      id: 6,
      title: "Rockfall Alerts Log",
      category: "geophone",
      date: "2024-10-26",
      size: "38 KB",
      type: "CSV",
      path: "/Upload/Geophone/Report/rockfall_alerts.csv",
      description:
        "Time-series log of rockfall detection events and alert triggers",
      status: "completed",
      author: "System",
    },
    {
      id: 7,
      title: "Geophone 3D Interactive Dashboard",
      category: "geophone",
      date: "2024-10-26",
      size: "4.6 MB",
      type: "HTML",
      path: "/Upload/Geophone/3-D/interactive_dashboard.html",
      description:
        "Interactive 3D visualization of seismic activity and rockfall events",
      status: "completed",
      author: "System",
    },

    // Piezometer Reports
    {
      id: 8,
      title: "Piezometer Landslide Analysis",
      category: "piezometer",
      date: "2024-10-26",
      size: "29 KB",
      type: "PDF",
      path: "/Upload/Piezometer/Report/report.pdf",
      description:
        "Groundwater pressure monitoring and landslide risk assessment",
      status: "completed",
      author: "System",
    },

    // LiDAR Reports
    {
      id: 9,
      title: "LiDAR Terrain Analysis",
      category: "lidar",
      date: "2024-10-26",
      size: "169 KB",
      type: "PDF",
      path: "/Upload/LiDAR/Report/lidar_rockfall_report.pdf",
      description: "3D terrain mapping and rockfall trajectory analysis",
      status: "completed",
      author: "System",
    },
    {
      id: 10,
      title: "LiDAR 3D Clustering Analysis",
      category: "lidar",
      date: "2024-10-26",
      size: "5.0 MB",
      type: "HTML",
      path: "/Upload/LiDAR/3-D/clustering_3d.html",
      description:
        "Interactive 3D point cloud clustering and terrain visualization",
      status: "completed",
      author: "System",
    },

    // GB-InSAR Reports
    {
      id: 11,
      title: "GB-InSAR Deformation Report",
      category: "gb-insar",
      date: "2024-10-26",
      size: "53 KB",
      type: "PDF",
      path: "/Upload/GB-InSAR/Reports/gbinsar_rockfall_report.pdf",
      description: "Ground-based radar interferometry deformation analysis",
      status: "completed",
      author: "System",
    },

    // Weather Station Reports
    {
      id: 12,
      title: "Weather Station Analysis",
      category: "weather",
      date: "2024-10-26",
      size: "100 KB",
      type: "PDF",
      path: "/Upload/Auto_Weather_station/Report/weather_analysis_report.pdf",
      description:
        "Environmental conditions and weather impact analysis on slope stability",
      status: "completed",
      author: "System",
    },
  ];

  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      setReports(allReports);
      setLoading(false);
    }, 800);
  }, []);

  const filteredReports = reports.filter((report) => {
    const matchesCategory =
      activeCategory === "all" || report.category === activeCategory;
    const matchesSearch =
      report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleDownload = (report) => {
    try {
      // Create a temporary link element to trigger download
      const link = document.createElement("a");
      link.href = report.path;
      link.download = report.path.split("/").pop(); // Extract filename from path
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Download error:", error);
      alert(
        `Error downloading file. Please check if the file exists at: ${report.path}`
      );
    }
  };

  const handleView = (report) => {
    try {
      // Open file in a new browser tab for viewing
      // Use the full URL to ensure it bypasses React Router
      const fullUrl = `${window.location.origin}${report.path}`;
      console.log(`Opening file at: ${fullUrl}`);

      const newWindow = window.open(fullUrl, "_blank");

      if (
        !newWindow ||
        newWindow.closed ||
        typeof newWindow.closed === "undefined"
      ) {
        alert("Pop-up blocked! Please allow pop-ups for this site.");
      }
    } catch (error) {
      console.error("View error:", error);
      alert(
        `Error opening file. Please check if the file exists at: ${report.path}`
      );
    }
  };

  const getCategoryColor = (color) => {
    const colors = {
      blue: "from-blue-500 to-blue-600",
      purple: "from-purple-500 to-purple-600",
      green: "from-green-500 to-green-600",
      cyan: "from-cyan-500 to-cyan-600",
      orange: "from-orange-500 to-orange-600",
      red: "from-red-500 to-red-600",
      yellow: "from-yellow-500 to-yellow-600",
    };
    return colors[color] || colors.blue;
  };

  const getCategoryStats = (categoryId) => {
    if (categoryId === "all") return reports.length;
    return reports.filter((r) => r.category === categoryId).length;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      <DashboardNavbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                Reports & Analytics
              </h1>
              <p className="text-gray-600 text-lg">
                Access and download comprehensive analysis reports from all
                monitoring devices
              </p>
            </div>
            <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold shadow-lg flex items-center space-x-2">
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <span>Generate New Report</span>
            </button>
          </div>

          {/* Search Bar */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-gray-200">
            <div className="relative">
              <input
                type="text"
                placeholder="Search reports by title or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-6 py-4 pl-14 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700 placeholder-gray-400 transition-all"
              />
              <div className="absolute left-5 top-4 text-gray-400 text-xl">
                🔍
              </div>
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Category Filters */}
        <div className="mb-8 overflow-x-auto">
          <div className="flex space-x-4 pb-4">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 whitespace-nowrap ${
                  activeCategory === category.id
                    ? `bg-gradient-to-r ${getCategoryColor(
                        category.color
                      )} text-white shadow-lg transform scale-105`
                    : "bg-white text-gray-700 hover:bg-gray-100 border border-gray-200"
                }`}
              >
                <span className="text-xl">{category.icon}</span>
                <span>{category.name}</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-bold ${
                    activeCategory === category.id
                      ? "bg-white/20"
                      : "bg-gray-200"
                  }`}
                >
                  {getCategoryStats(category.id)}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Reports Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium">Loading reports...</p>
            </div>
          </div>
        ) : filteredReports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredReports.map((report) => {
              const category = categories.find((c) => c.id === report.category);
              return (
                <div
                  key={report.id}
                  className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-200"
                >
                  <div
                    className={`bg-gradient-to-r ${getCategoryColor(
                      category.color
                    )} p-6 text-white`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <span className="text-4xl">{category.icon}</span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          report.type === "HTML"
                            ? "bg-green-500/30 text-white border border-white/30"
                            : report.type === "CSV"
                            ? "bg-yellow-500/30 text-white border border-white/30"
                            : report.type === "JSON"
                            ? "bg-purple-500/30 text-white border border-white/30"
                            : "bg-white/20 text-white"
                        }`}
                      >
                        {report.type === "HTML"
                          ? "📊 Interactive"
                          : report.type === "CSV"
                          ? "📈 CSV Data"
                          : report.type === "JSON"
                          ? "📋 JSON Data"
                          : "📄 PDF"}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-2">{report.title}</h3>
                    <p className="text-sm opacity-90">{category.name}</p>
                  </div>

                  <div className="p-6">
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {report.description}
                    </p>

                    <div className="space-y-2 mb-6">
                      <div className="flex items-center text-sm text-gray-500">
                        <svg
                          className="w-4 h-4 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        {new Date(report.date).toLocaleDateString("en-US", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                        })}
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <svg
                          className="w-4 h-4 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                          />
                        </svg>
                        {report.size}
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <svg
                          className="w-4 h-4 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          />
                        </svg>
                        {report.author}
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <button
                        onClick={() => handleView(report)}
                        className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold flex items-center justify-center space-x-2"
                      >
                        <svg
                          className="w-4 h-4"
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
                        <span>{report.type === "HTML" ? "Open" : "View"}</span>
                      </button>
                      <button
                        onClick={() => handleDownload(report)}
                        className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-all duration-300 font-semibold flex items-center justify-center space-x-2"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                          />
                        </svg>
                        <span>Download</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-xl p-16 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              No Reports Found
            </h3>
            <p className="text-gray-600">
              {searchQuery
                ? `No reports match your search "${searchQuery}"`
                : `No reports available in ${
                    categories.find((c) => c.id === activeCategory)?.name
                  }`}
            </p>
          </div>
        )}

        {/* Summary Stats */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-2xl shadow-xl p-6 text-center border border-blue-100">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-2xl font-bold text-gray-900">
              {reports.length}
            </div>
            <div className="text-sm text-gray-600">Total Reports</div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-6 text-center border border-green-100">
            <div className="text-3xl mb-2">✅</div>
            <div className="text-2xl font-bold text-gray-900">
              {reports.filter((r) => r.status === "completed").length}
            </div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-6 text-center border border-purple-100">
            <div className="text-3xl mb-2">📅</div>
            <div className="text-2xl font-bold text-gray-900">This Week</div>
            <div className="text-sm text-gray-600">Latest Reports</div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-6 text-center border border-orange-100">
            <div className="text-3xl mb-2">📁</div>
            <div className="text-2xl font-bold text-gray-900">
              {categories.length - 1}
            </div>
            <div className="text-sm text-gray-600">Categories</div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Report;
