import React, { useState } from 'react';
import DashboardNavbar from '../Components/DashboardNavbar';
import ProfileCard from '../Components/Profile/ProfileCard';
import AdvancedToggle from '../Components/Profile/AdvancedToggle';
import ThemeSwitcher from '../Components/Profile/ThemeSwitcher';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [settings, setSettings] = useState({
    language: 'en',
    timezone: 'UTC-8',
    theme: 'light',
    autoSave: true,
    emailNotifications: true,
    pushNotifications: true,
    predictionAlerts: true,
    profileVisibility: 'team',
    activityTracking: true,
    dataSharing: false,
    twoFactorAuth: false,
    sessionTimeout: '1hour',
    debugMode: false,
    experimentalFeatures: false
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveSettings = async () => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsLoading(false);
    console.log('Settings saved:', settings);
  };

  const tabs = [
    { id: 'general', name: 'General', icon: '⚙️', description: 'Basic settings' },
    { id: 'notifications', name: 'Notifications', icon: '🔔', description: 'Alert preferences' },
    { id: 'privacy', name: 'Privacy', icon: '🔒', description: 'Data privacy' },
    { id: 'security', name: 'Security', icon: '🛡️', description: 'Account security' },
    { id: 'advanced', name: 'Advanced', icon: '🔧', description: 'Power user options' }
  ];

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <ProfileCard 
        title="Language & Region"
        subtitle="Configure your language and timezone preferences"
        gradient="from-blue-500 to-purple-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select 
              value={settings.language}
              onChange={(e) => handleSettingChange('language', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
            <select 
              value={settings.timezone}
              onChange={(e) => handleSettingChange('timezone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="UTC-8">UTC-8 (Pacific Time)</option>
              <option value="UTC-5">UTC-5 (Eastern Time)</option>
              <option value="UTC">UTC (Greenwich Time)</option>
            </select>
          </div>
        </div>
      </ProfileCard>

      <ProfileCard 
        title="Interface Preferences"
        subtitle="Customize your experience"
        gradient="from-green-500 to-teal-600"
      >
        <div className="space-y-6">
          <ThemeSwitcher 
            currentTheme={settings.theme} 
            onThemeChange={(theme) => handleSettingChange('theme', theme)} 
          />
          
          <AdvancedToggle
            label="Auto Save"
            description="Automatically save your work"
            checked={settings.autoSave}
            onChange={(checked) => handleSettingChange('autoSave', checked)}
            color="blue"
            icon="💾"
          />
        </div>
      </ProfileCard>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <ProfileCard 
        title="Alert Preferences"
        subtitle="Configure notifications"
        gradient="from-yellow-500 to-orange-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AdvancedToggle
            label="Email Notifications"
            description="Receive alerts via email"
            checked={settings.emailNotifications}
            onChange={(checked) => handleSettingChange('emailNotifications', checked)}
            color="blue"
            icon="📧"
          />
          
          <AdvancedToggle
            label="Push Notifications"
            description="Receive browser notifications"
            checked={settings.pushNotifications}
            onChange={(checked) => handleSettingChange('pushNotifications', checked)}
            color="green"
            icon="📱"
          />
          
          <AdvancedToggle
            label="Prediction Alerts"
            description="Get notified about predictions"
            checked={settings.predictionAlerts}
            onChange={(checked) => handleSettingChange('predictionAlerts', checked)}
            color="purple"
            icon="🔮"
          />
        </div>
      </ProfileCard>
    </div>
  );

  const renderPrivacySettings = () => (
    <div className="space-y-6">
      <ProfileCard 
        title="Data Privacy"
        subtitle="Control your data"
        gradient="from-emerald-500 to-teal-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Profile Visibility</label>
            <select 
              value={settings.profileVisibility}
              onChange={(e) => handleSettingChange('profileVisibility', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="public">Public</option>
              <option value="team">Team Only</option>
              <option value="private">Private</option>
            </select>
          </div>
          
          <AdvancedToggle
            label="Activity Tracking"
            description="Allow activity tracking"
            checked={settings.activityTracking}
            onChange={(checked) => handleSettingChange('activityTracking', checked)}
            color="blue"
            icon="📈"
          />
          
          <AdvancedToggle
            label="Data Sharing"
            description="Share anonymized data"
            checked={settings.dataSharing}
            onChange={(checked) => handleSettingChange('dataSharing', checked)}
            color="green"
            icon="🔗"
          />
        </div>
      </ProfileCard>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <ProfileCard 
        title="Account Security"
        subtitle="Manage security settings"
        gradient="from-red-500 to-pink-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AdvancedToggle
            label="Two-Factor Authentication"
            description="Enable 2FA for security"
            checked={settings.twoFactorAuth}
            onChange={(checked) => handleSettingChange('twoFactorAuth', checked)}
            color="green"
            icon="🔐"
          />
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout</label>
            <select 
              value={settings.sessionTimeout}
              onChange={(e) => handleSettingChange('sessionTimeout', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="15min">15 minutes</option>
              <option value="30min">30 minutes</option>
              <option value="1hour">1 hour</option>
              <option value="4hours">4 hours</option>
            </select>
          </div>
        </div>
      </ProfileCard>
    </div>
  );

  const renderAdvancedSettings = () => (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <span className="text-yellow-600 text-xl mr-3">⚠️</span>
          <div>
            <h3 className="text-yellow-800 font-semibold">Advanced Settings</h3>
            <p className="text-yellow-700 text-sm">These settings are for advanced users only.</p>
          </div>
        </div>
      </div>
      
      <ProfileCard 
        title="Developer Options"
        subtitle="Advanced settings"
        gradient="from-gray-500 to-slate-600"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AdvancedToggle
            label="Debug Mode"
            description="Enable error logging"
            checked={settings.debugMode}
            onChange={(checked) => handleSettingChange('debugMode', checked)}
            color="red"
            icon="🐛"
          />
          
          <AdvancedToggle
            label="Experimental Features"
            description="Enable experimental features"
            checked={settings.experimentalFeatures}
            onChange={(checked) => handleSettingChange('experimentalFeatures', checked)}
            color="orange"
            icon="🧪"
          />
        </div>
      </ProfileCard>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general': return renderGeneralSettings();
      case 'notifications': return renderNotificationSettings();
      case 'privacy': return renderPrivacySettings();
      case 'security': return renderSecuritySettings();
      case 'advanced': return renderAdvancedSettings();
      default: return renderGeneralSettings();
    }
  };

  const filteredTabs = tabs.filter(tab => 
    !searchQuery || 
    tab.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tab.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      <DashboardNavbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Advanced Settings
              </h1>
              <p className="text-gray-600 mt-2">
                Customize your AI Rockfall Prediction experience
              </p>
            </div>
            
            <button
              onClick={handleSaveSettings}
              disabled={isLoading}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <span>💾</span>
                  <span>Save Settings</span>
                </>
              )}
            </button>
          </div>
          
          <div className="relative">
            <input
              type="text"
              placeholder="Search settings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="absolute left-3 top-3 text-gray-400 text-lg">🔍</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Categories</h3>
              <nav className="space-y-2">
                {filteredTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{tab.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium">{tab.name}</div>
                        <div className={`text-xs mt-1 ${
                          activeTab === tab.id ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {tab.description}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          <div className="lg:col-span-3">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
