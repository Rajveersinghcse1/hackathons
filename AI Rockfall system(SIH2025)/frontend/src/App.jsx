import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './Pages/Landing'
import Dashboard from './Pages/Dashboard'
import Sites from './Pages/Sites'
import Device from './Pages/Device'
import Prediction from './Pages/Prediction'
import Report from './Pages/Report'
import UserProfile from './Pages/UserProfile'
import Settings from './Pages/Settings'
import HelpService from './Pages/HelpService'
import DroneDashboard from './Pages/DroneDashboard'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  return isLoggedIn ? children : <Navigate to="/" replace />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />

        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/sites" 
          element={
            <ProtectedRoute>
              <Sites />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/devices" 
          element={
            <ProtectedRoute>
              <Device />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/prediction" 
          element={
            <ProtectedRoute>
              <Prediction />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/report" 
          element={
            <ProtectedRoute>
              <Report />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <UserProfile />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/help" 
          element={
            <ProtectedRoute>
              <HelpService />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/drones" 
          element={
            <ProtectedRoute>
              <DroneDashboard />
            </ProtectedRoute>
          } 
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
