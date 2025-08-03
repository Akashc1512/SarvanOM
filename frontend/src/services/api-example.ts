import { api } from './api';

/**
 * Example usage of the enhanced submitQuery function with orchestration flags
 */

// Example 1: Basic query with default orchestration options
export async function exampleBasicQuery() {
  try {
    const response = await api.submitQuery({
      query: "Explain Knowledge Graphs",
      options: { factcheck: true, citations: true }
    });
    
    console.log('Basic query response:', response);
    return response;
  } catch (error) {
    console.error('Basic query failed:', error);
    throw error;
  }
}

// Example 2: Query with custom orchestration options
export async function exampleCustomOptions() {
  try {
    const response = await api.submitQuery({
      query: "What is Artificial Intelligence?",
      options: { 
        factcheck: false,  // Disable fact-checking
        citations: true     // Enable citations
      },
      priority: "high",
      max_tokens: 1500,
      temperature: 0.7
    });
    
    console.log('Custom options query response:', response);
    return response;
  } catch (error) {
    console.error('Custom options query failed:', error);
    throw error;
  }
}

// Example 3: Using the convenience method
export async function exampleConvenienceMethod() {
  try {
    const response = await api.submitQueryWithOptions("Explain Quantum Computing", {
      factcheck: true,
      citations: true,
      priority: "medium",
      max_tokens: 1000,
      context: "For a beginner audience"
    });
    
    console.log('Convenience method response:', response);
    return response;
  } catch (error) {
    console.error('Convenience method failed:', error);
    throw error;
  }
}

// Example 4: Query with minimal options (uses defaults)
export async function exampleMinimalOptions() {
  try {
    const response = await api.submitQuery({
      query: "What is Machine Learning?"
      // Uses default options: factcheck: true, citations: true
    });
    
    console.log('Minimal options response:', response);
    return response;
  } catch (error) {
    console.error('Minimal options query failed:', error);
    throw error;
  }
}

// Example 5: Query with only fact-checking enabled
export async function exampleFactCheckOnly() {
  try {
    const response = await api.submitQuery({
      query: "Explain the benefits of renewable energy",
      options: { 
        factcheck: true,   // Enable fact-checking
        citations: false    // Disable citations
      }
    });
    
    console.log('Fact-check only response:', response);
    return response;
  } catch (error) {
    console.error('Fact-check only query failed:', error);
    throw error;
  }
}

// Example 6: Query with only citations enabled
export async function exampleCitationsOnly() {
  try {
    const response = await api.submitQuery({
      query: "What are the latest developments in AI?",
      options: { 
        factcheck: false,  // Disable fact-checking
        citations: true     // Enable citations
      },
      priority: "low"
    });
    
    console.log('Citations only response:', response);
    return response;
  } catch (error) {
    console.error('Citations only query failed:', error);
    throw error;
  }
}

// Example 7: High-priority query with all options enabled
export async function exampleHighPriorityQuery() {
  try {
    const response = await api.submitQuery({
      query: "Critical analysis of climate change data",
      options: { 
        factcheck: true,   // Enable fact-checking
        citations: true     // Enable citations
      },
      priority: "high",
      max_tokens: 2000,
      temperature: 0.3,    // Lower temperature for more focused response
      context: "For academic research purposes"
    });
    
    console.log('High priority response:', response);
    return response;
  } catch (error) {
    console.error('High priority query failed:', error);
    throw error;
  }
}

// Export all examples for easy testing
export const examples = {
  basic: exampleBasicQuery,
  custom: exampleCustomOptions,
  convenience: exampleConvenienceMethod,
  minimal: exampleMinimalOptions,
  factCheckOnly: exampleFactCheckOnly,
  citationsOnly: exampleCitationsOnly,
  highPriority: exampleHighPriorityQuery
}; 