import React, { useState } from "react";
import DashboardNavbar from "../Components/DashboardNavbar";

const HelpService = () => {
  const [activeSection, setActiveSection] = useState("faq");
  const [searchQuery, setSearchQuery] = useState("");
  const [ticketForm, setTicketForm] = useState({
    subject: "",
    category: "technical",
    priority: "medium",
    description: "",
    attachments: [],
  });

  const faqData = [
    {
      category: "Getting Started",
      questions: [
        {
          q: "How do I start using the AI Rockfall Prediction System?",
          a: "Begin by logging into your account, then navigate to the Sites page to add your first monitoring location. Upload geological data and configure sensors to start receiving predictions.",
        },
        {
          q: "What data formats are supported for geological information?",
          a: "We support CSV, Excel (.xlsx), GeoJSON, and KML formats. For sensor data, we accept JSON, XML, and direct API connections from major sensor manufacturers.",
        },
        {
          q: "How accurate are the AI predictions?",
          a: "Our AI models achieve 92-96% accuracy depending on data quality and site conditions. Accuracy improves over time as the system learns from your specific site patterns.",
        },
      ],
    },
    {
      category: "Technical Support",
      questions: [
        {
          q: "Why are my sensor readings not updating?",
          a: "Check your internet connection, verify sensor power supply, and ensure your API credentials are correct. If issues persist, contact technical support.",
        },
        {
          q: "How do I interpret prediction confidence levels?",
          a: "Confidence levels range from 0-100%. Values above 80% indicate high reliability, 60-80% moderate reliability, and below 60% require additional data validation.",
        },
        {
          q: "Can I export prediction reports?",
          a: "Yes, reports can be exported in PDF, Excel, and JSON formats from the Reports page. You can schedule automated reports to be sent via email.",
        },
      ],
    },
    {
      category: "Account & Billing",
      questions: [
        {
          q: "How do I upgrade my subscription plan?",
          a: "Go to Settings > Billing to view available plans and upgrade options. Changes take effect immediately, and you'll be prorated for the current billing period.",
        },
        {
          q: "What happens if I exceed my data limits?",
          a: "You'll receive notifications at 80% and 95% usage. After reaching 100%, data collection continues but may be throttled. Upgrade your plan for unlimited access.",
        },
        {
          q: "How do I add team members to my account?",
          a: "Navigate to Settings > Team Management to invite users via email. Set their permissions level (Viewer, Analyst, or Admin) based on their role requirements.",
        },
      ],
    },
  ];

  const supportChannels = [
    {
      icon: "💬",
      title: "Live Chat",
      description: "Get instant help from our support team",
      availability: "24/7",
      action: "Start Chat",
      status: "online",
    },
    {
      icon: "📞",
      title: "Phone Support",
      description: "Speak directly with our experts",
      availability: "Mon-Fri 8AM-6PM PST",
      action: "Call Now",
      phone: "+1 (555) 123-4567",
    },
    {
      icon: "📧",
      title: "Email Support",
      description: "Send us detailed questions or issues",
      availability: "Response within 4 hours",
      action: "Send Email",
      email: "support@rockfallai.com",
    },
    {
      icon: "🎥",
      title: "Video Call",
      description: "Schedule a screen-sharing session",
      availability: "By appointment",
      action: "Schedule Call",
      status: "available",
    },
  ];

  const resourceCategories = [
    {
      title: "Video Tutorials",
      icon: "🎬",
      resources: [
        "Getting Started Guide (15 min)",
        "Setting Up Sensors (8 min)",
        "Understanding Predictions (12 min)",
        "Advanced Analytics (20 min)",
      ],
    },
    {
      title: "Documentation",
      icon: "📚",
      resources: [
        "API Reference Guide",
        "User Manual PDF",
        "Sensor Configuration Guide",
        "Best Practices Handbook",
      ],
    },
    {
      title: "Community",
      icon: "👥",
      resources: [
        "User Forum",
        "Expert Webinars",
        "Case Studies",
        "Feature Requests",
      ],
    },
  ];

  const handleTicketSubmit = (e) => {
    e.preventDefault();
    // Handle ticket submission
    alert(
      "Support ticket submitted successfully! We'll respond within 4 hours."
    );
    setTicketForm({
      subject: "",
      category: "technical",
      priority: "medium",
      description: "",
      attachments: [],
    });
  };

  const renderFAQ = () => (
    <div className="space-y-8">
      {/* Search */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200">
        <div className="relative">
          <input
            type="text"
            placeholder="Search frequently asked questions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-6 py-4 pl-14 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700 placeholder-gray-400 transition-all"
          />
          <div className="absolute left-5 top-4 text-gray-400 text-xl">🔍</div>
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
        <p className="mt-4 text-sm text-gray-500 text-center">
          Can't find what you're looking for?{" "}
          <button className="text-blue-600 hover:underline font-medium">
            Contact Support
          </button>
        </p>
      </div>

      {/* FAQ Categories */}
      {faqData.map((category, categoryIndex) => (
        <div
          key={categoryIndex}
          className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl overflow-hidden border border-gray-200 hover:shadow-2xl transition-all duration-300"
        >
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-5">
            <h3 className="text-xl font-bold text-white flex items-center">
              <span className="mr-3">📋</span>
              {category.category}
            </h3>
          </div>
          <div className="p-8 space-y-6">
            {category.questions
              .filter(
                (item) =>
                  searchQuery === "" ||
                  item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
                  item.a.toLowerCase().includes(searchQuery.toLowerCase())
              )
              .map((item, index) => (
                <div
                  key={index}
                  className="border-l-4 border-blue-400 bg-blue-50/50 rounded-r-xl pl-6 pr-6 py-4 hover:bg-blue-50 transition-colors"
                >
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-start">
                    <span className="text-blue-600 mr-2 mt-1">Q:</span>
                    <span>{item.q}</span>
                  </h4>
                  <p className="text-gray-700 leading-relaxed flex items-start">
                    <span className="text-green-600 font-semibold mr-2 mt-1">
                      A:
                    </span>
                    <span>{item.a}</span>
                  </p>
                </div>
              ))}
            {category.questions.filter(
              (item) =>
                searchQuery === "" ||
                item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.a.toLowerCase().includes(searchQuery.toLowerCase())
            ).length === 0 && (
              <p className="text-gray-500 text-center py-8">
                No results found for "{searchQuery}"
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );

  const renderSupport = () => (
    <div className="space-y-10">
      {/* Support Channels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {supportChannels.map((channel, index) => (
          <div
            key={index}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-200"
          >
            <div className="flex items-start space-x-5">
              <div className="text-5xl bg-gradient-to-br from-blue-100 to-purple-100 p-4 rounded-2xl">
                {channel.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-bold text-gray-900">
                    {channel.title}
                  </h3>
                  {channel.status && (
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        channel.status === "online"
                          ? "bg-green-100 text-green-800 border border-green-300"
                          : "bg-blue-100 text-blue-800 border border-blue-300"
                      }`}
                    >
                      ● {channel.status.toUpperCase()}
                    </span>
                  )}
                </div>
                <p className="text-gray-600 mb-4 leading-relaxed">
                  {channel.description}
                </p>
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">⏰ Available:</span>{" "}
                    {channel.availability}
                  </p>
                </div>
                {channel.phone && (
                  <p className="text-base font-bold text-blue-600 mb-3 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                      />
                    </svg>
                    {channel.phone}
                  </p>
                )}
                {channel.email && (
                  <p className="text-base font-bold text-blue-600 mb-4 flex items-center">
                    <svg
                      className="w-5 h-5 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    {channel.email}
                  </p>
                )}
                <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold shadow-lg transform hover:scale-105">
                  {channel.action} →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Submit Ticket Form */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-10 border border-gray-200">
        <div className="flex items-center mb-8">
          <div className="text-4xl mr-4">🎫</div>
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              Submit a Support Ticket
            </h3>
            <p className="text-gray-600">
              Our team will respond within 4 hours
            </p>
          </div>
        </div>
        <form onSubmit={handleTicketSubmit} className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Subject *
              </label>
              <input
                type="text"
                value={ticketForm.subject}
                onChange={(e) =>
                  setTicketForm((prev) => ({
                    ...prev,
                    subject: e.target.value,
                  }))
                }
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Brief description of your issue"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Category *
              </label>
              <select
                value={ticketForm.category}
                onChange={(e) =>
                  setTicketForm((prev) => ({
                    ...prev,
                    category: e.target.value,
                  }))
                }
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              >
                <option value="technical">🔧 Technical Issue</option>
                <option value="billing">💳 Billing & Account</option>
                <option value="feature">✨ Feature Request</option>
                <option value="general">💬 General Question</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Priority Level *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { value: "low", label: "Low", color: "blue", icon: "🟢" },
                {
                  value: "medium",
                  label: "Medium",
                  color: "yellow",
                  icon: "🟡",
                },
                { value: "high", label: "High", color: "orange", icon: "🟠" },
                { value: "urgent", label: "Urgent", color: "red", icon: "🔴" },
              ].map((priority) => (
                <label
                  key={priority.value}
                  className={`flex items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    ticketForm.priority === priority.value
                      ? `border-${priority.color}-500 bg-${priority.color}-50 shadow-md`
                      : "border-gray-300 hover:border-gray-400"
                  }`}
                >
                  <input
                    type="radio"
                    name="priority"
                    value={priority.value}
                    checked={ticketForm.priority === priority.value}
                    onChange={(e) =>
                      setTicketForm((prev) => ({
                        ...prev,
                        priority: e.target.value,
                      }))
                    }
                    className="sr-only"
                  />
                  <span className="mr-2">{priority.icon}</span>
                  <span className="font-semibold">{priority.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Description *
            </label>
            <textarea
              value={ticketForm.description}
              onChange={(e) =>
                setTicketForm((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              rows="6"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
              placeholder="Please provide detailed information about your issue, including any error messages, steps to reproduce, and what you've already tried..."
              required
            ></textarea>
            <p className="mt-2 text-sm text-gray-500">
              Be as detailed as possible to help us resolve your issue quickly
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Attachments (Optional)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center hover:border-blue-400 hover:bg-blue-50/30 transition-all cursor-pointer">
              <div className="text-5xl mb-4">📎</div>
              <p className="text-base font-medium text-gray-700 mb-2">
                Drop files here or click to upload
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Support for images, PDFs, and documents (Max 10MB)
              </p>
              <input type="file" multiple className="hidden" id="file-upload" />
              <label
                htmlFor="file-upload"
                className="inline-block bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer font-medium"
              >
                Choose Files
              </label>
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-6 border-t-2 border-gray-200">
            <button
              type="button"
              onClick={() =>
                setTicketForm({
                  subject: "",
                  category: "technical",
                  priority: "medium",
                  description: "",
                  attachments: [],
                })
              }
              className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-semibold"
            >
              Clear Form
            </button>
            <button
              type="submit"
              className="px-10 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold shadow-lg transform hover:scale-105"
            >
              Submit Ticket →
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const renderResources = () => (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {resourceCategories.map((category, index) => (
          <div
            key={index}
            className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-200"
          >
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-6">
              <div className="flex items-center space-x-3">
                <span className="text-4xl bg-white/20 p-3 rounded-xl">
                  {category.icon}
                </span>
                <h3 className="text-xl font-bold text-white">
                  {category.title}
                </h3>
              </div>
            </div>
            <div className="p-6">
              <ul className="space-y-3">
                {category.resources.map((resource, resourceIndex) => (
                  <li key={resourceIndex}>
                    <button className="text-left w-full p-4 text-gray-700 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 hover:text-blue-700 rounded-xl transition-all duration-300 flex items-center justify-between group border border-transparent hover:border-blue-200">
                      <span className="font-medium">{resource}</span>
                      <svg
                        className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transform group-hover:translate-x-1 transition-all"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div className="px-6 pb-6">
              <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold shadow-lg">
                View All Resources
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Resources Section */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <span className="text-3xl mr-3">🎓</span>
          Learning Resources
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div className="text-3xl mb-3">📖</div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">
              Knowledge Base
            </h4>
            <p className="text-gray-600 mb-4">
              Comprehensive guides and articles covering all aspects of the
              system
            </p>
            <button className="text-blue-600 font-semibold hover:underline">
              Browse Articles →
            </button>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="text-3xl mb-3">🎯</div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">
              Quick Start Guide
            </h4>
            <p className="text-gray-600 mb-4">
              Get up and running in minutes with our step-by-step walkthrough
            </p>
            <button className="text-purple-600 font-semibold hover:underline">
              Start Tutorial →
            </button>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="text-3xl mb-3">💡</div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">
              Best Practices
            </h4>
            <p className="text-gray-600 mb-4">
              Learn from experts on how to optimize your prediction accuracy
            </p>
            <button className="text-green-600 font-semibold hover:underline">
              View Tips →
            </button>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
            <div className="text-3xl mb-3">🔌</div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">
              API Documentation
            </h4>
            <p className="text-gray-600 mb-4">
              Complete API reference for developers and integrations
            </p>
            <button className="text-orange-600 font-semibold hover:underline">
              View Docs →
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const sections = [
    { id: "faq", name: "FAQ", icon: "❓" },
    { id: "support", name: "Contact Support", icon: "🎧" },
    { id: "resources", name: "Resources", icon: "📖" },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case "faq":
        return renderFAQ();
      case "support":
        return renderSupport();
      case "resources":
        return renderResources();
      default:
        return renderFAQ();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      <DashboardNavbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6 shadow-xl">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Help & Support Center
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Get the help you need to make the most of your AI Rockfall
            Prediction System. We're here 24/7 to assist you.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-12">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl p-2 inline-flex border border-gray-200">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`flex items-center space-x-2 px-8 py-4 rounded-xl font-semibold transition-all duration-300 ${
                  activeSection === section.id
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <span className="text-xl">{section.icon}</span>
                <span>{section.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="mb-12">{renderContent()}</div>

        {/* Quick Stats */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-blue-100">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-2xl mb-4">
              <span className="text-3xl">⚡</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent mb-2">
              &lt; 4hrs
            </div>
            <div className="text-sm font-medium text-gray-600">
              Average Response Time
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-green-100">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-2xl mb-4">
              <span className="text-3xl">✅</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent mb-2">
              98.5%
            </div>
            <div className="text-sm font-medium text-gray-600">
              Issue Resolution Rate
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-purple-100">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-2xl mb-4">
              <span className="text-3xl">🏆</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mb-2">
              4.9/5
            </div>
            <div className="text-sm font-medium text-gray-600">
              Customer Satisfaction
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-orange-100">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-orange-100 rounded-2xl mb-4">
              <span className="text-3xl">📚</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-orange-800 bg-clip-text text-transparent mb-2">
              200+
            </div>
            <div className="text-sm font-medium text-gray-600">
              Help Articles
            </div>
          </div>
        </div>

        {/* Emergency Contact Banner */}
        <div className="mt-12 bg-gradient-to-r from-red-500 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="text-5xl">🚨</div>
              <div>
                <h3 className="text-2xl font-bold mb-1">Emergency Support</h3>
                <p className="text-red-100">
                  For critical site safety issues, contact us immediately
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="tel:+15551234567"
                className="bg-white text-red-600 px-8 py-4 rounded-xl font-bold hover:bg-red-50 transition-colors shadow-lg"
              >
                📞 Emergency Hotline
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpService;
