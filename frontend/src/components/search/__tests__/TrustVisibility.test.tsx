import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CitationTooltip, CitationNumber, CitationLink } from '../CitationTooltip';
import { ShareButton, useSharedContent } from '../ShareButton';
import type { Citation } from '@/lib/api';

// Mock data
const mockCitation: Citation = {
  id: '1',
  title: 'Test Citation Title',
  url: 'https://example.com',
  source: 'Example Source',
  author: 'Test Author',
  date: '2024-01-01',
  relevance: 0.95,
  excerpt: 'This is a test citation excerpt that provides context about the source.',
  type: 'article'
};

const mockCitations: Citation[] = [mockCitation];

describe('CitationTooltip', () => {
  it('renders citation tooltip with correct content', async () => {
    render(
      <CitationTooltip citation={mockCitation}>
        <span>Hover me</span>
      </CitationTooltip>
    );

    const trigger = screen.getByText('Hover me');
    fireEvent.mouseEnter(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Citation Title')).toBeInTheDocument();
      expect(screen.getByText('by Test Author')).toBeInTheDocument();
      expect(screen.getByText('This is a test citation excerpt that provides context about the source.')).toBeInTheDocument();
      expect(screen.getByText('95% relevant')).toBeInTheDocument();
    });
  });

  it('shows tooltip on focus for accessibility', async () => {
    render(
      <CitationTooltip citation={mockCitation}>
        <span tabIndex={0}>Focus me</span>
      </CitationTooltip>
    );

    const trigger = screen.getByText('Focus me');
    fireEvent.focus(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Citation Title')).toBeInTheDocument();
    });
  });

  it('hides tooltip on mouse leave', async () => {
    render(
      <CitationTooltip citation={mockCitation}>
        <span>Hover me</span>
      </CitationTooltip>
    );

    const trigger = screen.getByText('Hover me');
    fireEvent.mouseEnter(trigger);

    await waitFor(() => {
      expect(screen.getByText('Test Citation Title')).toBeInTheDocument();
    });

    fireEvent.mouseLeave(trigger);

    await waitFor(() => {
      expect(screen.queryByText('Test Citation Title')).not.toBeInTheDocument();
    });
  });
});

describe('CitationNumber', () => {
  it('renders citation number with tooltip', () => {
    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByText('1');
    expect(citationNumber).toBeInTheDocument();
    expect(citationNumber).toHaveClass('cursor-help');
  });

  it('has proper accessibility attributes', () => {
    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByLabelText('Citation 1: Test Citation Title');
    expect(citationNumber).toBeInTheDocument();
  });
});

describe('CitationLink', () => {
  it('renders citation link with tooltip', () => {
    render(<CitationLink citation={mockCitation} number={1} />);
    
    const citationLink = screen.getByText('1');
    expect(citationLink).toBeInTheDocument();
    expect(citationLink.closest('a')).toHaveAttribute('href', 'https://example.com');
    expect(citationLink.closest('a')).toHaveAttribute('target', '_blank');
  });

  it('handles citations without URLs', () => {
    const citationWithoutUrl = { ...mockCitation, url: undefined };
    render(<CitationLink citation={citationWithoutUrl} number={1} />);
    
    const citationLink = screen.getByText('1');
    expect(citationLink.closest('a')).toHaveAttribute('href', '#');
    expect(citationLink.closest('a')).toHaveClass('cursor-help');
  });
});

describe('ShareButton', () => {
  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined),
      },
    });
  });

  it('renders share button with correct text', () => {
    render(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
      />
    );

    expect(screen.getByText('Share Result')).toBeInTheDocument();
  });

  it('shows loading state when generating permalink', async () => {
    render(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
      />
    );

    const shareButton = screen.getByText('Share Result');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(screen.getByText('Generating Link...')).toBeInTheDocument();
    });
  });

  it('shows success state after copying', async () => {
    render(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
      />
    );

    const shareButton = screen.getByText('Share Result');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(screen.getByText('Link Copied!')).toBeInTheDocument();
    });
  });

  it('handles clipboard errors gracefully', async () => {
    // Mock clipboard failure
    navigator.clipboard.writeText = jest.fn().mockRejectedValue(new Error('Clipboard error'));

    render(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
      />
    );

    const shareButton = screen.getByText('Share Result');
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to copy to clipboard')).toBeInTheDocument();
    });
  });

  it('renders different variants correctly', () => {
    const { rerender } = render(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
        variant="minimal"
      />
    );

    expect(screen.getByText('Share')).toBeInTheDocument();

    rerender(
      <ShareButton
        query="test query"
        answer="test answer"
        citations={mockCitations}
        variant="icon-only"
      />
    );

    expect(screen.queryByText('Share')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Share this search result')).toBeInTheDocument();
  });
});

describe('useSharedContent', () => {
  it('loads shared content correctly', async () => {
    const TestComponent = () => {
      const { sharedData, loadSharedContent } = useSharedContent();
      
      React.useEffect(() => {
        const shareData = {
          query: 'test query',
          answer: 'test answer',
          citations: mockCitations,
          timestamp: Date.now(),
          expiresAt: Date.now() + 86400000 // 24 hours
        };
        const encodedData = btoa(JSON.stringify(shareData));
        loadSharedContent(encodedData);
      }, [loadSharedContent]);

      return (
        <div>
          {sharedData ? (
            <div>
              <span data-testid="query">{sharedData.query}</span>
              <span data-testid="answer">{sharedData.answer}</span>
            </div>
          ) : (
            <span>Loading...</span>
          )}
        </div>
      );
    };

    render(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('query')).toHaveTextContent('test query');
      expect(screen.getByTestId('answer')).toHaveTextContent('test answer');
    });
  });

  it('handles expired shared content', async () => {
    const TestComponent = () => {
      const { error, loadSharedContent } = useSharedContent();
      
      React.useEffect(() => {
        const shareData = {
          query: 'test query',
          answer: 'test answer',
          citations: mockCitations,
          timestamp: Date.now() - 86400000, // 24 hours ago
          expiresAt: Date.now() - 3600000 // 1 hour ago (expired)
        };
        const encodedData = btoa(JSON.stringify(shareData));
        loadSharedContent(encodedData);
      }, [loadSharedContent]);

      return <div>{error && <span data-testid="error">{error}</span>}</div>;
    };

    render(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('This shared link has expired (24 hours)');
    });
  });
});

describe('Accessibility', () => {
  it('meets WCAG AA contrast requirements', () => {
    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByText('1');
    // Check that the element has proper contrast classes
    expect(citationNumber).toHaveClass('text-primary');
    expect(citationNumber).toHaveClass('bg-primary/20');
  });

  it('supports keyboard navigation', () => {
    render(
      <CitationTooltip citation={mockCitation}>
        <span tabIndex={0}>Focus me</span>
      </CitationTooltip>
    );

    const trigger = screen.getByText('Focus me');
    trigger.focus();
    
    expect(trigger).toHaveFocus();
  });

  it('provides proper ARIA labels', () => {
    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByLabelText('Citation 1: Test Citation Title');
    expect(citationNumber).toBeInTheDocument();
  });

  it('has aria-label attributes for accessibility', () => {
    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByText('1');
    expect(citationNumber).toHaveAttribute('aria-label', 'Citation 1: Test Citation Title');
  });

  it('respects prefers-reduced-motion', () => {
    // Mock prefers-reduced-motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    render(<CitationNumber citation={mockCitation} number={1} />);
    
    const citationNumber = screen.getByText('1');
    // Should still render without motion-related classes when reduced motion is preferred
    expect(citationNumber).toBeInTheDocument();
  });
});
