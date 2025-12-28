import React, { useState } from 'react';

const ThemeSwitcher = ({ currentTheme, onThemeChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const themes = [
    {
      id: 'light',
      name: 'Light',
      icon: '☀️',
      description: 'Clean and bright interface',
      colors: ['bg-white', 'bg-gray-100', 'bg-blue-500']
    },
    {
      id: 'dark',
      name: 'Dark',
      icon: '🌙',
      description: 'Easy on the eyes, perfect for night work',
      colors: ['bg-gray-900', 'bg-gray-800', 'bg-blue-600']
    },
    {
      id: 'auto',
      name: 'System',
      icon: '🖥️',
      description: 'Matches your device settings',
      colors: ['bg-gradient-to-r from-gray-900 to-white', 'bg-gray-400', 'bg-purple-500']
    },
    {
      id: 'cyberpunk',
      name: 'Cyberpunk',
      icon: '🔮',
      description: 'Neon-inspired futuristic theme',
      colors: ['bg-black', 'bg-cyan-400', 'bg-pink-500']
    },
    {
      id: 'nature',
      name: 'Nature',
      icon: '🌲',
      description: 'Earth tones and natural colors',
      colors: ['bg-green-50', 'bg-green-200', 'bg-green-600']
    },
    {
      id: 'ocean',
      name: 'Ocean',
      icon: '🌊',
      description: 'Deep blues and aqua tones',
      colors: ['bg-blue-50', 'bg-blue-200', 'bg-blue-700']
    }
  ];

  const handleThemeSelect = (themeId) => {
    onThemeChange(themeId);
    setIsOpen(false);
  };

  const currentThemeData = themes.find(theme => theme.id === currentTheme) || themes[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 bg-white rounded-xl border border-gray-200 hover:border-gray-300 transition-all duration-200 hover:shadow-lg group"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-lg">
              🎨
            </div>
            <div className="text-left">
              <h4 className="text-sm font-semibold text-gray-900">Theme</h4>
              <p className="text-xs text-gray-500">
                {currentThemeData.name} - {currentThemeData.description}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              {currentThemeData.colors.map((color, index) => (
                <div key={index} className={`w-4 h-4 rounded-full ${color} border border-gray-200`}></div>
              ))}
            </div>
            <svg 
              className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-200 p-2 z-50 max-h-96 overflow-y-auto">
          <div className="grid grid-cols-1 gap-2">
            {themes.map((theme) => (
              <button
                key={theme.id}
                onClick={() => handleThemeSelect(theme.id)}
                className={`p-3 rounded-lg text-left hover:bg-gray-50 transition-all duration-200 border-2 ${
                  currentTheme === theme.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-transparent hover:border-gray-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{theme.icon}</span>
                    <div>
                      <div className="font-semibold text-gray-900 text-sm">{theme.name}</div>
                      <div className="text-xs text-gray-500">{theme.description}</div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-1">
                    {theme.colors.map((color, index) => (
                      <div key={index} className={`w-3 h-3 rounded-full ${color} border border-gray-200`}></div>
                    ))}
                  </div>
                </div>
              </button>
            ))}
          </div>
          
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="text-xs text-gray-500 px-3">
              💡 Tip: Dark themes can help reduce eye strain during long work sessions
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThemeSwitcher;