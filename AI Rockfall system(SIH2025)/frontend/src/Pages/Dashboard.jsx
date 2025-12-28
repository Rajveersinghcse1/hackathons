import React, { useState, useEffect } from "react";
import DashboardNavbar from "../Components/DashboardNavbar";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const Dashboard = () => {
  // Random greetings array
  const greetings = [
    "Great to see you here! 👋",
    "Ready to make today productive? 🚀",
    "Let's monitor those predictions! 📊",
    "Hope you're having a fantastic day! ✨",
    "Time to track some data! 📈",
    "Welcome to your command center! 🎯",
    "Let's keep those operations safe! 🛡️",
    "Ready to analyze today's insights? 💡",
    "Another day, another prediction! 🔮",
    "Your safety dashboard awaits! 🌟",
  ];

  // Select a random greeting on component mount
  const [currentGreeting] = useState(() => {
    return greetings[Math.floor(Math.random() * greetings.length)];
  });

  const stats = [
    {
      title: "Active Sites",
      value: "4",
      change: "+12%",
      changeType: "positive",
      icon: "📍",
    },
    {
      title: "Devices Data",
      value: "7",
      change: "+5%",
      changeType: "positive",
      icon: "📱",
    },
    {
      title: "Predictions Today",
      value: "2",
      change: "+18%",
      changeType: "positive",
      icon: "🔮",
    },
    {
      title: "Critical Alerts",
      value: "0",
      change: "-100%",
      changeType: "positive",
      icon: "🚨",
    },
  ];

  // Extensometer Crack Monitoring Data (Last 30 days)
  const crackMonitoringData = [
    { date: "Sep 18", opening: 0.55, cumulative: 0.55, rate: 0.0 },
    { date: "Sep 20", opening: 0.54, cumulative: 2.22, rate: 0.27 },
    { date: "Sep 22", opening: 0.65, cumulative: 4.29, rate: 0.12 },
    { date: "Sep 24", opening: 0.73, cumulative: 7.19, rate: 0.1 },
    { date: "Sep 26", opening: 0.83, cumulative: 12.3, rate: 0.1 },
    { date: "Sep 28", opening: 0.95, cumulative: 18.13, rate: 0.19 },
    { date: "Sep 30", opening: 0.99, cumulative: 19.92, rate: -0.17 },
    { date: "Oct 2", opening: 1.08, cumulative: 24.94, rate: 0.04 },
    { date: "Oct 4", opening: 1.26, cumulative: 33.16, rate: 0.24 },
    { date: "Oct 6", opening: 1.39, cumulative: 44.74, rate: 0.1 },
    { date: "Oct 8", opening: 1.66, cumulative: 58.51, rate: 0.11 },
    { date: "Oct 10", opening: 1.94, cumulative: 71.54, rate: 0.14 },
    { date: "Oct 12", opening: 1.86, cumulative: 79.15, rate: -0.04 },
    { date: "Oct 14", opening: 2.14, cumulative: 91.29, rate: 0.12 },
    { date: "Oct 16", opening: 2.36, cumulative: 104.98, rate: 0.17 },
    { date: "Oct 17", opening: 2.69, cumulative: 117.42, rate: 0.11 },
  ];

  // Weather Station Data (Last 7 days hourly averages)
  const weatherData = [
    { time: "Mon", temp: 21.7, humidity: 61.9, wind: 3.9, rainfall: 0 },
    { time: "Tue", temp: 24.5, humidity: 58.5, wind: 5.2, rainfall: 5.8 },
    { time: "Wed", temp: 27.8, humidity: 55.4, wind: 6.5, rainfall: 0 },
    { time: "Thu", temp: 25.3, humidity: 63.2, wind: 4.8, rainfall: 6.5 },
    { time: "Fri", temp: 23.1, humidity: 65.1, wind: 3.5, rainfall: 0 },
    { time: "Sat", temp: 26.9, humidity: 57.8, wind: 5.9, rainfall: 3.4 },
    { time: "Sun", temp: 29.2, humidity: 54.2, wind: 7.1, rainfall: 0 },
  ];

  // Piezometer Pressure Trends (Last 30 readings)
  const piezometerData = [
    { reading: "1", pressure: -0.77, groundwater: 1.24 },
    { reading: "5", pressure: -1.52, groundwater: 0.36 },
    { reading: "10", pressure: -0.78, groundwater: 0.63 },
    { reading: "15", pressure: -0.34, groundwater: 1.09 },
    { reading: "20", pressure: -0.84, groundwater: -0.001 },
    { reading: "25", pressure: -0.27, groundwater: 0.26 },
    { reading: "30", pressure: -0.57, groundwater: -0.56 },
    { reading: "35", pressure: -0.81, groundwater: -0.37 },
    { reading: "40", pressure: 0.98, groundwater: 0.21 },
    { reading: "45", pressure: 0.46, groundwater: -0.62 },
    { reading: "50", pressure: 1.16, groundwater: 0.71 },
    { reading: "55", pressure: 1.03, groundwater: -2.08 },
    { reading: "60", pressure: 2.27, groundwater: -1.51 },
    { reading: "64", pressure: -0.87, groundwater: 1.78 },
  ];

  // Risk Distribution Data
  const riskDistribution = [
    { name: "Low Risk", value: 19, color: "#10B981" },
    { name: "Medium Risk", value: 31, color: "#F59E0B" },
    { name: "High Risk", value: 14, color: "#EF4444" },
  ];

  // Seismic Activity Data (Geophone)
  const seismicActivity = [
    { date: "Oct 11", microseismic: 12, minor: 8, moderate: 2 },
    { date: "Oct 12", microseismic: 15, minor: 5, moderate: 1 },
    { date: "Oct 13", microseismic: 10, minor: 9, moderate: 3 },
    { date: "Oct 14", microseismic: 8, minor: 12, moderate: 2 },
    { date: "Oct 15", microseismic: 14, minor: 7, moderate: 1 },
    { date: "Oct 16", microseismic: 11, minor: 10, moderate: 4 },
    { date: "Oct 17", microseismic: 9, minor: 11, moderate: 2 },
  ];

  const COLORS = ["#10B981", "#F59E0B", "#EF4444"];

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNavbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  {currentGreeting}
                </h1>
                <p className="text-blue-100 text-lg">
                  Monitor rockfall predictions and manage your mining operations
                  efficiently.
                </p>
              </div>
              <div className="hidden md:block">
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
                  <svg
                    className="w-12 h-12 text-white"
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
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm font-medium">
                    {stat.title}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stat.value}
                  </p>
                  <div className="flex items-center mt-2">
                    <span
                      className={`text-sm font-medium ${
                        stat.changeType === "positive"
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {stat.change}
                    </span>
                    <span className="text-gray-500 text-sm ml-1">
                      vs last week
                    </span>
                  </div>
                </div>
                <div className="text-4xl">{stat.icon}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Extensometer Crack Monitoring Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Extensometer Crack Monitoring
              </h2>
              <p className="text-sm text-gray-500">
                Real-time crack opening and cumulative displacement
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={crackMonitoringData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                />
                <YAxis
                  yAxisId="left"
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                  label={{
                    value: "Opening (mm)",
                    angle: -90,
                    position: "insideLeft",
                    style: { fontSize: 12 },
                  }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                  label={{
                    value: "Cumulative (mm)",
                    angle: 90,
                    position: "insideRight",
                    style: { fontSize: 12 },
                  }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                  }}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="opening"
                  stroke="#EF4444"
                  strokeWidth={2}
                  name="Crack Opening"
                  dot={{ fill: "#EF4444", r: 4 }}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="cumulative"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="Cumulative"
                  dot={{ fill: "#3B82F6", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Weather Parameters Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Weather Station Data
              </h2>
              <p className="text-sm text-gray-500">
                Temperature, humidity, and wind speed trends
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={weatherData}>
                <defs>
                  <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient
                    id="colorHumidity"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                />
                <YAxis tick={{ fontSize: 12 }} stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="temp"
                  stroke="#F59E0B"
                  fillOpacity={1}
                  fill="url(#colorTemp)"
                  name="Temperature (°C)"
                />
                <Area
                  type="monotone"
                  dataKey="humidity"
                  stroke="#10B981"
                  fillOpacity={1}
                  fill="url(#colorHumidity)"
                  name="Humidity (%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Piezometer Pressure Trends */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Piezometer Monitoring
              </h2>
              <p className="text-sm text-gray-500">
                Pore pressure and groundwater level variations
              </p>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={piezometerData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="reading"
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                  label={{
                    value: "Reading #",
                    position: "insideBottom",
                    offset: -5,
                    style: { fontSize: 12 },
                  }}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke="#9CA3AF"
                  label={{
                    value: "Pressure (kPa)",
                    angle: -90,
                    position: "insideLeft",
                    style: { fontSize: 12 },
                  }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#fff",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="pressure"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  name="Pore Pressure"
                  dot={{ fill: "#8B5CF6", r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="groundwater"
                  stroke="#06B6D4"
                  strokeWidth={2}
                  name="Groundwater Level"
                  dot={{ fill: "#06B6D4", r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution Pie Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Risk Level Distribution
              </h2>
              <p className="text-sm text-gray-500">
                Current risk assessment across all monitoring points
              </p>
            </div>
            <div className="flex items-center justify-between">
              <ResponsiveContainer width="60%" height={300}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="w-40 space-y-4">
                {riskDistribution.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span className="text-sm font-medium text-gray-700">
                        {item.name}
                      </span>
                    </div>
                    <span className="text-sm font-bold text-gray-900">
                      {item.value}
                    </span>
                  </div>
                ))}
                <div className="pt-4 border-t">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Total
                    </span>
                    <span className="text-sm font-bold text-gray-900">
                      {riskDistribution.reduce((a, b) => a + b.value, 0)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Seismic Activity Chart - Full Width */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-gray-900">
              Seismic Activity Monitoring (Geophone)
            </h2>
            <p className="text-sm text-gray-500">
              Daily seismic event classification and magnitude tracking
            </p>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={seismicActivity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9CA3AF" />
              <YAxis
                tick={{ fontSize: 12 }}
                stroke="#9CA3AF"
                label={{
                  value: "Number of Events",
                  angle: -90,
                  position: "insideLeft",
                  style: { fontSize: 12 },
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Bar
                dataKey="microseismic"
                stackId="a"
                fill="#10B981"
                name="Microseismic"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="minor"
                stackId="a"
                fill="#F59E0B"
                name="Minor Events"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="moderate"
                stackId="a"
                fill="#EF4444"
                name="Moderate Events"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* System Status Footer */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">System Status</p>
                <p className="text-2xl font-bold">Operational</p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Data Points Today</p>
                <p className="text-2xl font-bold">1,247</p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Last Updated</p>
                <p className="text-2xl font-bold">2 min ago</p>
              </div>
              <div className="text-4xl">⏱️</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
