import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import oracleRedwoodTheme from '../theme/oracleRedwoodTheme';
import App from '../App';

describe('App', () => {
  it('renders login form initially', () => {
    render(
      <ThemeProvider theme={oracleRedwoodTheme}>
        <App />
      </ThemeProvider>
    );
    
    // Check if login form is rendered
    expect(screen.getByText(/Oracle BI Reporting/i)).toBeInTheDocument();
  });
});