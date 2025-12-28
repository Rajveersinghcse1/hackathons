import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send chat message
  sendMessage: (message, includeEntities = true, includeSentiment = true) =>
    api.post('/chat', {
      message,
      include_entities: includeEntities,
      include_sentiment: includeSentiment,
    }),

  // Get chat history
  getChatHistory: (conversationId, limit = 50) =>
    api.get('/chat/history', {
      params: { conversation_id: conversationId, limit },
    }),

  // Batch analyze messages
  batchAnalyze: (messages) =>
    api.post('/chat/batch', messages),

  // Get model info
  getModelInfo: () => api.get('/model/info'),
};

export const fineTuneAPI = {
  // Start fine-tuning
  startFineTuning: (data) => api.post('/finetune/start', data),

  // Get training status
  getTrainingStatus: (taskId) => api.get(`/finetune/status/${taskId}`),

  // List training tasks
  listTrainingTasks: (status, limit = 50) =>
    api.get('/finetune/tasks', {
      params: { status, limit },
    }),

  // Cancel training task
  cancelTrainingTask: (taskId) => api.delete(`/finetune/task/${taskId}`),

  // Load fine-tuned model
  loadFineTunedModel: (modelPath) =>
    api.post('/finetune/load-model', { model_path: modelPath }),

  // List fine-tuned models
  listFineTunedModels: () => api.get('/finetune/models'),
};

export const analyticsAPI = {
  // Get analytics overview
  getOverview: () => api.get('/analytics/overview'),

  // Get sentiment trends
  getSentimentTrends: (days = 7) =>
    api.get('/analytics/sentiment-trends', {
      params: { days },
    }),

  // Get popular topics
  getPopularTopics: (limit = 10) =>
    api.get('/analytics/popular-topics', {
      params: { limit },
    }),

  // Get model performance
  getModelPerformance: () => api.get('/analytics/model-performance'),

  // Get usage statistics
  getUsageStats: (period = '7d') =>
    api.get('/analytics/usage-stats', {
      params: { period },
    }),

  // Record chat session
  recordChatSession: (sessionData) =>
    api.post('/analytics/record-session', sessionData),

  // Export analytics data
  exportData: (format = 'json', startDate, endDate) =>
    api.get('/analytics/export', {
      params: { format, start_date: startDate, end_date: endDate },
    }),
};

export const healthAPI = {
  // Health check
  healthCheck: () => api.get('/health', { baseURL: 'http://localhost:8000' }),

  // Root endpoint
  root: () => api.get('/', { baseURL: 'http://localhost:8000' }),
};

export default api;
