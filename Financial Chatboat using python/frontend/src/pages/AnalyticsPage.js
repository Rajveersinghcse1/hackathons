import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Paper,
  CircularProgress,
  Chip,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Assessment,
  Speed,
  People,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  AreaChart,
  Area,
} from 'recharts';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import { analyticsAPI } from '../services/api';

const COLORS = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0'];

const AnalyticsPage = () => {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [sentimentTrends, setSentimentTrends] = useState([]);
  const [popularTopics, setPopularTopics] = useState([]);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [usageStats, setUsageStats] = useState(null);
  const [timePeriod, setTimePeriod] = useState('7d');

  useEffect(() => {
    loadAnalyticsData();
  }, [timePeriod]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      const [
        overviewResponse,
        trendsResponse,
        topicsResponse,
        performanceResponse,
        usageResponse,
      ] = await Promise.all([
        analyticsAPI.getOverview(),
        analyticsAPI.getSentimentTrends(parseInt(timePeriod.replace('d', ''))),
        analyticsAPI.getPopularTopics(10),
        analyticsAPI.getModelPerformance(),
        analyticsAPI.getUsageStats(timePeriod),
      ]);

      setOverview(overviewResponse.data);
      setSentimentTrends(trendsResponse.data.trends);
      setPopularTopics(topicsResponse.data.topics);
      setModelPerformance(performanceResponse.data);
      setUsageStats(usageResponse.data);
      
    } catch (error) {
      console.error('Error loading analytics data:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format) => {
    try {
      const response = await analyticsAPI.exportData(format);
      
      if (format === 'csv') {
        const blob = new Blob([response.data.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
      } else {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { 
          type: 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
      }
      
      toast.success(`Data exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Failed to export data');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading Analytics Data...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            Analytics Dashboard
          </Typography>
          
          <Box display="flex" gap={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Time Period</InputLabel>
              <Select
                value={timePeriod}
                label="Time Period"
                onChange={(e) => setTimePeriod(e.target.value)}
              >
                <MenuItem value="1d">1 Day</MenuItem>
                <MenuItem value="7d">7 Days</MenuItem>
                <MenuItem value="30d">30 Days</MenuItem>
                <MenuItem value="90d">90 Days</MenuItem>
              </Select>
            </FormControl>
            
            <Button
              variant="outlined"
              onClick={() => exportData('json')}
              size="small"
            >
              Export JSON
            </Button>
            
            <Button
              variant="outlined"
              onClick={() => exportData('csv')}
              size="small"
            >
              Export CSV
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Overview Cards */}
      {overview && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <People color="primary" />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 600 }}>
                        {overview.total_chat_sessions}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Chats
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Speed color="success" />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 600 }}>
                        {overview.average_response_time}s
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Response Time
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Assessment color="warning" />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 600 }}>
                        {overview.active_models}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Models
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <TrendingUp color="error" />
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 600 }}>
                        {overview.fine_tuned_models}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Fine-tuned Models
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>
      )}

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* Sentiment Trends */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Sentiment Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={sentimentTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="positive" 
                      stackId="1" 
                      stroke="#4caf50" 
                      fill="#4caf50" 
                      fillOpacity={0.6}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="neutral" 
                      stackId="1" 
                      stroke="#ff9800" 
                      fill="#ff9800" 
                      fillOpacity={0.6}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="negative" 
                      stackId="1" 
                      stroke="#f44336" 
                      fill="#f44336" 
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Sentiment Distribution
                </Typography>
                {overview && (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Positive', value: overview.sentiment_distribution.positive },
                          { name: 'Neutral', value: overview.sentiment_distribution.neutral },
                          { name: 'Negative', value: overview.sentiment_distribution.negative },
                        ]}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label
                      >
                        {[
                          { name: 'Positive', value: overview.sentiment_distribution.positive },
                          { name: 'Neutral', value: overview.sentiment_distribution.neutral },
                          { name: 'Negative', value: overview.sentiment_distribution.negative },
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Popular Topics */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Popular Topics
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={popularTopics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="topic" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="mentions" fill="#2196f3" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Model Performance */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Model Performance
                </Typography>
                {modelPerformance && (
                  <Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Overall Accuracy
                      </Typography>
                      <Typography variant="h4" color="primary">
                        {(modelPerformance.accuracy * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Positive F1
                        </Typography>
                        <Chip 
                          label={modelPerformance.f1_score.positive.toFixed(3)}
                          color="success"
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Neutral F1
                        </Typography>
                        <Chip 
                          label={modelPerformance.f1_score.neutral.toFixed(3)}
                          color="warning"
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">
                          Negative F1
                        </Typography>
                        <Chip 
                          label={modelPerformance.f1_score.negative.toFixed(3)}
                          color="error"
                          size="small"
                        />
                      </Grid>
                    </Grid>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Total Predictions: {modelPerformance.total_predictions.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Average Confidence: {(modelPerformance.average_confidence * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Usage Statistics */}
        {usageStats && (
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Usage Statistics ({usageStats.period})
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {usageStats.total_requests.toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Requests
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {usageStats.unique_users.toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Unique Users
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {(usageStats.error_rate * 100).toFixed(2)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Error Rate
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" color="info.main">
                          {usageStats.uptime}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Uptime
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default AnalyticsPage;
