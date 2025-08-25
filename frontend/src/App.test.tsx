import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

test('renders Oatie AI header', () => {
  render(<AppWithRouter />);
  const headerElement = screen.getByText(/Oatie/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders welcome message', () => {
  render(<AppWithRouter />);
  const welcomeElement = screen.getByText(/Welcome to Oatie AI Reporting/i);
  expect(welcomeElement).toBeInTheDocument();
});

test('renders navigation links', () => {
  render(<AppWithRouter />);
  const dashboardLink = screen.getByText(/Dashboard/i);
  const reportsLink = screen.getByText(/Reports/i);
  const aiAssistantLink = screen.getByText(/AI Assistant/i);
  
  expect(dashboardLink).toBeInTheDocument();
  expect(reportsLink).toBeInTheDocument();
  expect(aiAssistantLink).toBeInTheDocument();
});