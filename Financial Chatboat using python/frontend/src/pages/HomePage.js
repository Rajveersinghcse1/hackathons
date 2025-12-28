import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Chip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  Analytics,
  SmartToy,
  Security,
  Speed,
  Psychology,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <SmartToy />,
      title: 'Advanced FinBERT AI',
      description: 'Powered by state-of-the-art FinBERT model for accurate financial sentiment analysis',
      color: '#2196f3',
    },
    {
      icon: <TrendingUp />,
      title: 'Real-time Analysis',
      description: 'Get instant sentiment analysis and entity extraction from financial text',
      color: '#4caf50',
    },
    {
      icon: <Psychology />,
      title: 'Fine-tuning Capability',
      description: 'Customize the model with your own data for domain-specific applications',
      color: '#ff9800',
    },
    {
      icon: <Analytics />,
      title: 'Comprehensive Analytics',
      description: 'Track performance, trends, and insights with detailed analytics dashboard',
      color: '#9c27b0',
    },
    {
      icon: <Speed />,
      title: 'High Performance',
      description: 'Optimized for speed with GPU acceleration and efficient processing',
      color: '#f44336',
    },
    {
      icon: <Security />,
      title: 'Enterprise Ready',
      description: 'Secure, scalable, and ready for production deployment',
      color: '#607d8b',
    },
  ];

  const stats = [
    { label: 'Accuracy', value: '94.5%' },
    { label: 'Response Time', value: '<200ms' },
    { label: 'Supported Languages', value: '5+' },
    { label: 'API Endpoints', value: '15+' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box textAlign="center" mb={8}>
          <Typography 
            variant="h1" 
            sx={{ 
              mb: 3,
              background: 'linear-gradient(45deg, #2196f3 30%, #ff9800 90%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 700,
            }}
          >
            FinBERT Financial Chatbot
          </Typography>
          
          <Typography 
            variant="h5" 
            color="text.secondary" 
            sx={{ mb: 4, maxWidth: 800, mx: 'auto' }}
          >
            Advanced AI-powered financial sentiment analysis and entity extraction 
            with customizable fine-tuning capabilities
          </Typography>

          <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/chat')}
              sx={{ borderRadius: 3, px: 4, py: 1.5 }}
            >
              Start Chatting
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/analytics')}
              sx={{ borderRadius: 3, px: 4, py: 1.5 }}
            >
              View Analytics
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Card sx={{ textAlign: 'center', p: 2, height: '100%' }}>
                <CardContent>
                  <Typography variant="h3" color="primary" sx={{ fontWeight: 700 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Typography variant="h2" textAlign="center" sx={{ mb: 6 }}>
          Key Features
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Card 
                  sx={{ 
                    height: '100%', 
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: `0 8px 25px ${feature.color}40`,
                    }
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Avatar
                      sx={{
                        bgcolor: feature.color,
                        mb: 2,
                        width: 60,
                        height: 60,
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    
                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                      {feature.title}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {/* Technology Stack */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <Card sx={{ mt: 8, p: 4 }}>
          <Typography variant="h4" textAlign="center" sx={{ mb: 4 }}>
            Technology Stack
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>Backend</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {['Python', 'FastAPI', 'FinBERT', 'PyTorch', 'Transformers', 'PostgreSQL'].map((tech) => (
                  <Chip key={tech} label={tech} color="primary" variant="outlined" />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="h6" sx={{ mb: 2 }}>Frontend</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {['React', 'Material-UI', 'WebSocket', 'Chart.js', 'Framer Motion'].map((tech) => (
                  <Chip key={tech} label={tech} color="secondary" variant="outlined" />
                ))}
              </Box>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 3 }} />
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>Machine Learning</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {['FinBERT', 'BERT', 'Transformers', 'Hugging Face'].map((tech) => (
                  <Chip key={tech} label={tech} color="success" variant="outlined" />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>Deployment</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {['Docker', 'Kubernetes', 'Redis', 'Nginx'].map((tech) => (
                  <Chip key={tech} label={tech} color="warning" variant="outlined" />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>Monitoring</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {['Prometheus', 'Grafana', 'ELK Stack'].map((tech) => (
                  <Chip key={tech} label={tech} color="error" variant="outlined" />
                ))}
              </Box>
            </Grid>
          </Grid>
        </Card>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
      >
        <Box textAlign="center" sx={{ mt: 8, p: 6, borderRadius: 4, background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%)' }}>
          <Typography variant="h4" sx={{ mb: 2 }}>
            Ready to Get Started?
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Experience the power of AI-driven financial analysis. Start chatting with our FinBERT model 
            or explore the analytics dashboard to see real-time insights.
          </Typography>
          
          <Box display="flex" gap={2} justifyContent="center" flexWrap="wrap">
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/chat')}
              sx={{ borderRadius: 3, px: 4, py: 1.5 }}
            >
              Try the Chatbot
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/finetune')}
              sx={{ borderRadius: 3, px: 4, py: 1.5 }}
            >
              Fine-tune Model
            </Button>
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default HomePage;
