import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Navbar = ({ onSignInClick, onGetStartedClick }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <nav className="w-full bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold shadow-lg">
              G
            </div>
            <span className="font-bold text-xl text-gray-800">
              GeoTech Predictor
            </span>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden lg:flex space-x-8 text-gray-600 font-medium">
            <a href="#features" className="hover:text-blue-600 transition-colors duration-200">Features</a>
            <a href="#technology" className="hover:text-blue-600 transition-colors duration-200">Technology</a>
            <a href="#about" className="hover:text-blue-600 transition-colors duration-200">About</a>
            <a href="#contact" className="hover:text-blue-600 transition-colors duration-200">Contact</a>
            <button 
              onClick={() => navigate('/devices')}
              className="hover:text-blue-600 transition-colors duration-200 cursor-pointer"
            >
              Devices
            </button>
          </div>

          {/* Desktop Right Side */}
          <div className="hidden lg:flex items-center space-x-6">
            {/* API Status */}
            <div className="flex items-center space-x-2 text-sm text-gray-500 bg-gray-50 px-3 py-1 rounded-full">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="font-medium">API Connected</span>
            </div>

            {/* Sign In */}
            <button 
              onClick={onSignInClick}
              className="text-gray-600 font-medium hover:text-blue-600 transition-colors duration-200 cursor-pointer"
            >
              Sign In
            </button>

            {/* CTA Button */}
            <button 
              onClick={onGetStartedClick}
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 font-medium cursor-pointer"
            >
              Get Started Free
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none focus:text-gray-900 p-2"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="lg:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t">
              <a href="#features" className="block px-3 py-2 text-gray-600 hover:text-blue-600 font-medium">Features</a>
              <a href="#technology" className="block px-3 py-2 text-gray-600 hover:text-blue-600 font-medium">Technology</a>
              <a href="#about" className="block px-3 py-2 text-gray-600 hover:text-blue-600 font-medium">About</a>
              <a href="#contact" className="block px-3 py-2 text-gray-600 hover:text-blue-600 font-medium">Contact</a>
              <button 
                onClick={() => navigate('/devices')}
                className="block px-3 py-2 text-gray-600 hover:text-blue-600 font-medium cursor-pointer w-full text-left"
              >
                Devices
              </button>
              
              {/* Mobile API Status */}
              <div className="flex items-center space-x-2 text-sm text-gray-500 px-3 py-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span className="font-medium">API Connected</span>
              </div>
              
              {/* Mobile buttons */}
              <div className="px-3 py-2 space-y-2">
                <button 
                  onClick={onSignInClick}
                  className="w-full text-left text-gray-600 font-medium hover:text-blue-600 py-2 cursor-pointer"
                >
                  Sign In
                </button>
                <button 
                  onClick={onGetStartedClick}
                  className="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg font-medium cursor-pointer"
                >
                  Get Started Free
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
