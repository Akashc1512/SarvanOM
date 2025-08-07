import React from 'react';
import { render, screen } from '@testing-library/react';
import { SarvanomLoader, SarvanomLoaderFullScreen, SarvanomLoaderInline } from '../SarvanomLoader';

describe('SarvanomLoader', () => {
  it('renders the loader with default size', () => {
    render(<SarvanomLoader />);
    const svg = screen.getByRole('img', { hidden: true });
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveAttribute('width', '120');
    expect(svg).toHaveAttribute('height', '120');
  });

  it('renders the loader with custom size', () => {
    render(<SarvanomLoader size={80} />);
    const svg = screen.getByRole('img', { hidden: true });
    expect(svg).toHaveAttribute('width', '80');
    expect(svg).toHaveAttribute('height', '80');
  });

  it('renders the loader with custom className', () => {
    render(<SarvanomLoader className="custom-class" />);
    const container = screen.getByRole('img', { hidden: true }).parentElement;
    expect(container).toHaveClass('custom-class');
  });

  it('contains the required SVG elements', () => {
    render(<SarvanomLoader />);
    const svg = screen.getByRole('img', { hidden: true });
    
    // Check for outer blue circle
    expect(svg.querySelector('circle[cx="32"][cy="32"][r="30"]')).toBeInTheDocument();
    
    // Check for center pulsing node
    expect(svg.querySelector('circle[cx="32"][cy="32"][r="2"]')).toBeInTheDocument();
    
    // Check for ellipses
    expect(svg.querySelectorAll('ellipse')).toHaveLength(3);
    
    // Check for outer nodes
    expect(svg.querySelectorAll('circle[cx="12"][cy="32"][r="3"]')).toHaveLength(1);
    expect(svg.querySelectorAll('circle[cx="32"][cy="12"][r="3"]')).toHaveLength(1);
    expect(svg.querySelectorAll('circle[cx="52"][cy="32"][r="3"]')).toHaveLength(1);
  });
});

describe('SarvanomLoaderFullScreen', () => {
  it('renders full screen loader with text', () => {
    render(<SarvanomLoaderFullScreen />);
    expect(screen.getByText('Loading SarvanOM...')).toBeInTheDocument();
  });
});

describe('SarvanomLoaderInline', () => {
  it('renders inline loader with default size', () => {
    render(<SarvanomLoaderInline />);
    const svg = screen.getByRole('img', { hidden: true });
    expect(svg).toHaveAttribute('width', '40');
    expect(svg).toHaveAttribute('height', '40');
  });

  it('renders inline loader with custom size', () => {
    render(<SarvanomLoaderInline size={60} />);
    const svg = screen.getByRole('img', { hidden: true });
    expect(svg).toHaveAttribute('width', '60');
    expect(svg).toHaveAttribute('height', '60');
  });
}); 