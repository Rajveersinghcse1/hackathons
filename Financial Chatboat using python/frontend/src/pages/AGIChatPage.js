import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Container, Paper, TextField, Button, Typography, IconButton,
  List, ListItem, Avatar, Chip, LinearProgress, Dialog, DialogTitle,
  DialogContent, DialogActions, FormControlLabel, Switch, Card,
  CardContent, Grid, Accordion, AccordionSummary, AccordionDetails,
  Tooltip, Alert, Snackbar
} from '@mui/material';
import {
  Send as SendIcon,
  Psychology as BrainIcon,
  Memory as MemoryIcon,
  School as LearnIcon,
  Analytics as AnalyticsIcon,
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Search as SearchIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

const AGIChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useMemory, setUseMemory] = useState(true);
  const [sessionId, setSessionId] = useState('default');
  const [showSettings, setShowSettings] = useState(false);
  const [showKnowledgeDialog, setShowKnowledgeDialog] = useState(false);
  const [showMemorySearch, setShowMemorySearch] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [memoryStats, setMemoryStats] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // Knowledge management
  const [knowledgeText, setKnowledgeText] = useState('');
  const [knowledgeCategory, setKnowledgeCategory] = useState('general');
  const [knowledgeImportance, setKnowledgeImportance] = useState(1.0);
  
  // Memory search
  const [memoryQuery, setMemoryQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    loadModelInfo();
    loadMemoryStats();
    // Add welcome message
    setMessages([{
      id: 1,
      text: "Hello! I'm your Advanced AGI Assistant. I have enhanced capabilities including memory, learning, and reasoning. How can I help you today?",
      sender: 'agi',
      timestamp: new Date().toISOString(),
      metadata: {
        strategy: 'greeting',
        confidence: 0.95,
        features: ['Memory Bank', 'Continuous Learning', 'Multi-Model AI']
      }
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadModelInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/model/info');
      if (response.ok) {
        const data = await response.json();
        setModelInfo(data);
      }
    } catch (error) {
      console.error('Error loading model info:', error);
    }
  };

  const loadMemoryStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/memory/stats');
      if (response.ok) {
        const data = await response.json();
        setMemoryStats(data);
      }
    } catch (error) {
      console.error('Error loading memory stats:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          context: '',
          use_memory: useMemory,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const agiMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: 'agi',
          timestamp: data.timestamp,
          metadata: {
            sentiment: data.sentiment,
            strategy: data.strategy,
            confidence: data.confidence,
            processing_time: data.processing_time,
            relevant_memories: data.relevant_memories,
            ...data.metadata
          }
        };

        setMessages(prev => [...prev, agiMessage]);
        
        // Update memory stats after conversation
        loadMemoryStats();
        
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your message. Please try again.',
        sender: 'agi',
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const addKnowledge = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/knowledge/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          knowledge_text: knowledgeText,
          category: knowledgeCategory,
          importance: knowledgeImportance
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSnackbar({
          open: true,
          message: 'Knowledge added successfully!',
          severity: 'success'
        });
        setShowKnowledgeDialog(false);
        setKnowledgeText('');
        loadMemoryStats();
      } else {
        throw new Error('Failed to add knowledge');
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error adding knowledge',
        severity: 'error'
      });
    }
  };

  const searchMemory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/memory/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: memoryQuery,
          top_k: 5
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.memories);
      }
    } catch (error) {
      console.error('Error searching memory:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getSentimentColor = (sentiment) => {
    if (!sentiment) return 'default';
    switch (sentiment.label?.toLowerCase()) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      default: return 'info';
    }
  };

  const getStrategyIcon = (strategy) => {
    switch (strategy) {
      case 'question_answering': return <SearchIcon />;
      case 'analysis': return <AnalyticsIcon />;
      case 'conversation': return <BrainIcon />;
      default: return <BrainIcon />;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <Paper elevation={3} sx={{ p: 2, mb: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <BrainIcon sx={{ fontSize: 40, color: 'white' }} />
              <Box>
                <Typography variant="h4" sx={{ color: 'white', fontWeight: 'bold' }}>
                  Advanced AGI Chat
                </Typography>
                <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  Intelligent • Learning • Reasoning
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Add Knowledge">
                <IconButton 
                  onClick={() => setShowKnowledgeDialog(true)}
                  sx={{ color: 'white' }}
                >
                  <AddIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Search Memory">
                <IconButton 
                  onClick={() => setShowMemorySearch(true)}
                  sx={{ color: 'white' }}
                >
                  <MemoryIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton 
                  onClick={() => setShowSettings(true)}
                  sx={{ color: 'white' }}
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        {/* Status Cards */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <BrainIcon color="primary" />
                <Typography variant="body2">
                  Models: {modelInfo?.models_loaded?.length || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <MemoryIcon color="secondary" />
                <Typography variant="body2">
                  Memories: {memoryStats?.total_memories || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <LearnIcon color="success" />
                <Typography variant="body2">
                  Learning: {useMemory ? 'Active' : 'Disabled'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1 }}>
                <AnalyticsIcon color="warning" />
                <Typography variant="body2">
                  Session: {sessionId}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Chat Area */}
        <Paper 
          elevation={2} 
          sx={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          <Box 
            ref={chatContainerRef}
            sx={{ 
              flex: 1, 
              overflow: 'auto', 
              p: 2,
              background: 'linear-gradient(to bottom, #f8f9fa, #e9ecef)'
            }}
          >
            <List sx={{ py: 0 }}>
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ListItem 
                      sx={{ 
                        flexDirection: 'column',
                        alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                        mb: 2
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 1,
                          maxWidth: '80%',
                          flexDirection: message.sender === 'user' ? 'row-reverse' : 'row'
                        }}
                      >
                        <Avatar
                          sx={{
                            bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                            mt: 1
                          }}
                        >
                          {message.sender === 'user' ? 'U' : 'A'}
                        </Avatar>
                        
                        <Paper
                          elevation={1}
                          sx={{
                            p: 2,
                            bgcolor: message.sender === 'user' 
                              ? 'primary.main' 
                              : message.error 
                                ? 'error.light' 
                                : 'background.paper',
                            color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                            borderRadius: 2,
                            position: 'relative'
                          }}
                        >
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {message.text}
                          </Typography>
                          
                          {/* AGI Message Metadata */}
                          {message.sender === 'agi' && message.metadata && (
                            <Box sx={{ mt: 2 }}>
                              <Accordion>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                  <Typography variant="caption">
                                    AGI Analysis
                                  </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                                    {message.metadata.sentiment && (
                                      <Chip
                                        size="small"
                                        label={`${message.metadata.sentiment.label} (${(message.metadata.sentiment.confidence * 100).toFixed(1)}%)`}
                                        color={getSentimentColor(message.metadata.sentiment)}
                                      />
                                    )}
                                    <Chip
                                      size="small"
                                      icon={getStrategyIcon(message.metadata.strategy)}
                                      label={message.metadata.strategy}
                                      variant="outlined"
                                    />
                                    <Chip
                                      size="small"
                                      label={`Confidence: ${(message.metadata.confidence * 100).toFixed(1)}%`}
                                      color="info"
                                      variant="outlined"
                                    />
                                    {message.metadata.relevant_memories > 0 && (
                                      <Chip
                                        size="small"
                                        icon={<MemoryIcon />}
                                        label={`${message.metadata.relevant_memories} memories`}
                                        color="secondary"
                                        variant="outlined"
                                      />
                                    )}
                                  </Box>
                                  <Typography variant="caption" color="text.secondary">
                                    Processing time: {(message.metadata.processing_time * 1000).toFixed(1)}ms
                                  </Typography>
                                </AccordionDetails>
                              </Accordion>
                            </Box>
                          )}
                          
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              display: 'block',
                              mt: 1,
                              opacity: 0.7,
                              textAlign: message.sender === 'user' ? 'right' : 'left'
                            }}
                          >
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Paper>
                      </Box>
                    </ListItem>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <ListItem>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar sx={{ bgcolor: 'secondary.main' }}>A</Avatar>
                    <Paper elevation={1} sx={{ p: 2, minWidth: 100 }}>
                      <Typography variant="body2" color="text.secondary">
                        AGI is thinking...
                      </Typography>
                      <LinearProgress sx={{ mt: 1 }} />
                    </Paper>
                  </Box>
                </ListItem>
              )}
            </List>
            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                placeholder="Ask anything... I can learn, reason, and remember!"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                sx={{ 
                  minWidth: 60,
                  height: 56,
                  borderRadius: 3,
                  background: 'linear-gradient(45deg, #667eea, #764ba2)'
                }}
              >
                <SendIcon />
              </Button>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={useMemory}
                    onChange={(e) => setUseMemory(e.target.checked)}
                    size="small"
                  />
                }
                label="Use Memory"
              />
              <Typography variant="caption" color="text.secondary">
                Advanced AGI • Memory Enabled • Learning Active
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Knowledge Dialog */}
        <Dialog open={showKnowledgeDialog} onClose={() => setShowKnowledgeDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Knowledge to AGI</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Knowledge Text"
              value={knowledgeText}
              onChange={(e) => setKnowledgeText(e.target.value)}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Category"
              value={knowledgeCategory}
              onChange={(e) => setKnowledgeCategory(e.target.value)}
              margin="normal"
            />
            <TextField
              fullWidth
              type="number"
              label="Importance (0-10)"
              value={knowledgeImportance}
              onChange={(e) => setKnowledgeImportance(parseFloat(e.target.value))}
              inputProps={{ min: 0, max: 10, step: 0.1 }}
              margin="normal"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowKnowledgeDialog(false)}>Cancel</Button>
            <Button onClick={addKnowledge} variant="contained">Add Knowledge</Button>
          </DialogActions>
        </Dialog>

        {/* Memory Search Dialog */}
        <Dialog open={showMemorySearch} onClose={() => setShowMemorySearch(false)} maxWidth="md" fullWidth>
          <DialogTitle>Search Memory Bank</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                label="Search Query"
                value={memoryQuery}
                onChange={(e) => setMemoryQuery(e.target.value)}
              />
              <Button variant="contained" onClick={searchMemory}>
                <SearchIcon />
              </Button>
            </Box>
            
            {searchResults.length > 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>Search Results:</Typography>
                {searchResults.map((result, index) => (
                  <Card key={index} sx={{ mb: 1 }}>
                    <CardContent>
                      <Typography variant="body2">{result.text}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Category: {result.category} | Similarity: {(result.similarity * 100).toFixed(1)}%
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowMemorySearch(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Settings Dialog */}
        <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
          <DialogTitle>AGI Settings</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Session ID"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              margin="normal"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={useMemory}
                  onChange={(e) => setUseMemory(e.target.checked)}
                />
              }
              label="Enable Memory Bank"
            />
            
            {modelInfo && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Model Information:</Typography>
                <Typography variant="body2">Device: {modelInfo.device}</Typography>
                <Typography variant="body2">Models: {modelInfo.models_loaded?.join(', ')}</Typography>
                <Typography variant="body2">Pipelines: {modelInfo.pipelines_loaded?.join(', ')}</Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowSettings(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};

export default AGIChatPage;
