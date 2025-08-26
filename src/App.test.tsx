import { ThemeProvider } from '@mui/material';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';
import oracleRedwoodTheme from './theme/oracleRedwoodTheme';

describe('App', () => {
  it('renders login form initially', () => {
    render(
      <ThemeProvider theme={oracleRedwoodTheme}>
        <App />
      </ThemeProvider>
    );

    // Check if login form is rendered
    expect(screen.getByRole('heading', { name: /Oracle/i })).toBeTruthy();
    expect(screen.getByText(/Oatie AI Reporting/i)).toBeTruthy();
  });
});