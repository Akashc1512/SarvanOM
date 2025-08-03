import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AgentToolkit from '../AgentToolkit';

// Mock the API client
jest.mock('@/services/api', () => ({
  api: {
    client: {
      post: jest.fn()
    }
  }
}));

// Mock Lucide React icons
jest.mock('lucide-react', () => ({
  Search: () => <span data-testid="search-icon">🔍</span>,
  FileText: () => <span data-testid="file-icon">📄</span>,
  Code: () => <span data-testid="code-icon">💻</span>,
  Brain: () => <span data-testid="brain-icon">🧠</span>,
  Database: () => <span data-testid="database-icon">🗄️</span>,
  Globe: () => <span data-testid="globe-icon">🌐</span>,
  Loader2: () => <span data-testid="loader-icon">⏳</span>,
  CheckCircle: () => <span data-testid="success-icon">✅</span>,
  XCircle: () => <span data-testid="error-icon">❌</span>
}));

describe('AgentToolkit', () => {
  const mockAgents = [
    {
      id: 'browser',
      name: 'Web Search',
      description: 'Search the web for real-time information',
      icon: () => <span>🔍</span>,
      category: 'search' as const,
      status: 'available' as const,
      endpoint: '/api/agents/browser'
    },
    {
      id: 'pdf',
      name: 'PDF Processor',
      description: 'Upload and analyze PDF documents',
      icon: () => <span>📄</span>,
      category: 'document' as const,
      status: 'available' as const,
      endpoint: '/api/agents/pdf'
    }
  ];

  const mockOnToolSelected = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.prompt
    global.prompt = jest.fn();
    // Mock document.createElement for file input
    global.document.createElement = jest.fn(() => ({
      type: '',
      accept: '',
      onchange: null,
      click: jest.fn(),
      files: null
    })) as any;
  });

  it('renders agent toolkit with available agents', () => {
    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    expect(screen.getByText('Agent Toolkit')).toBeInTheDocument();
    expect(screen.getByText('Web Search')).toBeInTheDocument();
    expect(screen.getByText('PDF Processor')).toBeInTheDocument();
  });

  it('displays agent descriptions', () => {
    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    expect(screen.getByText('Search the web for real-time information')).toBeInTheDocument();
    expect(screen.getByText('Upload and analyze PDF documents')).toBeInTheDocument();
  });

  it('shows agent categories as badges', () => {
    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    expect(screen.getByText('search')).toBeInTheDocument();
    expect(screen.getByText('document')).toBeInTheDocument();
  });

  it('handles browser agent click', async () => {
    const mockPrompt = jest.fn().mockReturnValue('test query');
    global.prompt = mockPrompt;

    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    const browserButton = screen.getByText('Web Search').closest('button');
    expect(browserButton).toBeInTheDocument();

    fireEvent.click(browserButton!);

    expect(mockPrompt).toHaveBeenCalledWith('Enter search term:');
  });

  it('handles PDF agent click', () => {
    const mockFileInput = {
      type: 'file',
      accept: '.pdf',
      onchange: null,
      click: jest.fn(),
      files: null
    };
    (global.document.createElement as jest.Mock).mockReturnValue(mockFileInput);

    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    const pdfButton = screen.getByText('PDF Processor').closest('button');
    expect(pdfButton).toBeInTheDocument();

    fireEvent.click(pdfButton!);

    expect(mockFileInput.click).toHaveBeenCalled();
  });

  it('calls onToolSelected callback when agent is selected', async () => {
    const mockPrompt = jest.fn().mockReturnValue('test query');
    global.prompt = mockPrompt;

    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
      />
    );

    const browserButton = screen.getByText('Web Search').closest('button');
    fireEvent.click(browserButton!);

    await waitFor(() => {
      expect(mockOnToolSelected).toHaveBeenCalled();
    });
  });

  it('handles empty agent list', () => {
    render(
      <AgentToolkit
        availableAgents={[]}
        onToolSelected={mockOnToolSelected}
      />
    );

    expect(screen.getByText('Agent Toolkit')).toBeInTheDocument();
    // Should not crash with empty agents list
  });

  it('applies custom className', () => {
    render(
      <AgentToolkit
        availableAgents={mockAgents}
        onToolSelected={mockOnToolSelected}
        className="custom-class"
      />
    );

    const toolkitContainer = screen.getByText('Agent Toolkit').closest('div')?.parentElement;
    expect(toolkitContainer).toHaveClass('custom-class');
  });

  it('handles agent with error status', () => {
    const agentsWithError = [
      {
        id: 'browser',
        name: 'Web Search',
        description: 'Search the web for real-time information',
        icon: () => <span>🔍</span>,
        category: 'search' as const,
        status: 'error' as const,
        endpoint: '/api/agents/browser'
      }
    ];

    render(
      <AgentToolkit
        availableAgents={agentsWithError}
        onToolSelected={mockOnToolSelected}
      />
    );

    // Should still render the agent even with error status
    expect(screen.getByText('Web Search')).toBeInTheDocument();
  });

  it('handles agent with busy status', () => {
    const agentsWithBusy = [
      {
        id: 'browser',
        name: 'Web Search',
        description: 'Search the web for real-time information',
        icon: () => <span>🔍</span>,
        category: 'search' as const,
        status: 'busy' as const,
        endpoint: '/api/agents/browser'
      }
    ];

    render(
      <AgentToolkit
        availableAgents={agentsWithBusy}
        onToolSelected={mockOnToolSelected}
      />
    );

    // Should still render the agent even with busy status
    expect(screen.getByText('Web Search')).toBeInTheDocument();
  });
}); 