import Tavily from 'tavily';
import config from '../config'; // Ensure your config path is correct

// Define the structure for a processed search result
export interface ProcessedSearchResult {
  title: string;
  url: string;
  content: string; // Snippet or summary from Tavily
  score?: number; // Tavily provides a score
  raw_content?: string; // Optional: Tavily sometimes provides this
  // Add any other fields from Tavily's result object that might be useful
}

let tavilyClient: Tavily | null = null;

if (config.searchApiKey) {
  tavilyClient = new Tavily(config.searchApiKey);
} else {
  console.warn("Tavily Search API key is not configured. Web search functionality will be unavailable.");
}

/**
 * Performs a web search using the Tavily API.
 * @param query The search query string.
 * @param maxResults The maximum number of results to return (default: 5).
 * @returns A promise that resolves to an array of processed search results.
 * @throws Error if the Tavily API key is not configured or if the API call fails.
 */
export const searchWeb = async (
  query: string,
  maxResults: number = 5
): Promise<ProcessedSearchResult[]> => {
  if (!tavilyClient) {
    throw new Error("Search service is unavailable: Tavily API key not configured.");
  }

  try {
    // Note: Tavily's search method might have different parameters.
    // Consulting its documentation for `search(query, options)` is key.
    // Common options include 'max_results', 'include_answer', 'include_raw_content', 'search_depth'.
    const response = await tavilyClient.search(query, {
      maxResults: maxResults,
      // include_domains: [], // Example: restrict search to specific domains
      // exclude_domains: [], // Example: exclude specific domains
      includeRawContent: false, // If you want the full raw content of pages (can be large)
      searchDepth: "basic", // "basic" or "advanced" (advanced may use more credits)
    });

    if (!response || !response.results) {
      console.warn("Tavily API returned no results or an unexpected response format for query:", query);
      return [];
    }

    // Transform Tavily results into our ProcessedSearchResult format
    return response.results.map((result: any): ProcessedSearchResult => ({
      title: result.title,
      url: result.url,
      content: result.content, // This is typically the snippet or summary
      score: result.score,
      // raw_content: result.raw_content, // if requested and available
    }));

  } catch (error) {
    console.error("Error during Tavily API call for query:", query, error);
    // It's good practice to throw a custom error or re-throw,
    // depending on how you want to handle this upstream.
    if (error instanceof Error) {
        throw new Error(`Tavily API error: ${error.message}`);
    }
    throw new Error("An unknown error occurred while searching the web.");
  }
};

// Example of how to potentially fetch full content if needed,
// though Tavily's main purpose is search and curated snippets.
// This would typically involve another library or a direct HTTP fetch.
/*
export const fetchPageContent = async (url: string): Promise<string> => {
  // Implementation for fetching full page content would go here
  // e.g., using axios or node-fetch to get HTML, then a library to parse text.
  // This is outside the scope of Tavily's direct functionality.
  console.warn(`Fetching full page content for ${url} is not implemented.`);
  return "";
};
*/
