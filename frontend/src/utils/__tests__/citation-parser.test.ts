import { parseCitations, extractCitations } from '../citation-parser';

describe('Citation Parser', () => {
  const mockSources = [
    { url: 'https://example.com/1', title: 'Source 1' },
    { url: 'https://example.com/2', title: 'Source 2' },
    { url: 'https://example.com/3', title: 'Source 3' },
  ];

  describe('parseCitations', () => {
    it('should parse citations and convert them to clickable links', () => {
      const text = 'This is a test with citations [1] and [2].';
      const result = parseCitations(text, mockSources);
      
      expect(result).toContain('<a href="https://example.com/1"');
      expect(result).toContain('<a href="https://example.com/2"');
      expect(result).toContain('target="_blank"');
      expect(result).toContain('rel="noopener noreferrer"');
    });

    it('should handle citations without corresponding sources', () => {
      const text = 'This has citations [1], [2], and [5].';
      const result = parseCitations(text, mockSources);
      
      expect(result).toContain('<a href="https://example.com/1"');
      expect(result).toContain('<a href="https://example.com/2"');
      expect(result).toContain('<span class="text-gray-500 font-medium">[5]</span>');
    });

    it('should return empty string for null/undefined text', () => {
      expect(parseCitations('')).toBe('');
      expect(parseCitations(null as any)).toBe('');
      expect(parseCitations(undefined as any)).toBe('');
    });

    it('should handle text without citations', () => {
      const text = 'This text has no citations.';
      const result = parseCitations(text, mockSources);
      
      expect(result).toBe(text);
    });
  });

  describe('extractCitations', () => {
    it('should extract citation numbers from text', () => {
      const text = 'This has citations [1], [2], and [3].';
      const result = extractCitations(text);
      
      expect(result).toEqual([1, 2, 3]);
    });

    it('should remove duplicate citations', () => {
      const text = 'This has citations [1], [2], [1], and [3].';
      const result = extractCitations(text);
      
      expect(result).toEqual([1, 2, 3]);
    });

    it('should return empty array for text without citations', () => {
      const text = 'This text has no citations.';
      const result = extractCitations(text);
      
      expect(result).toEqual([]);
    });

    it('should handle empty or null text', () => {
      expect(extractCitations('')).toEqual([]);
      expect(extractCitations(null as any)).toEqual([]);
      expect(extractCitations(undefined as any)).toEqual([]);
    });
  });
}); 