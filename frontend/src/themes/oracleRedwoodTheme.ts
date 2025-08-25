import { createTheme, Theme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// Oracle Redwood Design System - Clean Implementation
const oracleColors = {
  primary: {
    main: '#e27938',
    light: '#efb883', 
    dark: '#b04e23',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#757575',
    light: '#bdbdbd',
    dark: '#424242',
    contrastText: '#ffffff',
  },
  error: {
    main: '#f44336',
    light: '#e57373',
    dark: '#d32f2f',
  },
  warning: {
    main: '#ffc107',
    light: '#ffd54f', 
    dark: '#ffa000',
  },
  info: {
    main: '#2196f3',
    light: '#64b5f6',
    dark: '#1976d2',
  },
  success: {
    main: '#4caf50',
    light: '#81c784',
    dark: '#388e3c',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
};

// Create Oracle Redwood Theme
export const oracleRedwoodTheme: Theme = createTheme({
  palette: {
    mode: 'light',
    primary: oracleColors.primary,
    secondary: oracleColors.secondary,
    error: oracleColors.error,
    warning: oracleColors.warning,
    info: oracleColors.info,
    success: oracleColors.success,
    grey: oracleColors.grey,
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
      disabled: '#bdbdbd',
    },
    action: {
      active: '#757575',
      hover: alpha('#e27938', 0.04),
      selected: alpha('#e27938', 0.08),
      disabled: '#e0e0e0',
      disabledBackground: '#f5f5f5',
    },
    divider: '#eeeeee',
  },
  typography: {
    fontFamily: [
      '"Oracle Sans"',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 300,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem', 
      fontWeight: 300,
      lineHeight: 1.2,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 400,
      lineHeight: 1.2,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.43,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.75,
      textTransform: 'none' as const,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          padding: '8px 24px',
          minHeight: 40,
        },
        contained: {
          background: `linear-gradient(135deg, ${oracleColors.primary.main} 0%, ${oracleColors.primary.dark} 100%)`,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&.Mui-focused': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: oracleColors.primary.main,
                borderWidth: 2,
              },
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: `1px solid ${oracleColors.grey[200]}`,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: oracleColors.grey[900],
          borderBottom: `1px solid ${oracleColors.grey[200]}`,
        },
      },
    },
  },
});

export default oracleRedwoodTheme;
