import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  TextField,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  CloudUpload,
  PlayArrow,
  Stop,
  GetApp,
  Visibility,
  Delete,
  ModelTraining,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import Papa from 'papaparse';
import toast from 'react-hot-toast';

import { fineTuneAPI } from '../services/api';

const FineTunePage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [trainingData, setTrainingData] = useState([]);
  const [validationData, setValidationData] = useState([]);
  const [datasetName, setDatasetName] = useState('');
  const [trainingTasks, setTrainingTasks] = useState([]);
  const [fineTunedModels, setFineTunedModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [taskStatusDialog, setTaskStatusDialog] = useState(null);
  
  // Training parameters
  const [learningRate, setLearningRate] = useState(2e-5);
  const [batchSize, setBatchSize] = useState(16);
  const [numEpochs, setNumEpochs] = useState(3);
  const [saveModel, setSaveModel] = useState(true);

  const steps = [
    'Upload Training Data',
    'Configure Parameters',
    'Start Training',
    'Monitor Progress'
  ];

  useEffect(() => {
    loadTrainingTasks();
    loadFineTunedModels();
  }, []);

  const loadTrainingTasks = async () => {
    try {
      const response = await fineTuneAPI.listTrainingTasks();
      setTrainingTasks(response.data.tasks);
    } catch (error) {
      console.error('Error loading training tasks:', error);
    }
  };

  const loadFineTunedModels = async () => {
    try {
      const response = await fineTuneAPI.listFineTunedModels();
      setFineTunedModels(response.data.models);
    } catch (error) {
      console.error('Error loading fine-tuned models:', error);
    }
  };

  const onDropTraining = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      Papa.parse(file, {
        complete: (results) => {
          const data = results.data
            .filter(row => row.length >= 2 && row[0] && row[1])
            .map(row => ({
              text: row[0],
              label: row[1].toLowerCase()
            }));
          setTrainingData(data);
          toast.success(`Loaded ${data.length} training samples`);
        },
        header: false,
        skipEmptyLines: true
      });
    }
  };

  const onDropValidation = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      Papa.parse(file, {
        complete: (results) => {
          const data = results.data
            .filter(row => row.length >= 2 && row[0] && row[1])
            .map(row => ({
              text: row[0],
              label: row[1].toLowerCase()
            }));
          setValidationData(data);
          toast.success(`Loaded ${data.length} validation samples`);
        },
        header: false,
        skipEmptyLines: true
      });
    }
  };

  const { getRootProps: getTrainingRootProps, getInputProps: getTrainingInputProps, isDragActive: isTrainingDragActive } = useDropzone({
    onDrop: onDropTraining,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    multiple: false
  });

  const { getRootProps: getValidationRootProps, getInputProps: getValidationInputProps, isDragActive: isValidationDragActive } = useDropzone({
    onDrop: onDropValidation,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    multiple: false
  });

  const startFineTuning = async () => {
    if (!datasetName || trainingData.length === 0) {
      toast.error('Please provide dataset name and training data');
      return;
    }

    try {
      setLoading(true);
      
      const response = await fineTuneAPI.startFineTuning({
        dataset_name: datasetName,
        training_data: trainingData,
        validation_data: validationData.length > 0 ? validationData : null,
        learning_rate: learningRate,
        batch_size: batchSize,
        num_epochs: numEpochs,
        save_model: saveModel
      });

      toast.success('Fine-tuning started successfully!');
      setActiveStep(3);
      loadTrainingTasks();
      
    } catch (error) {
      console.error('Error starting fine-tuning:', error);
      toast.error('Failed to start fine-tuning');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'default';
      default:
        return 'warning';
    }
  };

  const formatDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.round((end - start) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.round(duration / 60)}m`;
    return `${Math.round(duration / 3600)}h`;
  };

  const cancelTask = async (taskId) => {
    try {
      await fineTuneAPI.cancelTrainingTask(taskId);
      toast.success('Task cancelled');
      loadTrainingTasks();
    } catch (error) {
      console.error('Error cancelling task:', error);
      toast.error('Failed to cancel task');
    }
  };

  const loadModel = async (modelPath) => {
    try {
      setLoading(true);
      await fineTuneAPI.loadFineTunedModel(modelPath);
      toast.success('Model loaded successfully');
    } catch (error) {
      console.error('Error loading model:', error);
      toast.error('Failed to load model');
    } finally {
      setLoading(false);
    }
  };

  const TaskStatusDialog = ({ task, onClose }) => {
    const [taskStatus, setTaskStatus] = useState(null);

    useEffect(() => {
      if (task) {
        const interval = setInterval(async () => {
          try {
            const response = await fineTuneAPI.getTrainingStatus(task.task_id);
            setTaskStatus(response.data);
          } catch (error) {
            console.error('Error fetching task status:', error);
          }
        }, 2000);

        return () => clearInterval(interval);
      }
    }, [task]);

    return (
      <Dialog open={!!task} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Training Task Status</DialogTitle>
        <DialogContent>
          {taskStatus && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {taskStatus.task_id}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={taskStatus.status} 
                  color={getStatusColor(taskStatus.status)}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Progress: {(taskStatus.progress * 100).toFixed(1)}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={taskStatus.progress * 100}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              {taskStatus.current_epoch && (
                <Typography variant="body2" gutterBottom>
                  Epoch: {taskStatus.current_epoch} / {taskStatus.total_epochs}
                </Typography>
              )}

              {taskStatus.loss && (
                <Typography variant="body2" gutterBottom>
                  Loss: {taskStatus.loss.toFixed(4)}
                </Typography>
              )}

              {taskStatus.accuracy && (
                <Typography variant="body2" gutterBottom>
                  Accuracy: {(taskStatus.accuracy * 100).toFixed(2)}%
                </Typography>
              )}

              <Typography variant="body2" color="text.secondary">
                Created: {new Date(taskStatus.created_at).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last Updated: {new Date(taskStatus.updated_at).toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 600 }}>
          Fine-tune FinBERT Model
        </Typography>

        {/* Stepper */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>

        <Grid container spacing={3}>
          {/* Main Content */}
          <Grid item xs={12} lg={8}>
            <AnimatePresence mode="wait">
              {/* Step 0: Upload Data */}
              {activeStep === 0 && (
                <motion.div
                  key="step0"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Upload Training Data
                      </Typography>
                      
                      <TextField
                        fullWidth
                        label="Dataset Name"
                        value={datasetName}
                        onChange={(e) => setDatasetName(e.target.value)}
                        sx={{ mb: 3 }}
                      />

                      {/* Training Data Upload */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          Training Data (Required)
                        </Typography>
                        <Paper
                          {...getTrainingRootProps()}
                          sx={{
                            border: '2px dashed',
                            borderColor: isTrainingDragActive ? 'primary.main' : 'grey.300',
                            p: 3,
                            textAlign: 'center',
                            cursor: 'pointer',
                            bgcolor: isTrainingDragActive ? 'action.hover' : 'transparent'
                          }}
                        >
                          <input {...getTrainingInputProps()} />
                          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                          <Typography variant="body1">
                            {isTrainingDragActive 
                              ? 'Drop the file here...' 
                              : 'Drag & drop training data or click to select'
                            }
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            CSV format: text,label (positive/negative/neutral)
                          </Typography>
                        </Paper>
                        {trainingData.length > 0 && (
                          <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                            ✓ {trainingData.length} training samples loaded
                          </Typography>
                        )}
                      </Box>

                      {/* Validation Data Upload */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          Validation Data (Optional)
                        </Typography>
                        <Paper
                          {...getValidationRootProps()}
                          sx={{
                            border: '2px dashed',
                            borderColor: isValidationDragActive ? 'primary.main' : 'grey.300',
                            p: 3,
                            textAlign: 'center',
                            cursor: 'pointer',
                            bgcolor: isValidationDragActive ? 'action.hover' : 'transparent'
                          }}
                        >
                          <input {...getValidationInputProps()} />
                          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                          <Typography variant="body1">
                            {isValidationDragActive 
                              ? 'Drop the file here...' 
                              : 'Drag & drop validation data or click to select'
                            }
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            CSV format: text,label (positive/negative/neutral)
                          </Typography>
                        </Paper>
                        {validationData.length > 0 && (
                          <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                            ✓ {validationData.length} validation samples loaded
                          </Typography>
                        )}
                      </Box>

                      <Box display="flex" justifyContent="flex-end">
                        <Button
                          variant="contained"
                          onClick={() => setActiveStep(1)}
                          disabled={!datasetName || trainingData.length === 0}
                        >
                          Next: Configure Parameters
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Step 1: Configure Parameters */}
              {activeStep === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Training Parameters
                      </Typography>

                      <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            label="Learning Rate"
                            type="number"
                            value={learningRate}
                            onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                            inputProps={{ step: 1e-6, min: 1e-6, max: 1e-2 }}
                          />
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth>
                            <InputLabel>Batch Size</InputLabel>
                            <Select
                              value={batchSize}
                              label="Batch Size"
                              onChange={(e) => setBatchSize(e.target.value)}
                            >
                              <MenuItem value={8}>8</MenuItem>
                              <MenuItem value={16}>16</MenuItem>
                              <MenuItem value={32}>32</MenuItem>
                              <MenuItem value={64}>64</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth>
                            <InputLabel>Number of Epochs</InputLabel>
                            <Select
                              value={numEpochs}
                              label="Number of Epochs"
                              onChange={(e) => setNumEpochs(e.target.value)}
                            >
                              <MenuItem value={1}>1</MenuItem>
                              <MenuItem value={2}>2</MenuItem>
                              <MenuItem value={3}>3</MenuItem>
                              <MenuItem value={5}>5</MenuItem>
                              <MenuItem value={10}>10</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={saveModel}
                                onChange={(e) => setSaveModel(e.target.checked)}
                              />
                            }
                            label="Save Trained Model"
                          />
                        </Grid>
                      </Grid>

                      <Box display="flex" justifyContent="space-between" sx={{ mt: 3 }}>
                        <Button onClick={() => setActiveStep(0)}>
                          Back
                        </Button>
                        <Button
                          variant="contained"
                          onClick={() => setActiveStep(2)}
                        >
                          Next: Review & Start
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Step 2: Review & Start */}
              {activeStep === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Review Configuration
                      </Typography>

                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Dataset Name:</Typography>
                          <Typography variant="body1">{datasetName}</Typography>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Training Samples:</Typography>
                          <Typography variant="body1">{trainingData.length}</Typography>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Validation Samples:</Typography>
                          <Typography variant="body1">{validationData.length || 'None'}</Typography>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Learning Rate:</Typography>
                          <Typography variant="body1">{learningRate}</Typography>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Batch Size:</Typography>
                          <Typography variant="body1">{batchSize}</Typography>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2">Epochs:</Typography>
                          <Typography variant="body1">{numEpochs}</Typography>
                        </Grid>
                      </Grid>

                      <Box display="flex" justifyContent="space-between" sx={{ mt: 3 }}>
                        <Button onClick={() => setActiveStep(1)}>
                          Back
                        </Button>
                        <Button
                          variant="contained"
                          startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                          onClick={startFineTuning}
                          disabled={loading}
                          color="success"
                        >
                          {loading ? 'Starting...' : 'Start Fine-tuning'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Step 3: Monitor Progress */}
              {activeStep === 3 && (
                <motion.div
                  key="step3"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Training Progress
                      </Typography>
                      
                      <Typography variant="body1" sx={{ mb: 2 }}>
                        Fine-tuning has been started! Monitor the progress in the training tasks table below.
                      </Typography>

                      <Box display="flex" justifyContent="flex-start">
                        <Button
                          variant="outlined"
                          onClick={() => setActiveStep(0)}
                        >
                          Start New Training
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </Grid>

          {/* Side Panel */}
          <Grid item xs={12} lg={4}>
            {/* Training Tasks */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Training Tasks
                </Typography>
                
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Dataset</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trainingTasks.map((task) => (
                        <TableRow key={task.task_id}>
                          <TableCell>
                            <Typography variant="body2">
                              {task.dataset_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatDuration(task.created_at, task.completed_at)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={task.status} 
                              color={getStatusColor(task.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={0.5}>
                              <Button
                                size="small"
                                onClick={() => setTaskStatusDialog(task)}
                              >
                                <Visibility fontSize="small" />
                              </Button>
                              {task.status === 'running' && (
                                <Button
                                  size="small"
                                  color="error"
                                  onClick={() => cancelTask(task.task_id)}
                                >
                                  <Stop fontSize="small" />
                                </Button>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Fine-tuned Models */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Fine-tuned Models
                </Typography>
                
                <Box>
                  {fineTunedModels.map((model) => (
                    <Paper key={model.name} sx={{ p: 2, mb: 2 }}>
                      <Typography variant="subtitle2">{model.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(model.created_at).toLocaleDateString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        {model.size_mb.toFixed(1)} MB
                      </Typography>
                      
                      <Box display="flex" gap={1} sx={{ mt: 1 }}>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => loadModel(model.path)}
                          disabled={loading}
                        >
                          <GetApp fontSize="small" />
                        </Button>
                      </Box>
                    </Paper>
                  ))}
                  
                  {fineTunedModels.length === 0 && (
                    <Typography variant="body2" color="text.secondary">
                      No fine-tuned models available
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Task Status Dialog */}
        <TaskStatusDialog 
          task={taskStatusDialog} 
          onClose={() => setTaskStatusDialog(null)} 
        />
      </motion.div>
    </Container>
  );
};

export default FineTunePage;
