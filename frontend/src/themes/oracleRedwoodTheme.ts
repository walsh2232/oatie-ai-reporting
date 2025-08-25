import { createTheme, Theme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// Oracle JET Design System Color Palette
const oracleColors = {
  // Oracle Brand Colors
  primary: {
    50: '#fdf7f0',
    100: '#faebd7',
    200: '#f5d5ae',
    300: '#efb883',
    400: '#e89356',
    500: '#e27938',
    600: '#d4622a',
    700: '#b04e23',
    800: '#8e4024',
    900: '#713a22',
    main: '#e27938',
    dark: '#b04e23',
    light: '#efb883',
  },
  
  // Oracle Neutral Palette
  neutral: {
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

  // Oracle Semantic Colors
  success: {
    50: '#e8f5e8',
    100: '#c8e6c9',
    200: '#a5d6a7',
    300: '#81c784',
    400: '#66bb6a',
    500: '#4caf50',
    600: '#43a047',
    700: '#388e3c',
    800: '#2e7d32',
    900: '#1b5e20',
    main: '#4caf50',
  },
    gray90: '#212529',
    black: '#000000',
  }
};

// Oracle OCI Layout System (from Designer Toolkit)
const oracleOCILayout = {
  spacing: 32,                   // Base spacing unit from OCI layout engine
  iconSize: 40,                  // SVG icon dimensions
  simpleWidth: 40,               // Simple resource width
  detailedWidth: 170,            // Detailed resource width (from OCI research)
  containerWidth: 200,           // Container width
  containerHeight: 200,          // Container height
  borderRadius: 4,               // Standard border radius
};

// Oracle Typography System (Enterprise-grade)
const oracleTypography = {
  fontFamily: '"Oracle Sans", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
  weights: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  sizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
  }
};

// Oracle Box Shadow System
const oracleBoxShadows = {
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
};

// Oracle Redwood Theme with OCI Designer Toolkit patterns
export const oracleRedwoodTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: `rgb(${oracleOCIColors.brand.primary})`,
      light: `rgb(${oracleOCIColors.brand.light})`,
      dark: `rgb(${oracleOCIColors.brand.dark})`,
      contrastText: oracleOCIColors.neutral.white,
    },
    secondary: {
      main: `rgb(${oracleOCIColors.brand.secondary})`,
      light: `rgb(${oracleOCIColors.brand.light})`,
      dark: `rgb(${oracleOCIColors.brand.dark})`,
      contrastText: oracleOCIColors.neutral.white,
    },
    error: {
      main: `rgb(${oracleOCIColors.danger})`,
      contrastText: oracleOCIColors.neutral.white,
    },
    warning: {
      main: `rgb(${oracleOCIColors.warning})`,
      contrastText: oracleOCIColors.neutral.black,
    },
    info: {
      main: `rgb(${oracleOCIColors.info})`,
      contrastText: oracleOCIColors.neutral.white,
    },
    success: {
      main: `rgb(${oracleOCIColors.success})`,
      contrastText: oracleOCIColors.neutral.white,
    },
    background: {
      default: oracleOCIColors.console.background,
      paper: oracleOCIColors.console.panelBackground,
    },
    text: {
      primary: oracleOCIColors.console.text,
      secondary: oracleOCIColors.neutral.gray70,
      disabled: oracleOCIColors.neutral.gray50,
    },
    divider: oracleOCIColors.neutral.gray30,
    action: {
      hover: 'rgba(0, 0, 0, 0.04)',
      selected: oracleOCIColors.console.activeTab,
      disabled: oracleOCIColors.neutral.gray50,
    },
  },
  
  typography: {
    fontFamily: oracleTypography.fontFamily,
    h1: {
      fontSize: oracleTypography.sizes['4xl'],
      fontWeight: oracleTypography.weights.bold,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: oracleTypography.sizes['3xl'],
      fontWeight: oracleTypography.weights.semibold,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: oracleTypography.sizes['2xl'],
      fontWeight: oracleTypography.weights.semibold,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: oracleTypography.sizes.xl,
      fontWeight: oracleTypography.weights.semibold,
      lineHeight: 1.5,
    },
    h5: {
      fontSize: oracleTypography.sizes.lg,
      fontWeight: oracleTypography.weights.medium,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: oracleTypography.sizes.base,
      fontWeight: oracleTypography.weights.medium,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: oracleTypography.sizes.base,
      fontWeight: oracleTypography.weights.regular,
      lineHeight: 1.6,
    },
    body2: {
      fontSize: oracleTypography.sizes.sm,
      fontWeight: oracleTypography.weights.regular,
      lineHeight: 1.5,
    },
    caption: {
      fontSize: oracleTypography.sizes.xs,
      fontWeight: oracleTypography.weights.regular,
      lineHeight: 1.4,
    },
    button: {
      fontSize: oracleTypography.sizes.sm,
      fontWeight: oracleTypography.weights.medium,
      textTransform: 'none',
      letterSpacing: '0.01em',
    },
  },
  
  spacing: (factor: number) => `${(oracleOCILayout.spacing / 8) * factor}px`,
  
  shape: {
    borderRadius: oracleOCILayout.borderRadius,
  },
  
  shadows: [
    'none',
    oracleBoxShadows.xs,
    oracleBoxShadows.sm,
    oracleBoxShadows.md,
    oracleBoxShadows.lg,
    oracleBoxShadows.xl,
    oracleBoxShadows['2xl'],
    // Additional Material-UI shadows
    '0 8px 16px rgba(0,0,0,0.15)',
    '0 12px 24px rgba(0,0,0,0.15)',
    '0 16px 32px rgba(0,0,0,0.15)',
    '0 20px 40px rgba(0,0,0,0.15)',
    '0 24px 48px rgba(0,0,0,0.15)',
    '0 28px 56px rgba(0,0,0,0.15)',
    '0 32px 64px rgba(0,0,0,0.15)',
    '0 36px 72px rgba(0,0,0,0.15)',
    '0 40px 80px rgba(0,0,0,0.15)',
    '0 44px 88px rgba(0,0,0,0.15)',
    '0 48px 96px rgba(0,0,0,0.15)',
    '0 52px 104px rgba(0,0,0,0.15)',
    '0 56px 112px rgba(0,0,0,0.15)',
    '0 60px 120px rgba(0,0,0,0.15)',
    '0 64px 128px rgba(0,0,0,0.15)',
    '0 68px 136px rgba(0,0,0,0.15)',
    '0 72px 144px rgba(0,0,0,0.15)',
    '0 76px 152px rgba(0,0,0,0.15)',
  ],
  
  components: {
    // Oracle OCI-inspired component overrides
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: oracleOCIColors.console.background,
          color: oracleOCIColors.console.text,
          boxShadow: oracleBoxShadows.sm,
          borderBottom: `1px solid ${oracleOCIColors.neutral.gray30}`,
        },
      },
    },
    
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: oracleOCILayout.borderRadius,
          textTransform: 'none',
          fontWeight: oracleTypography.weights.medium,
          minHeight: oracleOCILayout.iconSize, // OCI icon size for consistency
          padding: '8px 16px',
          boxShadow: oracleBoxShadows.xs,
          '&:hover': {
            boxShadow: oracleBoxShadows.sm,
          },
        },
        contained: {
          '&:hover': {
            boxShadow: oracleBoxShadows.md,
          },
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: oracleOCILayout.borderRadius * 2,
          boxShadow: oracleBoxShadows.sm,
          border: `1px solid ${oracleOCIColors.neutral.gray30}`,
          backgroundColor: oracleOCIColors.console.panelBackground,
          '&:hover': {
            boxShadow: oracleBoxShadows.md,
          },
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: oracleOCIColors.console.panelBackground,
          borderRadius: oracleOCILayout.borderRadius,
        },
        elevation1: {
          boxShadow: oracleBoxShadows.xs,
        },
        elevation2: {
          boxShadow: oracleBoxShadows.sm,
        },
        elevation3: {
          boxShadow: oracleBoxShadows.md,
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: oracleOCILayout.borderRadius,
            backgroundColor: oracleOCIColors.console.background,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: `rgb(${oracleOCIColors.brand.primary})`,
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: `rgb(${oracleOCIColors.brand.primary})`,
              borderWidth: '2px',
            },
          },
        },
      },
    },
    
    MuiTabs: {
      styleOverrides: {
        root: {
          backgroundColor: oracleOCIColors.console.tabBackground,
          borderBottom: `1px solid ${oracleOCIColors.neutral.gray30}`,
        },
        indicator: {
          backgroundColor: `rgb(${oracleOCIColors.brand.primary})`,
          height: 3,
        },
      },
    },
    
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: oracleTypography.weights.medium,
          color: oracleOCIColors.neutral.gray70,
          '&.Mui-selected': {
            backgroundColor: oracleOCIColors.console.activeTab,
            color: `rgb(${oracleOCIColors.brand.primary})`,
          },
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
          },
        },
      },
    },
    
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: oracleOCILayout.borderRadius * 2,
          boxShadow: oracleBoxShadows.xl,
          backgroundColor: oracleOCIColors.console.panelBackground,
        },
      },
    },
  },
} as ThemeOptions);

// Export Oracle color palette and layout constants for use in custom components
export { 
  oracleOCIColors, 
  oracleOCILayout, 
  oracleTypography, 
  oracleBoxShadows 
};

export default oracleRedwoodTheme;
    rgb160: '28, 28, 28',
    rgb170: '20, 20, 20',
    rgb180: '15, 15, 15',
    rgb190: '0, 0, 0',        // black
  },
  
  // Oracle Success Colors
  success: {
    rgb70: '25, 135, 84',
    rgb80: '32, 145, 94',
    rgb90: '40, 155, 104',
    rgb110: '20, 108, 67',
    rgb120: '15, 81, 50',
    rgb130: '198, 233, 198',
    rgb150: '144, 200, 144',
    rgb170: '90, 167, 90',
  },
  
  // Oracle Danger Colors  
  danger: {
    rgb70: '220, 53, 69',
    rgb90: '235, 87, 100',
    rgb110: '176, 42, 55',
    rgb120: '132, 32, 41',
    rgb130: '248, 215, 218',
    rgb150: '241, 169, 177',
    rgb170: '234, 123, 135',
  },
  
  // Oracle Warning Colors
  warning: {
    rgb60: '255, 193, 7',
    rgb70: '255, 183, 0',
    rgb90: '255, 205, 57',
    rgb110: '204, 154, 6',
    rgb120: '153, 116, 4',
    rgb130: '255, 243, 205',
    rgb150: '255, 235, 156',
    rgb170: '255, 227, 107',
  },
  
  // Oracle Info Colors
  info: {
    rgb70: '13, 110, 253',
    rgb80: '31, 120, 255',
    rgb90: '49, 130, 255',
    rgb110: '10, 88, 202',
    rgb120: '8, 66, 152',
    rgb130: '207, 226, 255',
    rgb150: '159, 196, 255',
    rgb170: '111, 166, 255',
  }
};

// OCI Designer Toolkit CSS Variables and Layout Patterns
const ocdThemeVariables = {
  // Console layout colors from OCD research
  consoleBackground: 'rgb(255, 255, 255)',
  propertiesPanelBackground: 'rgb(255, 255, 255)',
  activeTabBackground: 'rgb(209, 209, 212)',
  dialogBorder: 'rgb(19, 18, 67)',
  dialogHighlight: 'rgb(230, 232, 244)',
  toolbarButton: 'rgb(245, 245, 245)',
  paletteIcon: 'rgb(44, 44, 44)',
  
  // Layout dimensions from OCD patterns
  sidebarWidth: '250px',
  propertiesPanelWidth: '600px',
  toolbarHeight: '40px',
  tabHeight: '32px',
  
  // Flex layout patterns
  flexLayouts: {
    console: 'flex',
    consoleDirection: 'column',
    mainDirection: 'row',
    leftColumnDirection: 'column',
  },
  
  // Transition patterns
  transitions: {
    panelSlide: 'transform 0.3s ease-in-out',
    buttonHover: 'all 0.2s ease-in-out',
    tabSwitch: 'background-color 0.15s ease',
  }
};

// Oracle JET Spacing System (based on research)
const oracleSpacing = {
  '1x': '0.25rem',    // 4px
  '2x': '0.5rem',     // 8px  
  '3x': '0.75rem',    // 12px
  '4x': '1rem',       // 16px
  '5x': '1.25rem',    // 20px
  '6x': '1.5rem',     // 24px
};

// Oracle JET Border Radius System
const oracleBorderRadius = {
  sm: '0.125rem',     // 2px
  md: '0.375rem',     // 6px
  lg: '0.5rem',       // 8px
  xl: '0.75rem',      // 12px
  '2xl': '1rem',      // 16px
};

// Oracle JET Box Shadow System
const oracleBoxShadows = {
  xs: '0px 1px 4px 0px rgba(0, 0, 0, 0.12)',
  sm: '0px 4px 8px 0px rgba(0, 0, 0, 0.16)', 
  md: '0px 6px 12px 0px rgba(0, 0, 0, 0.2)',
  lg: '0px 8px 16px 0px rgba(0, 0, 0, 0.24)',
  xl: '0px 12px 24px 0px rgba(0, 0, 0, 0.28)',
};

// Oracle-inspired Material-UI Theme with OCI Designer Toolkit enhancements
export const oracleRedwoodTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: `rgb(${oracleColorPalette.brand.rgb110})`,
      light: `rgb(${oracleColorPalette.brand.rgb70})`,
      dark: `rgb(${oracleColorPalette.brand.rgb130})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    secondary: {
      main: `rgb(${oracleColorPalette.brand.rgb100})`,
      light: `rgb(${oracleColorPalette.brand.rgb80})`,
      dark: `rgb(${oracleColorPalette.brand.rgb140})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    error: {
      main: `rgb(${oracleColorPalette.danger.rgb70})`,
      light: `rgb(${oracleColorPalette.danger.rgb90})`,
      dark: `rgb(${oracleColorPalette.danger.rgb120})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    warning: {
      main: `rgb(${oracleColorPalette.warning.rgb70})`,
      light: `rgb(${oracleColorPalette.warning.rgb90})`,
      dark: `rgb(${oracleColorPalette.warning.rgb120})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb190})`,
    },
    info: {
      main: `rgb(${oracleColorPalette.info.rgb80})`,
      light: `rgb(${oracleColorPalette.info.rgb90})`,
      dark: `rgb(${oracleColorPalette.info.rgb120})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    success: {
      main: `rgb(${oracleColorPalette.success.rgb70})`,
      light: `rgb(${oracleColorPalette.success.rgb90})`,
      dark: `rgb(${oracleColorPalette.success.rgb120})`,
      contrastText: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    background: {
      default: `rgb(${oracleColorPalette.neutral.rgb10})`,
      paper: `rgb(${oracleColorPalette.neutral.rgb0})`,
    },
    text: {
      primary: `rgb(${oracleColorPalette.neutral.rgb170})`,
      secondary: `rgba(${oracleColorPalette.neutral.rgb170}, 0.7)`,
      disabled: `rgba(${oracleColorPalette.neutral.rgb170}, 0.4)`,
    },
    divider: `rgba(${oracleColorPalette.neutral.rgb170}, 0.3)`,
    action: {
      hover: `rgba(${oracleColorPalette.neutral.rgb170}, 0.08)`,
      selected: `rgba(${oracleColorPalette.brand.rgb110}, 0.16)`,
      disabled: `rgba(${oracleColorPalette.neutral.rgb170}, 0.4)`,
      disabledBackground: `rgba(${oracleColorPalette.neutral.rgb170}, 0.04)`,
    },
  },
  
  typography: {
    // Oracle typically uses clean, enterprise-grade fonts
    fontFamily: '"Oracle Sans", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
    
    // Oracle JET typography scale
    h1: {
      fontSize: '2.5rem',      // 40px
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2rem',        // 32px  
      fontWeight: 600,
      lineHeight: 1.25,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.75rem',     // 28px
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',      // 24px
      fontWeight: 600,
      lineHeight: 1.35,
    },
    h5: {
      fontSize: '1.25rem',     // 20px
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1.125rem',    // 18px
      fontWeight: 600,
      lineHeight: 1.45,
    },
    body1: {
      fontSize: '1rem',        // 16px
      lineHeight: 1.5,
      fontWeight: 400,
    },
    body2: {
      fontSize: '0.875rem',    // 14px
      lineHeight: 1.5,
      fontWeight: 400,
    },
    caption: {
      fontSize: '0.75rem',     // 12px
      lineHeight: 1.4,
      fontWeight: 400,
    },
    button: {
      fontSize: '0.875rem',    // 14px
      fontWeight: 600,
      textTransform: 'none',   // Oracle uses sentence case
      letterSpacing: '0.01em',
    },
  },
  
  spacing: (factor: number) => `${0.25 * factor}rem`, // 4px base unit
  
  shape: {
    borderRadius: 6, // Oracle JET medium border radius
  },
  
  shadows: [
    'none',
    oracleBoxShadows.xs,
    oracleBoxShadows.sm,
    oracleBoxShadows.md,
    oracleBoxShadows.lg,
    oracleBoxShadows.xl,
    // Additional shadows for Material-UI compatibility
    '0px 8px 20px 0px rgba(0, 0, 0, 0.32)',
    '0px 10px 24px 0px rgba(0, 0, 0, 0.36)',
    '0px 12px 28px 0px rgba(0, 0, 0, 0.4)',
    '0px 14px 32px 0px rgba(0, 0, 0, 0.44)',
    '0px 16px 36px 0px rgba(0, 0, 0, 0.48)',
    '0px 18px 40px 0px rgba(0, 0, 0, 0.52)',
    '0px 20px 44px 0px rgba(0, 0, 0, 0.56)',
    '0px 22px 48px 0px rgba(0, 0, 0, 0.6)',
    '0px 24px 52px 0px rgba(0, 0, 0, 0.64)',
    '0px 26px 56px 0px rgba(0, 0, 0, 0.68)',
    '0px 28px 60px 0px rgba(0, 0, 0, 0.72)',
    '0px 30px 64px 0px rgba(0, 0, 0, 0.76)',
    '0px 32px 68px 0px rgba(0, 0, 0, 0.8)',
    '0px 34px 72px 0px rgba(0, 0, 0, 0.84)',
    '0px 36px 76px 0px rgba(0, 0, 0, 0.88)',
    '0px 38px 80px 0px rgba(0, 0, 0, 0.92)',
    '0px 40px 84px 0px rgba(0, 0, 0, 0.96)',
    '0px 42px 88px 0px rgba(0, 0, 0, 1)',
    '0px 44px 92px 0px rgba(0, 0, 0, 1)',
  ],
  
  components: {
    // Enhanced with OCI Designer Toolkit CSS variables and patterns
    MuiCssBaseline: {
      styleOverrides: {
        ':root': {
          // OCI Designer Toolkit CSS Variables
          '--redwood-theme-console-background-colour': ocdThemeVariables.consoleBackground,
          '--redwood-theme-properties-panel-background-colour': ocdThemeVariables.propertiesPanelBackground,
          '--redwood-theme-active-tab-background-colour': ocdThemeVariables.activeTabBackground,
          '--redwood-theme-dialog-border-colour': ocdThemeVariables.dialogBorder,
          '--redwood-theme-dialog-highlight-colour': ocdThemeVariables.dialogHighlight,
          '--redwood-theme-toolbar-button-colour': ocdThemeVariables.toolbarButton,
          '--redwood-theme-palette-icon-colour': ocdThemeVariables.paletteIcon,
        },
        '*, *::before, *::after': {
          boxSizing: 'border-box',
        },
        html: {
          height: '100%',
        },
        body: {
          height: '100%',
          margin: 0,
          fontFamily: '"Oracle Sans", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb10})`,
        },
        '#root': {
          height: '100%',
        },
        // OCI Designer Toolkit layout classes
        '.ocd-console': {
          display: ocdThemeVariables.flexLayouts.console,
          flexDirection: ocdThemeVariables.flexLayouts.consoleDirection,
          minHeight: '100vh',
          backgroundColor: 'var(--redwood-theme-console-background-colour)',
        },
        '.ocd-console-main': {
          display: ocdThemeVariables.flexLayouts.console,
          flexDirection: ocdThemeVariables.flexLayouts.mainDirection,
          flex: 1,
          overflow: 'hidden',
        },
        '.ocd-designer-left-column': {
          display: ocdThemeVariables.flexLayouts.console,
          flexDirection: ocdThemeVariables.flexLayouts.leftColumnDirection,
          minWidth: ocdThemeVariables.sidebarWidth,
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb20})`,
        },
        '.ocd-right-side-panel': {
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: ocdThemeVariables.propertiesPanelWidth,
          minWidth: ocdThemeVariables.propertiesPanelWidth,
          backgroundColor: 'var(--redwood-theme-properties-panel-background-colour)',
          transform: 'translateX(100%)',
          transition: ocdThemeVariables.transitions.panelSlide,
          zIndex: 1000,
          overflow: 'auto',
          '&.open': {
            transform: 'translateX(0)',
          }
        },
        '.ocd-toolbar-button': {
          width: '25px',
          height: '25px',
          backgroundColor: 'var(--redwood-theme-toolbar-button-colour)',
          border: 'none',
          borderRadius: oracleBorderRadius.sm,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: ocdThemeVariables.transitions.buttonHover,
          '&:hover': {
            backgroundColor: `rgb(${oracleColorPalette.neutral.rgb30})`,
          }
        },
        '.ocd-modal-wrapper': {
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1300,
        },
        '.ocd-modal-dialog': {
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb0})`,
          borderRadius: oracleBorderRadius.lg,
          border: `2px solid var(--redwood-theme-dialog-border-colour)`,
          boxShadow: oracleBoxShadows.xl,
          maxWidth: '90vw',
          maxHeight: '90vh',
          overflow: 'auto',
        },
      },
    },
    
    // Oracle JET-inspired component overrides enhanced with OCD patterns
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: oracleBorderRadius.md,
          textTransform: 'none',
          fontWeight: 600,
          padding: `${oracleSpacing['2x']} ${oracleSpacing['4x']}`,
          minHeight: '2.75rem', // Oracle JET button height
          boxShadow: oracleBoxShadows.xs,
          transition: ocdThemeVariables.transitions.buttonHover,
          '&:hover': {
            boxShadow: oracleBoxShadows.sm,
          },
        },
        contained: {
          '&:hover': {
            boxShadow: oracleBoxShadows.md,
          },
        },
      },
    },
    
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: oracleBorderRadius.lg,
          boxShadow: oracleBoxShadows.sm,
        },
        elevation1: {
          boxShadow: oracleBoxShadows.xs,
        },
        elevation2: {
          boxShadow: oracleBoxShadows.sm,
        },
        elevation3: {
          boxShadow: oracleBoxShadows.md,
        },
      },
    },
    
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: oracleBorderRadius.lg,
          boxShadow: oracleBoxShadows.sm,
          border: `1px solid rgba(${oracleColorPalette.neutral.rgb170}, 0.1)`,
          transition: ocdThemeVariables.transitions.buttonHover,
          '&:hover': {
            boxShadow: oracleBoxShadows.md,
          },
        },
      },
    },
    
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: oracleBorderRadius.md,
            height: '2.75rem', // Oracle JET input height
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: `rgb(${oracleColorPalette.brand.rgb100})`,
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: `rgb(${oracleColorPalette.brand.rgb110})`,
              borderWidth: '2px',
            },
          },
        },
      },
    },
    
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb0})`,
          color: `rgb(${oracleColorPalette.neutral.rgb170})`,
          boxShadow: oracleBoxShadows.sm,
          borderBottom: `1px solid rgba(${oracleColorPalette.neutral.rgb170}, 0.1)`,
        },
      },
    },
    
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: `1px solid rgba(${oracleColorPalette.neutral.rgb170}, 0.1)`,
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb0})`,
        },
      },
    },
    
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: `1px solid rgba(${oracleColorPalette.neutral.rgb170}, 0.1)`,
          borderRadius: oracleBorderRadius.lg,
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: `rgba(${oracleColorPalette.neutral.rgb170}, 0.03)`,
            borderBottom: `1px solid rgba(${oracleColorPalette.neutral.rgb170}, 0.1)`,
          },
          '& .MuiDataGrid-row:hover': {
            backgroundColor: `rgba(${oracleColorPalette.brand.rgb110}, 0.08)`,
          },
        },
      },
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: oracleBorderRadius.xl,
          fontWeight: 500,
        },
      },
    },
    
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: oracleBorderRadius.xl,
          boxShadow: oracleBoxShadows.xl,
        },
      },
    },
    
    MuiTabs: {
      styleOverrides: {
        root: {
          backgroundColor: `rgb(${oracleColorPalette.neutral.rgb20})`,
          borderRadius: `${oracleBorderRadius.md} ${oracleBorderRadius.md} 0 0`,
        },
        indicator: {
          backgroundColor: `rgb(${oracleColorPalette.brand.rgb110})`,
          height: 3,
        },
      },
    },
    
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          transition: ocdThemeVariables.transitions.tabSwitch,
          '&.Mui-selected': {
            color: `rgb(${oracleColorPalette.brand.rgb110})`,
            backgroundColor: 'var(--redwood-theme-active-tab-background-colour)',
          },
        },
      },
    },
  },
} as ThemeOptions);

// Export Oracle color palette and OCD variables for use in custom components
export { oracleColorPalette, oracleSpacing, oracleBorderRadius, oracleBoxShadows, ocdThemeVariables };

// Export dark theme variant (optional)
export const oracleRedwoodDarkTheme = createTheme({
  ...oracleRedwoodTheme,
  palette: {
    ...oracleRedwoodTheme.palette,
    mode: 'dark',
    background: {
      default: `rgb(${oracleColorPalette.neutral.rgb160})`,
      paper: `rgb(${oracleColorPalette.neutral.rgb150})`,
    },
    text: {
      primary: `rgb(${oracleColorPalette.neutral.rgb20})`,
      secondary: `rgba(${oracleColorPalette.neutral.rgb20}, 0.7)`,
      disabled: `rgba(${oracleColorPalette.neutral.rgb20}, 0.4)`,
    },
  },
});
