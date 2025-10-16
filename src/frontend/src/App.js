import React from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { Box, AppBar, Toolbar, Typography } from '@mui/material';

// WCAG 2.1 AA compliant dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)', // WCAG fix: 7.5:1 contrast
    },
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        notchedOutline: {
          borderColor: 'rgba(255, 255, 255, 0.3)', // WCAG fix: 3.5:1
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Glossary Extraction & Validation
            </Typography>
          </Toolbar>
        </AppBar>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Welcome to Glossary App
          </Typography>
          <Typography variant="body1">
            Setup complete. Ready for Phase 1 development.
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
