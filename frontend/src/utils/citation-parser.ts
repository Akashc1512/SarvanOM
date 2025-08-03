/**
 * Parse inline citations in the format [n] and convert them to clickable links
 * @param text - The text containing citations
 * @param sources - Array of sources to link citations to
 * @returns HTML string with parsed citations
 */
export function parseCitations(text: string, sources: any[] = []): string {
  if (!text) return "";
  
  // Replace [n] citations with clickable links
  return text.replace(/\[(\d+)\]/g, (match, number) => {
    const index = parseInt(number) - 1; // Convert to 0-based index
    const source = sources[index];
    
    if (source && source.url) {
      return `<a href="${source.url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 hover:underline font-medium">[${number}]</a>`;
    }
    
    // If no source found, just return the citation number
    return `<span class="text-gray-500 font-medium">[${number}]</span>`;
  });
}

/**
 * Extract citation numbers from text
 * @param text - The text to extract citations from
 * @returns Array of citation numbers
 */
export function extractCitations(text: string): number[] {
  if (!text) return [];
  
  const citations: number[] = [];
  const regex = /\[(\d+)\]/g;
  let match;
  
  while ((match = regex.exec(text)) !== null) {
    if (match[1]) {
      citations.push(parseInt(match[1]));
    }
  }
  
  return [...new Set(citations)]; // Remove duplicates
} 