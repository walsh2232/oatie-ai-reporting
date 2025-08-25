import { createTheme, type Theme } from '@mui/material/styles';

// Oracle Redwood Design System color tokens
const oracleColors = {
  // Primary Oracle Red
  primary: {
    50: '#fef2f2',
    100: '#fde6e6',
    200: '#facccc',
    300: '#f8a3a3',
    400: '#f37373',
    500: '#ec4c4c',
    600: '#da2b2b',
    700: '#b71c1c',
    800: '#991b1b',
    900: '#7f1d1d',
    950: '#450a0a',
  },
  // Oracle Blue
  secondary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },
  // Neutral grays
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e5e5e5',
    300: '#d4d4d4',
    400: '#a3a3a3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
    950: '#0a0a0a',
  },
  // Status colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
    950: '#052e16',
  },
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
    950: '#451a03',
  },
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
    950: '#450a0a',
  },
};

// Oracle Redwood typography using Oracle Sans
const typography = {
  fontFamily: [
    '"Oracle Sans"',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
  ].join(','),
  h1: {
    fontSize: '2.5rem',
    fontWeight: 600,
    lineHeight: 1.2,
    letterSpacing: '-0.025em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.25,
    letterSpacing: '-0.025em',
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.6,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5,
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.4,
  },
};

// Create Oracle Redwood Material-UI theme
export const oracleRedwoodTheme: Theme = createTheme({
  palette: {
    primary: {
      main: oracleColors.primary[600],
      light: oracleColors.primary[400],
      dark: oracleColors.primary[800],
      contrastText: '#ffffff',
    },
    secondary: {
      main: oracleColors.secondary[600],
      light: oracleColors.secondary[400],
      dark: oracleColors.secondary[800],
      contrastText: '#ffffff',
    },
    error: {
      main: oracleColors.error[500],
      light: oracleColors.error[300],
      dark: oracleColors.error[700],
    },
    warning: {
      main: oracleColors.warning[500],
      light: oracleColors.warning[300],
      dark: oracleColors.warning[700],
    },
    success: {
      main: oracleColors.success[500],
      light: oracleColors.success[300],
      dark: oracleColors.success[700],
    },
    grey: oracleColors.neutral,
    background: {
      default: oracleColors.neutral[50],
      paper: '#ffffff',
    },
    text: {
      primary: oracleColors.neutral[900],
      secondary: oracleColors.neutral[600],
    },
  },
  typography,
  spacing: (factor: number) => `${8 * factor}px`,
  shape: {
    borderRadius: 8,
  },
  components: {
    // Oracle Redwood button styling
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
          padding: '12px 24px',
          fontSize: '0.875rem',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    // Oracle card styling
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          border: `1px solid ${oracleColors.neutral[200]}`,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.12)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    // Oracle input field styling
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: '#ffffff',
            '& fieldset': {
              borderColor: oracleColors.neutral[300],
            },
            '&:hover fieldset': {
              borderColor: oracleColors.primary[400],
            },
            '&.Mui-focused fieldset': {
              borderColor: oracleColors.primary[600],
              borderWidth: 2,
            },
          },
        },
      },
    },
    // Oracle app bar styling
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: oracleColors.neutral[900],
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          borderBottom: `1px solid ${oracleColors.neutral[200]}`,
        },
      },
    },
    // Oracle paper styling
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    // Oracle dialog styling
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          padding: '8px',
        },
      },
    },
  },
});

export default oracleRedwoodTheme;