import React, { useState, useEffect } from "react";
import DashboardNavbar from "../Components/DashboardNavbar";
import ProfileCard from "../Components/Profile/ProfileCard";
import AvatarUpload from "../Components/Profile/AvatarUpload";
import ActivityTimeline from "../Components/Profile/ActivityTimeline";
import StatCard from "../Components/Profile/StatCard";
import {
  AdvancedInput,
  AdvancedSelect,
} from "../Components/Profile/AdvancedInput";
import AdvancedToggle from "../Components/Profile/AdvancedToggle";

const UserProfile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [isLoading, setIsLoading] = useState(false);
  const [avatar, setAvatar] = useState(null);

  const [profile, setProfile] = useState({
    firstName: "Rajveer",
    lastName: "Singh",
    email: "RockfallPrediction@gmail.com",
    role: "Mine Engineer",
    company: "GeoTech Mining Solutions",
    phone: "+1 (555) 123-4567",
    location: "Vancouver, Canada",
    bio: "Experienced mining engineer specializing in rockfall prediction and geological risk assessment. Over 10 years of experience in mine safety and AI-powered prediction systems.",
    department: "Safety & Engineering",
    employeeId: "ENG-2024-001",
    joinDate: "2024-01-15",
    dateOfBirth: "1985-06-15",
    nationality: "Canadian",
    languages: ["English", "French"],
    education: "Mining Engineering, University of British Columbia",
    certifications: [
      "Professional Engineer (P.Eng)",
      "Mine Safety Certification",
    ],
    emergencyContact: "Sarah Singh - +1 (555) 987-6543",
    timezone: "PST",
    workHours: "08:00-17:00",
  });

  // Load profile from localStorage on mount
  useEffect(() => {
    const savedProfile = localStorage.getItem("userProfile");
    if (savedProfile) {
      try {
        const parsedProfile = JSON.parse(savedProfile);
        setProfile(parsedProfile);
        if (parsedProfile.avatar) {
          setAvatar(parsedProfile.avatar);
        }
      } catch (error) {
        console.error("Error loading profile:", error);
      }
    } else {
      // Save initial profile to localStorage
      const initialProfile = {
        ...profile,
        avatar: null,
      };
      localStorage.setItem("userProfile", JSON.stringify(initialProfile));
    }
  }, []);

  const handleSave = async () => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Save profile to localStorage
    const updatedProfile = {
      ...profile,
      avatar: avatar,
    };
    localStorage.setItem("userProfile", JSON.stringify(updatedProfile));

    // Dispatch custom event to notify other components
    window.dispatchEvent(new Event("profileUpdated"));

    setIsEditing(false);
    setIsLoading(false);
    console.log("Profile saved:", updatedProfile);
  };

  const handleInputChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const stats = [
    {
      title: "Sites Monitored",
      value: "24",
      icon: "",
      color: "blue",
      trend: "+3",
      trendDirection: "up",
    },
    {
      title: "Predictions Made",
      value: "1,247",
      icon: "",
      color: "purple",
      trend: "+127",
      trendDirection: "up",
    },
    {
      title: "Reports Generated",
      value: "86",
      icon: "",
      color: "green",
      trend: "+12",
      trendDirection: "up",
    },
    {
      title: "Accuracy Rate",
      value: "94.2%",
      icon: "",
      color: "orange",
      trend: "+2.1%",
      trendDirection: "up",
    },
    {
      title: "Years Experience",
      value: "10+",
      icon: "",
      color: "indigo",
      trend: "Stable",
      trendDirection: "stable",
    },
    {
      title: "Team Members",
      value: "12",
      icon: "",
      color: "red",
      trend: "+2",
      trendDirection: "up",
    },
  ];

  const recentActivity = [
    {
      action: "Generated comprehensive safety report for Site Alpha-7",
      time: "2 hours ago",
      type: "report",
      priority: "high",
      tags: ["Safety", "Report", "Alpha-7"],
      details:
        "Comprehensive analysis of geological conditions and risk factors.",
      status: "completed",
    },
    {
      action: "Updated AI prediction model for Beta-3 sector",
      time: "1 day ago",
      type: "prediction",
      priority: "medium",
      tags: ["AI", "Model", "Beta-3"],
      details: "Enhanced prediction accuracy with new geological data inputs.",
      status: "completed",
    },
    {
      action: "Completed safety inspection at Gamma-1",
      time: "3 days ago",
      type: "inspection",
      priority: "high",
      tags: ["Inspection", "Safety", "Gamma-1"],
      details: "Routine safety inspection with focus on structural integrity.",
      status: "completed",
    },
    {
      action: "Published monthly analytics dashboard",
      time: "1 week ago",
      type: "analytics",
      priority: "low",
      tags: ["Analytics", "Dashboard", "Monthly"],
      details: "Summary of site performance metrics and trends.",
      status: "completed",
    },
    {
      action: "Led team training on new prediction algorithms",
      time: "2 weeks ago",
      type: "training",
      priority: "medium",
      tags: ["Training", "Team", "Algorithms"],
      details: "Knowledge transfer session on latest AI prediction methods.",
      status: "completed",
    },
  ];

  const tabs = [
    {
      id: "overview",
      name: "Overview",
      icon: "",
      description: "Profile summary and statistics",
    },
    {
      id: "personal",
      name: "Personal Info",
      icon: "",
      description: "Personal details and contact",
    },
    {
      id: "professional",
      name: "Professional",
      icon: "",
      description: "Work and career information",
    },
    {
      id: "activity",
      name: "Activity",
      icon: "",
      description: "Recent activity timeline",
    },
    {
      id: "security",
      name: "Security",
      icon: "",
      description: "Account security settings",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      <DashboardNavbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                User Profile
              </h1>
              <p className="text-gray-600 mt-2">
                Manage your personal and professional information
              </p>
            </div>

            <div className="flex space-x-3">
              {isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isLoading}
                    className="px-8 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-200 disabled:opacity-50 flex items-center space-x-2 font-medium shadow-lg"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
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
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        <span>Save Changes</span>
                      </>
                    )}
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-8 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2 font-medium shadow-lg"
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
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  <span>Edit Profile</span>
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-8">
              <div className="text-center mb-6">
                <AvatarUpload
                  currentAvatar={avatar}
                  onAvatarChange={setAvatar}
                  size="lg"
                  userName={profile.firstName + " " + profile.lastName}
                  allowEdit={isEditing}
                />
                <h3 className="text-xl font-bold text-gray-900 mt-4">
                  {profile.firstName} {profile.lastName}
                </h3>
                <p className="text-gray-600">{profile.role}</p>
                <p className="text-sm text-gray-500">{profile.company}</p>
              </div>

              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 ${
                      activeTab === tab.id
                        ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{tab.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium">{tab.name}</div>
                        <div
                          className={`text-xs mt-1 ${
                            activeTab === tab.id
                              ? "text-blue-100"
                              : "text-gray-500"
                          }`}
                        >
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
            {activeTab === "overview" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {stats.map((stat, index) => (
                    <StatCard key={index} {...stat} />
                  ))}
                </div>

                <ProfileCard
                  title="Quick Info"
                  subtitle="Essential profile information"
                  gradient="from-blue-500 to-purple-600"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">
                        Contact
                      </h4>
                      <p className="text-gray-600">{profile.email}</p>
                      <p className="text-gray-600">{profile.phone}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">
                        Location
                      </h4>
                      <p className="text-gray-600">{profile.location}</p>
                      <p className="text-gray-600">{profile.department}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <h4 className="font-semibold text-gray-700 mb-2">Bio</h4>
                    <p className="text-gray-600 leading-relaxed">
                      {profile.bio}
                    </p>
                  </div>
                </ProfileCard>
              </div>
            )}

            {activeTab === "personal" && (
              <div className="space-y-6">
                <ProfileCard
                  title="Personal Information"
                  subtitle="Basic personal details"
                  gradient="from-green-500 to-emerald-600"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <AdvancedInput
                      label="First Name"
                      value={profile.firstName}
                      onChange={(value) =>
                        handleInputChange("firstName", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Last Name"
                      value={profile.lastName}
                      onChange={(value) => handleInputChange("lastName", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Email"
                      type="email"
                      value={profile.email}
                      onChange={(value) => handleInputChange("email", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Phone"
                      type="tel"
                      value={profile.phone}
                      onChange={(value) => handleInputChange("phone", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Date of Birth"
                      type="date"
                      value={profile.dateOfBirth}
                      onChange={(value) =>
                        handleInputChange("dateOfBirth", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Nationality"
                      value={profile.nationality}
                      onChange={(value) =>
                        handleInputChange("nationality", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Biography
                    </label>
                    <textarea
                      value={profile.bio}
                      onChange={(e) => handleInputChange("bio", e.target.value)}
                      disabled={!isEditing}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="Tell us about yourself..."
                    />
                  </div>
                </ProfileCard>
              </div>
            )}

            {activeTab === "professional" && (
              <div className="space-y-6">
                <ProfileCard
                  title="Professional Information"
                  subtitle="Work and career details"
                  gradient="from-purple-500 to-pink-600"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <AdvancedInput
                      label="Job Title"
                      value={profile.role}
                      onChange={(value) => handleInputChange("role", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Company"
                      value={profile.company}
                      onChange={(value) => handleInputChange("company", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Department"
                      value={profile.department}
                      onChange={(value) =>
                        handleInputChange("department", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Employee ID"
                      value={profile.employeeId}
                      onChange={(value) =>
                        handleInputChange("employeeId", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Join Date"
                      type="date"
                      value={profile.joinDate}
                      onChange={(value) => handleInputChange("joinDate", value)}
                      disabled={!isEditing}
                      icon=""
                    />

                    <AdvancedInput
                      label="Work Hours"
                      value={profile.workHours}
                      onChange={(value) =>
                        handleInputChange("workHours", value)
                      }
                      disabled={!isEditing}
                      icon=""
                    />
                  </div>

                  <div className="mt-6 grid grid-cols-1 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Education
                      </label>
                      <textarea
                        value={profile.education}
                        onChange={(e) =>
                          handleInputChange("education", e.target.value)
                        }
                        disabled={!isEditing}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Certifications
                      </label>
                      <textarea
                        value={profile.certifications.join(", ")}
                        onChange={(e) =>
                          handleInputChange(
                            "certifications",
                            e.target.value.split(", ")
                          )
                        }
                        disabled={!isEditing}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
                      />
                    </div>
                  </div>
                </ProfileCard>
              </div>
            )}

            {activeTab === "activity" && (
              <div className="space-y-6">
                <ProfileCard
                  title="Recent Activity"
                  subtitle="Your latest actions and achievements"
                  gradient="from-orange-500 to-red-600"
                >
                  <ActivityTimeline
                    activities={recentActivity}
                    showPagination={true}
                  />
                </ProfileCard>
              </div>
            )}

            {activeTab === "security" && (
              <div className="space-y-6">
                <ProfileCard
                  title="Security Settings"
                  subtitle="Manage your account security"
                  gradient="from-red-500 to-pink-600"
                >
                  <div className="space-y-6">
                    <AdvancedToggle
                      label="Two-Factor Authentication"
                      description="Add an extra layer of security to your account"
                      checked={false}
                      onChange={() => {}}
                      color="green"
                      icon=""
                    />

                    <AdvancedToggle
                      label="Login Notifications"
                      description="Get notified when someone logs into your account"
                      checked={true}
                      onChange={() => {}}
                      color="blue"
                      icon=""
                    />

                    <AdvancedToggle
                      label="Activity Logging"
                      description="Keep a log of your account activity"
                      checked={true}
                      onChange={() => {}}
                      color="purple"
                      icon=""
                    />

                    <div className="pt-6 border-t border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">
                        Emergency Contact
                      </h4>
                      <AdvancedInput
                        label="Emergency Contact"
                        value={profile.emergencyContact}
                        onChange={(value) =>
                          handleInputChange("emergencyContact", value)
                        }
                        disabled={!isEditing}
                        icon=""
                        placeholder="Name - Phone number"
                      />
                    </div>
                  </div>
                </ProfileCard>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
