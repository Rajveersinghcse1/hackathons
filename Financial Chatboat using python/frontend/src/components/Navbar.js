import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Analytics as AnalyticsIcon,
  Tune as TuneIcon,
  Home as HomeIcon,
  Psychology as AGIIcon,
  School as TrainIcon,
  MonetizationOn as FinancialIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'Financial AI', path: '/', icon: <FinancialIcon /> },
    { label: 'Chat', path: '/chat', icon: <ChatIcon /> },
    { label: 'AGI Chat', path: '/agi-chat', icon: <AGIIcon /> },
    { label: 'Analytics', path: '/analytics', icon: <AnalyticsIcon /> },
    { label: 'Fine-tune', path: '/finetune', icon: <TuneIcon /> },
    { label: 'AGI Training', path: '/agi-training', icon: <TrainIcon /> },
  ];

  return (
    <AppBar 
      position="sticky" 
      sx={{ 
        background: 'rgba(26, 31, 58, 0.9)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Toolbar>
        <Avatar 
          sx={{ 
            bgcolor: 'primary.main', 
            mr: 2,
            width: 40,
            height: 40,
          }}
        >
          A
        </Avatar>
        
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            fontWeight: 700,
            background: 'linear-gradient(45deg, #2196f3 30%, #ff9800 90%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Advanced AGI Chatbot
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                px: 2,
                py: 1,
                backgroundColor: location.pathname === item.path ? 'rgba(33, 150, 243, 0.2)' : 'transparent',
                border: location.pathname === item.path ? '1px solid rgba(33, 150, 243, 0.5)' : '1px solid transparent',
                '&:hover': {
                  backgroundColor: 'rgba(33, 150, 243, 0.1)',
                  border: '1px solid rgba(33, 150, 243, 0.3)',
                },
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
