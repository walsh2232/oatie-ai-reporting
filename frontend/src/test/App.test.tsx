import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

import App from '../App';

describe('App Component', () => {
  it('renders the main heading', () => {
    render(<App />);
    const heading = screen.getByRole('heading', { name: /oatie ai reporting/i });
    expect(heading).toBeInTheDocument();
  });

  it('renders the welcome section', () => {
    render(<App />);
    const welcomeHeading = screen.getByRole('heading', { name: /welcome to oatie/i });
    expect(welcomeHeading).toBeInTheDocument();
  });

  it('contains proper accessibility structure', () => {
    render(<App />);
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });

  it('displays the project description', () => {
    render(<App />);
    const description = screen.getByText(/transform your fusion reporting with ai/i);
    expect(description).toBeInTheDocument();
  });
});