import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Avatar,
  Divider,
  CircularProgress,
  Switch,
  FormControlLabel,
  Tooltip,
  Grid,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Info as InfoIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

import { chatAPI } from '../services/api';
import WebSocketService from '../services/websocket';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [includeEntities, setIncludeEntities] = useState(true);
  const [includeSentiment, setIncludeSentiment] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  
  const messagesEndRef = useRef(null);
  const wsService = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    wsService.current = new WebSocketService();
    
    wsService.current.connect(
      (data) => {
        // Handle incoming message
        const botMessage = {
          id: Date.now(),
          type: 'bot',
          content: data.message || 'Received response',
          sentiment: data.sentiment,
          entities: data.entities,
          timestamp: new Date(),
          responseTime: data.response_time,
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      },
      () => setIsConnected(true),
      () => setIsConnected(false),
      (error) => {
        console.error('WebSocket error:', error);
        setIsLoading(false);
        toast.error('Connection error occurred');
      }
    );

    // Load model info
    loadModelInfo();

    // Add welcome message
    setMessages([{
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI financial assistant powered by FinBERT. I can analyze financial sentiment, extract entities, and help you understand market sentiment. How can I help you today?',
      timestamp: new Date(),
    }]);

    return () => {
      if (wsService.current) {
        wsService.current.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadModelInfo = async () => {
    try {
      const response = await chatAPI.getModelInfo();
      setModelInfo(response.data);
    } catch (error) {
      console.error('Error loading model info:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (isConnected && wsService.current) {
        // Send via WebSocket
        wsService.current.sendMessage({
          message: inputMessage,
          include_entities: includeEntities,
          include_sentiment: includeSentiment,
        });
      } else {
        // Fallback to HTTP API
        const response = await chatAPI.sendMessage(
          inputMessage,
          includeEntities,
          includeSentiment
        );

        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: response.data.message,
          sentiment: response.data.sentiment,
          entities: response.data.entities,
          timestamp: new Date(response.data.timestamp),
          responseTime: response.data.response_time,
        };

        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
      setIsLoading(false);
    }

    setInputMessage('');
  };

  const clearChat = () => {
    setMessages([{
      id: 1,
      type: 'bot',
      content: 'Chat cleared! How can I help you today?',
      timestamp: new Date(),
    }]);
  };

  const getSentimentIcon = (sentiment) => {
    if (!sentiment) return null;
    
    switch (sentiment.label) {
      case 'positive':
        return <TrendingUp color="success" />;
      case 'negative':
        return <TrendingDown color="error" />;
      default:
        return <TrendingFlat color="warning" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    if (!sentiment) return 'default';
    
    switch (sentiment.label) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'warning';
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Card sx={{ mb: 2, p: 2 }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={2}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <BotIcon />
              </Avatar>
              <Box>
                <Typography variant="h6">FinBERT Financial Assistant</Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {isConnected ? 'Connected' : 'Disconnected'} 
                  {modelInfo && ` • Model: ${modelInfo.model_type}`}
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" alignItems="center" gap={2} justifyContent="flex-end">
              <FormControlLabel
                control={
                  <Switch
                    checked={includeSentiment}
                    onChange={(e) => setIncludeSentiment(e.target.checked)}
                    size="small"
                  />
                }
                label="Sentiment"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={includeEntities}
                    onChange={(e) => setIncludeEntities(e.target.checked)}
                    size="small"
                  />
                }
                label="Entities"
              />
              <Tooltip title="Clear Chat">
                <IconButton onClick={clearChat} size="small">
                  <ClearIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>
      </Card>

      {/* Messages */}
      <Paper 
        sx={{ 
          flex: 1, 
          p: 2, 
          overflow: 'auto',
          background: 'rgba(26, 31, 58, 0.5)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Card
                  sx={{
                    maxWidth: '70%',
                    backgroundColor: message.type === 'user' ? 'primary.main' : 'background.paper',
                    color: message.type === 'user' ? 'white' : 'text.primary',
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box display="flex" alignItems="flex-start" gap={1}>
                      <Avatar 
                        sx={{ 
                          width: 32, 
                          height: 32,
                          bgcolor: message.type === 'user' ? 'rgba(255,255,255,0.2)' : 'primary.main',
                        }}
                      >
                        {message.type === 'user' ? <PersonIcon /> : <BotIcon />}
                      </Avatar>
                      <Box flex={1}>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                          {message.content}
                        </Typography>
                        
                        {/* Sentiment Analysis */}
                        {message.sentiment && (
                          <Box sx={{ mb: 1 }}>
                            <Chip
                              icon={getSentimentIcon(message.sentiment)}
                              label={`${message.sentiment.label} (${(message.sentiment.confidence * 100).toFixed(1)}%)`}
                              color={getSentimentColor(message.sentiment)}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        )}
                        
                        {/* Entities */}
                        {message.entities && message.entities.length > 0 && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Entities:
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                              {message.entities.map((entity, index) => (
                                <Chip
                                  key={index}
                                  label={`${entity.text} (${entity.label})`}
                                  size="small"
                                  variant="outlined"
                                  color="secondary"
                                />
                              ))}
                            </Box>
                          </Box>
                        )}
                        
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="caption" color="text.secondary">
                            {format(message.timestamp, 'HH:mm:ss')}
                          </Typography>
                          {message.responseTime && (
                            <Typography variant="caption" color="text.secondary">
                              {(message.responseTime * 1000).toFixed(0)}ms
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <Box display="flex" justifyContent="flex-start" mb={2}>
            <Card sx={{ backgroundColor: 'background.paper' }}>
              <CardContent sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <BotIcon />
                </Avatar>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Analyzing...
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Paper>

      {/* Input */}
      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Ask me about financial sentiment, market analysis, or any financial topic..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              background: 'rgba(255, 255, 255, 0.05)',
            },
          }}
        />
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          onClick={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
          sx={{ 
            minWidth: 'auto',
            px: 3,
            borderRadius: 2,
          }}
        >
          Send
        </Button>
      </Box>
    </Container>
  );
};

export default ChatPage;
