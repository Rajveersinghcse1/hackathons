import React, { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Box, Button, TextField, Card,
  CardContent, Grid, Tab, Tabs, Alert, CircularProgress,
  Accordion, AccordionSummary, AccordionDetails, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  FormControl, InputLabel, Select, MenuItem, Slider
} from '@mui/material';
import {
  TrendingUp, Assessment, Psychology, AccountBalance, 
  ExpandMore, Send, Analytics, PieChart, Timeline,
  Security, Calculate, Insights, MonetizationOn
} from '@mui/icons-material';

const AdvancedFinancialPage = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userProfile, setUserProfile] = useState({
    age: 35,
    risk_tolerance: 'medium',
    investment_horizon: 10,
    income: 75000,
    current_savings: 25000,
    monthly_savings: 500,
    goals: ['retirement'],
    retirement_age: 65
  });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [financialData, setFinancialData] = useState({
    stock_price: 150,
    eps: 8,
    total_debt: 1000000,
    total_equity: 2000000,
    current_assets: 800000,
    current_liabilities: 400000,
    net_income: 300000,
    shareholders_equity: 1800000
  });

  // Initialize with welcome message
  useEffect(() => {
    setMessages([{
      id: Date.now(),
      type: 'bot',
      content: `🤖 Welcome to the Advanced Financial Assistant!

I'm your comprehensive financial advisor powered by multiple ML models. I can help you with:

📊 **Investment Analysis & Portfolio Optimization**
💰 **Financial Planning & Retirement Strategies** 
📈 **Market Analysis & Trend Prediction**
🏢 **Company Valuation & Risk Assessment**
⚖️ **Risk Management & Asset Allocation**

Use the tabs above to explore different features, or simply chat with me about your financial questions!`,
      timestamp: new Date().toISOString()
    }]);
  }, []);

  // API Base URL
  const API_BASE = 'http://localhost:8002';

  // Send chat message
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          user_profile: userProfile
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: data.response,
          sentiment: data.sentiment,
          intent: data.intent,
          analysis: data.analysis,
          recommendations: data.recommendations,
          timestamp: data.timestamp
        };

        setMessages(prev => [...prev, botMessage]);
        setAnalysisResults(data.analysis);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: '❌ Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Get investment advice
  const getInvestmentAdvice = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/investment/advice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisResults({ investment_advice: data.investment_advice });
      }
    } catch (error) {
      console.error('Investment advice error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Analyze financial ratios
  const analyzeFinancialRatios = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/analysis/financial`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_type: 'ratios',
          data: financialData
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisResults({ financial_ratios: data.results });
      }
    } catch (error) {
      console.error('Financial analysis error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Get market analysis
  const getMarketAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/market/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          market_data: null,
          timeframe: '1month'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMarketData(data.market_analysis);
      }
    } catch (error) {
      console.error('Market analysis error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Run demo analysis
  const runDemoAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/demo/sample-analysis`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisResults(data.demo_analysis);
      }
    } catch (error) {
      console.error('Demo analysis error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Chat Interface
  const ChatInterface = () => (
    <Box>
      {/* Messages Display */}
      <Box 
        sx={{ 
          height: 400, 
          overflowY: 'auto', 
          border: '1px solid #ddd', 
          borderRadius: 2, 
          p: 2, 
          mb: 2,
          backgroundColor: '#f8f9fa'
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              mb: 2,
              p: 2,
              borderRadius: 2,
              maxWidth: '80%',
              alignSelf: message.type === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: message.type === 'user' ? '#2196f3' : '#fff',
              color: message.type === 'user' ? '#fff' : '#000',
              ml: message.type === 'user' ? 'auto' : 0,
              boxShadow: 1
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Typography>
            {message.sentiment && (
              <Box sx={{ mt: 1 }}>
                <Chip 
                  label={`Sentiment: ${message.sentiment.sentiment} (${(message.sentiment.confidence * 100).toFixed(1)}%)`}
                  size="small"
                  color={message.sentiment.sentiment === 'Positive' ? 'success' : 
                         message.sentiment.sentiment === 'Negative' ? 'error' : 'default'}
                />
                {message.intent && (
                  <Chip 
                    label={`Intent: ${message.intent}`}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
            )}
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>

      {/* Message Input */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask me about investments, market analysis, financial planning..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={isLoading}
        />
        <Button
          variant="contained"
          onClick={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
          startIcon={<Send />}
        >
          Send
        </Button>
      </Box>
    </Box>
  );

  // User Profile Editor
  const UserProfileEditor = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Psychology sx={{ mr: 1 }} />
          User Profile
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Age"
              type="number"
              value={userProfile.age}
              onChange={(e) => setUserProfile({...userProfile, age: parseInt(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Risk Tolerance</InputLabel>
              <Select
                value={userProfile.risk_tolerance}
                onChange={(e) => setUserProfile({...userProfile, risk_tolerance: e.target.value})}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Annual Income ($)"
              type="number"
              value={userProfile.income}
              onChange={(e) => setUserProfile({...userProfile, income: parseFloat(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Current Savings ($)"
              type="number"
              value={userProfile.current_savings}
              onChange={(e) => setUserProfile({...userProfile, current_savings: parseFloat(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Monthly Savings ($)"
              type="number"
              value={userProfile.monthly_savings}
              onChange={(e) => setUserProfile({...userProfile, monthly_savings: parseFloat(e.target.value)})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Investment Horizon (years)"
              type="number"
              value={userProfile.investment_horizon}
              onChange={(e) => setUserProfile({...userProfile, investment_horizon: parseInt(e.target.value)})}
            />
          </Grid>
        </Grid>
        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            onClick={getInvestmentAdvice}
            disabled={isLoading}
            startIcon={<TrendingUp />}
          >
            Get Personalized Investment Advice
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  // Financial Analysis Tools
  const FinancialAnalysisTools = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Calculate sx={{ mr: 1 }} />
              Financial Ratios Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Stock Price"
                  type="number"
                  value={financialData.stock_price}
                  onChange={(e) => setFinancialData({...financialData, stock_price: parseFloat(e.target.value)})}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="EPS"
                  type="number"
                  value={financialData.eps}
                  onChange={(e) => setFinancialData({...financialData, eps: parseFloat(e.target.value)})}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Total Debt"
                  type="number"
                  value={financialData.total_debt}
                  onChange={(e) => setFinancialData({...financialData, total_debt: parseFloat(e.target.value)})}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Total Equity"
                  type="number"
                  value={financialData.total_equity}
                  onChange={(e) => setFinancialData({...financialData, total_equity: parseFloat(e.target.value)})}
                />
              </Grid>
            </Grid>
            <Button
              variant="contained"
              onClick={analyzeFinancialRatios}
              disabled={isLoading}
              sx={{ mt: 2 }}
              startIcon={<Assessment />}
            >
              Analyze Ratios
            </Button>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Timeline sx={{ mr: 1 }} />
              Market Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Get comprehensive market trend analysis using advanced ML models
            </Typography>
            <Button
              variant="contained"
              onClick={getMarketAnalysis}
              disabled={isLoading}
              startIcon={<Analytics />}
            >
              Analyze Market Trends
            </Button>
            
            {marketData && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Market Analysis Results:</Typography>
                <Typography variant="body2">Current Price: ${marketData.current_price}</Typography>
                <Typography variant="body2">Volatility: {marketData.volatility}%</Typography>
                <Typography variant="body2">Trend: {marketData.trend}</Typography>
                <Typography variant="body2">Momentum: {marketData.momentum}%</Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Analysis Results Display
  const AnalysisResultsDisplay = () => (
    analysisResults && (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          <Insights sx={{ mr: 1 }} />
          Analysis Results
        </Typography>
        
        {analysisResults.investment_advice && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Investment Advice</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="subtitle2">Recommended Strategy: {analysisResults.investment_advice.recommended_strategy}</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>Expected Return: {analysisResults.investment_advice.expected_return}</Typography>
                
                <Typography variant="subtitle2" sx={{ mt: 2 }}>Asset Allocation:</Typography>
                {Object.entries(analysisResults.investment_advice.asset_allocation).map(([asset, percentage]) => (
                  <Box key={asset} sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                    <Typography>{asset.charAt(0).toUpperCase() + asset.slice(1)}</Typography>
                    <Typography>{percentage}%</Typography>
                  </Box>
                ))}
                
                {analysisResults.investment_advice.specific_recommendations && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">Specific Recommendations:</Typography>
                    {analysisResults.investment_advice.specific_recommendations.map((rec, index) => (
                      <Alert key={index} severity="info" sx={{ mt: 1 }}>
                        <strong>{rec.type}:</strong> {rec.recommendation}
                      </Alert>
                    ))}
                  </Box>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        )}

        {analysisResults.financial_ratios && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Financial Ratios Analysis</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Ratio</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Interpretation</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(analysisResults.financial_ratios).map(([ratio, data]) => (
                      <TableRow key={ratio}>
                        <TableCell>{ratio.replace('_', ' ').toUpperCase()}</TableCell>
                        <TableCell>{data.value}</TableCell>
                        <TableCell>{data.interpretation}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        )}

        {analysisResults.financial_plan && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Financial Planning Analysis</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="subtitle2">Retirement Projections:</Typography>
                <Typography>Projected Savings: ${analysisResults.financial_plan.projected_retirement_savings.toLocaleString()}</Typography>
                <Typography>Monthly Income: ${analysisResults.financial_plan.projected_monthly_income.toLocaleString()}</Typography>
                <Typography>Target Met: {analysisResults.financial_plan.meets_target ? '✅ Yes' : '❌ No'}</Typography>
                
                {analysisResults.financial_plan.recommendations && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">Recommendations:</Typography>
                    {analysisResults.financial_plan.recommendations.map((rec, index) => (
                      <Alert key={index} severity="warning" sx={{ mt: 1 }}>
                        {rec}
                      </Alert>
                    ))}
                  </Box>
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        )}
      </Box>
    )
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom>
            <MonetizationOn sx={{ fontSize: 40, mr: 1, color: 'primary.main' }} />
            Advanced Financial Assistant
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Comprehensive Financial Analysis & Advisory with ML Models
          </Typography>
        </Box>

        {/* Demo Analysis Button */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Button
            variant="outlined"
            onClick={runDemoAnalysis}
            disabled={isLoading}
            startIcon={<PieChart />}
            size="large"
          >
            Run Demo Analysis
          </Button>
        </Box>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
          <Tab label="Chat Assistant" icon={<Psychology />} />
          <Tab label="User Profile" icon={<AccountBalance />} />
          <Tab label="Analysis Tools" icon={<Assessment />} />
        </Tabs>

        {/* Tab Content */}
        {activeTab === 0 && <ChatInterface />}
        {activeTab === 1 && <UserProfileEditor />}
        {activeTab === 2 && <FinancialAnalysisTools />}

        {/* Analysis Results */}
        <AnalysisResultsDisplay />

        {/* Loading Indicator */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress />
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default AdvancedFinancialPage;
