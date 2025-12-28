import React, { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Box, Button, TextField, Card,
  CardContent, Grid, LinearProgress, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, FormControl, InputLabel, Select,
  MenuItem, Alert, Snackbar, Accordion, AccordionSummary,
  AccordionDetails, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, CircularProgress
} from '@mui/material';
import {
  School as TrainIcon,
  Psychology as AIIcon,
  Upload as UploadIcon,
  PlayArrow as StartIcon,
  CheckCircle as CompleteIcon,
  CheckCircle,
  ExpandMore as ExpandMoreIcon,
  CloudUpload as CloudUploadIcon,
  DataUsage as DataIcon,
  TrendingUp as ProgressIcon,
  Memory as MemoryIcon
} from '@mui/icons-material';

const AdvancedTrainingPage = () => {
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [showTrainingDialog, setShowTrainingDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // Training configuration
  const [sessionName, setSessionName] = useState('');
  const [modelName, setModelName] = useState('classification');
  const [learningRate, setLearningRate] = useState(2e-5);
  const [numEpochs, setNumEpochs] = useState(3);
  const [batchSize, setBatchSize] = useState(8);
  const [maxLength, setMaxLength] = useState(512);
  
  // Training data
  const [trainingData, setTrainingData] = useState([]);
  const [customData, setCustomData] = useState('');
  
  // Sample training data
  const [sampleDatasets] = useState([
    {
      name: 'Financial Sentiment',
      description: 'Financial news and sentiment labels',
      size: 1000,
      category: 'sentiment'
    },
    {
      name: 'General Knowledge',
      description: 'Q&A pairs for general knowledge',
      size: 500,
      category: 'qa'
    },
    {
      name: 'Conversation Data',
      description: 'Dialog pairs for conversation training',
      size: 750,
      category: 'conversation'
    }
  ]);

  useEffect(() => {
    loadTrainingStatus();
    loadModelInfo();
    
    // Poll training status every 5 seconds if training
    const interval = setInterval(() => {
      if (isTraining) {
        loadTrainingStatus();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [isTraining]);

  const loadTrainingStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/training/status');
      if (response.ok) {
        const data = await response.json();
        setTrainingStatus(data);
        setIsTraining(data.is_training);
      }
    } catch (error) {
      console.error('Error loading training status:', error);
    }
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

  const startTraining = async () => {
    if (!sessionName || trainingData.length === 0) {
      setSnackbar({
        open: true,
        message: 'Please provide session name and training data',
        severity: 'error'
      });
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/training/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_name: sessionName,
          model_name: modelName,
          training_data: trainingData,
          learning_rate: learningRate,
          num_epochs: numEpochs,
          batch_size: batchSize,
          max_length: maxLength
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSnackbar({
          open: true,
          message: data.message,
          severity: 'success'
        });
        setShowTrainingDialog(false);
        setIsTraining(true);
        loadTrainingStatus();
      } else {
        throw new Error('Failed to start training');
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error starting training: ' + error.message,
        severity: 'error'
      });
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/v1/training/upload-data', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setSnackbar({
          open: true,
          message: data.message,
          severity: 'success'
        });
        // You would process the uploaded data here
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error uploading file',
        severity: 'error'
      });
    }
  };

  const addCustomData = () => {
    if (!customData.trim()) return;
    
    const lines = customData.split('\n').filter(line => line.trim());
    const newData = lines.map((line, index) => ({
      id: Date.now() + index,
      text: line.trim(),
      label: 0 // Default label
    }));
    
    setTrainingData([...trainingData, ...newData]);
    setCustomData('');
    setShowUploadDialog(false);
  };

  const loadSampleDataset = (dataset) => {
    // Generate sample data based on dataset type
    const sampleData = [];
    for (let i = 0; i < Math.min(dataset.size, 100); i++) {
      switch (dataset.category) {
        case 'sentiment':
          sampleData.push({
            id: i,
            text: `Sample financial text ${i + 1}: The market is showing positive trends.`,
            label: Math.random() > 0.5 ? 1 : 0
          });
          break;
        case 'qa':
          sampleData.push({
            id: i,
            text: `Question ${i + 1}: What is artificial intelligence?`,
            label: 0
          });
          break;
        case 'conversation':
          sampleData.push({
            id: i,
            text: `User: Hello! AI: Hello! How can I help you today?`,
            label: 0
          });
          break;
        default:
          sampleData.push({
            id: i,
            text: `Sample text ${i + 1}`,
            label: 0
          });
      }
    }
    
    setTrainingData(sampleData);
    setSnackbar({
      open: true,
      message: `Loaded ${sampleData.length} examples from ${dataset.name}`,
      severity: 'success'
    });
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TrainIcon sx={{ fontSize: 40, color: 'white' }} />
          <Box>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 'bold' }}>
              Advanced AGI Training
            </Typography>
            <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.8)' }}>
              Train and fine-tune AI models with advanced capabilities
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* Training Status */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ProgressIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Training Status
              </Typography>
              
              {trainingStatus ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body1">
                      Status: <Chip 
                        label={trainingStatus.is_training ? 'Training' : 'Ready'} 
                        color={trainingStatus.is_training ? 'warning' : 'success'}
                        icon={trainingStatus.is_training ? <CircularProgress size={16} /> : <CompleteIcon />}
                      />
                    </Typography>
                    
                    {!trainingStatus.is_training && (
                      <Button
                        variant="contained"
                        startIcon={<StartIcon />}
                        onClick={() => setShowTrainingDialog(true)}
                        sx={{ background: 'linear-gradient(45deg, #667eea, #764ba2)' }}
                      >
                        Start Training
                      </Button>
                    )}
                  </Box>
                  
                  {trainingStatus.current_session && (
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Current Session: {trainingStatus.current_session.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Started: {new Date(trainingStatus.current_session.start_time).toLocaleString()}
                      </Typography>
                      <LinearProgress sx={{ mt: 1 }} />
                    </Box>
                  )}
                </Box>
              ) : (
                <Typography>Loading training status...</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Model Information */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AIIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Model Info
              </Typography>
              
              {modelInfo ? (
                <Box>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Device: {modelInfo.device}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Models: {modelInfo.models_loaded?.length || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Pipelines: {modelInfo.pipelines_loaded?.length || 0}
                  </Typography>
                  <Chip 
                    label="Training Ready" 
                    color="success" 
                    size="small"
                    icon={<CheckCircle />}
                  />
                </Box>
              ) : (
                <CircularProgress size={24} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Data Management */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <DataIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Training Data Management
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={() => setShowUploadDialog(true)}
                >
                  Add Data
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CloudUploadIcon />}
                  component="label"
                >
                  Upload File
                  <input
                    type="file"
                    hidden
                    accept=".json,.csv,.txt"
                    onChange={handleFileUpload}
                  />
                </Button>
              </Box>

              {/* Sample Datasets */}
              <Typography variant="h6" gutterBottom>Sample Datasets</Typography>
              <Grid container spacing={2}>
                {sampleDatasets.map((dataset, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>
                          {dataset.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {dataset.description}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Chip label={`${dataset.size} examples`} size="small" />
                          <Button 
                            size="small" 
                            onClick={() => loadSampleDataset(dataset)}
                          >
                            Load
                          </Button>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Current Training Data */}
              {trainingData.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Current Training Data ({trainingData.length} examples)
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Text</TableCell>
                          <TableCell>Label</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {trainingData.slice(0, 5).map((item) => (
                          <TableRow key={item.id}>
                            <TableCell>{item.id}</TableCell>
                            <TableCell>{item.text.substring(0, 50)}...</TableCell>
                            <TableCell>{item.label}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  {trainingData.length > 5 && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Showing 5 of {trainingData.length} examples
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* AGI Features */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <MemoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AGI Training Features
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Memory-Based Learning</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2">
                        The AGI system continuously learns from interactions and stores knowledge
                        in its memory bank for future reference and improved responses.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Multi-Model Training</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2">
                        Train multiple AI models simultaneously including language generation,
                        sentiment analysis, question answering, and classification models.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Continuous Learning</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2">
                        The system can learn and adapt from every interaction, automatically
                        improving its performance without manual intervention.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Advanced Reasoning</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2">
                        Implements advanced reasoning capabilities including logical inference,
                        causal reasoning, and contextual understanding.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Training Configuration Dialog */}
      <Dialog open={showTrainingDialog} onClose={() => setShowTrainingDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Configure Training Session</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Session Name"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                margin="normal"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  label="Model Type"
                >
                  <MenuItem value="classification">Classification</MenuItem>
                  <MenuItem value="generation">Text Generation</MenuItem>
                  <MenuItem value="sentiment">Sentiment Analysis</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Learning Rate"
                value={learningRate}
                onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                margin="normal"
                inputProps={{ step: 1e-5 }}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Epochs"
                value={numEpochs}
                onChange={(e) => setNumEpochs(parseInt(e.target.value))}
                margin="normal"
                inputProps={{ min: 1, max: 20 }}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Batch Size"
                value={batchSize}
                onChange={(e) => setBatchSize(parseInt(e.target.value))}
                margin="normal"
                inputProps={{ min: 1, max: 32 }}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Max Length"
                value={maxLength}
                onChange={(e) => setMaxLength(parseInt(e.target.value))}
                margin="normal"
                inputProps={{ min: 128, max: 1024 }}
              />
            </Grid>
          </Grid>
          
          <Alert severity="info" sx={{ mt: 2 }}>
            Training will use {trainingData.length} examples. Make sure you have sufficient training data loaded.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTrainingDialog(false)}>Cancel</Button>
          <Button onClick={startTraining} variant="contained" disabled={!sessionName || trainingData.length === 0}>
            Start Training
          </Button>
        </DialogActions>
      </Dialog>

      {/* Data Upload Dialog */}
      <Dialog open={showUploadDialog} onClose={() => setShowUploadDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Custom Training Data</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={8}
            label="Training Text (one example per line)"
            value={customData}
            onChange={(e) => setCustomData(e.target.value)}
            margin="normal"
            placeholder="Enter training examples, one per line..."
          />
          <Alert severity="info" sx={{ mt: 2 }}>
            Each line will be treated as a separate training example with default label 0.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUploadDialog(false)}>Cancel</Button>
          <Button onClick={addCustomData} variant="contained" disabled={!customData.trim()}>
            Add Data
          </Button>
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
    </Container>
  );
};

export default AdvancedTrainingPage;
