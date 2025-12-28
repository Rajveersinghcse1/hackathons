import React, { useState, useRef } from 'react';

const AvatarUpload = ({ 
  currentAvatar, 
  onAvatarChange, 
  userName = 'User',
  size = 'lg',
  allowEdit = true,
  className = ''
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32',
    xl: 'w-40 h-40'
  };

  const buttonSizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-10 h-10'
  };

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setIsUploading(true);
      
      // Simulate upload process
      setTimeout(() => {
        const reader = new FileReader();
        reader.onload = (e) => {
          onAvatarChange(e.target.result);
          setIsUploading(false);
        };
        reader.readAsDataURL(file);
      }, 1000);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const generateGradientAvatar = () => {
    const gradients = [
      'from-purple-400 to-pink-400',
      'from-blue-400 to-cyan-400',
      'from-green-400 to-blue-500',
      'from-orange-400 to-red-400',
      'from-indigo-400 to-purple-400',
      'from-pink-400 to-red-400'
    ];
    const randomGradient = gradients[Math.floor(Math.random() * gradients.length)];
    return `bg-gradient-to-br ${randomGradient}`;
  };

  const initials = userName.split(' ').map(n => n[0]).join('').toUpperCase();

  return (
    <div className={`relative group ${className}`}>
      <div
        className={`${sizeClasses[size]} rounded-full relative overflow-hidden ring-4 ring-white shadow-2xl ${
          dragOver ? 'ring-blue-500 ring-opacity-50' : ''
        } transition-all duration-300`}
        onDrop={allowEdit ? handleDrop : undefined}
        onDragOver={allowEdit ? handleDragOver : undefined}
        onDragLeave={allowEdit ? handleDragLeave : undefined}
      >
        {isUploading ? (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : currentAvatar ? (
          <img
            src={currentAvatar}
            alt={userName}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className={`w-full h-full ${generateGradientAvatar()} flex items-center justify-center text-white font-bold text-${size === 'xl' ? '4xl' : size === 'lg' ? '2xl' : size === 'md' ? 'xl' : 'lg'}`}>
            {initials}
          </div>
        )}

        {/* Overlay on hover */}
        {allowEdit && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 cursor-pointer">
            <div className="text-white text-center">
              <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="text-xs font-medium">Change</span>
            </div>
          </div>
        )}
      </div>

      {/* Edit Button */}
      {allowEdit && (
        <button
          onClick={() => fileInputRef.current?.click()}
          className={`absolute bottom-0 right-0 ${buttonSizeClasses[size]} bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg border-2 border-white transition-all duration-200 hover:scale-110 flex items-center justify-center`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
      )}

      {/* Status Indicator */}
      <div className="absolute top-0 right-0 w-4 h-4 bg-green-400 border-2 border-white rounded-full animate-pulse"></div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFileSelect(e.target.files[0])}
        className="hidden"
      />

      {/* Upload Instructions */}
      {allowEdit && dragOver && (
        <div className="absolute inset-0 rounded-full border-2 border-dashed border-blue-500 bg-blue-50 bg-opacity-90 flex items-center justify-center">
          <div className="text-center text-blue-700">
            <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="text-xs font-medium">Drop image</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AvatarUpload;