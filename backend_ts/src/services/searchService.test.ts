import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Tavily from 'tavily'; // The actual client
import type { ProcessedSearchResult } from './searchService';

// Mock the Tavily client
vi.mock('tavily');

// Store original process.env
const originalEnv = { ...process.env };

describe('Search Service (searchService.ts)', () => {
  let mockTavilySearch: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    // Reset modules to ensure config is re-evaluated with new mocks
    vi.resetModules();

    // Mock the search method for the Tavily instance
    mockTavilySearch = vi.fn();
    (Tavily as ReturnType<typeof vi.fn>).mockImplementation(() => {
      return {
        search: mockTavilySearch,
      };
    });
  });

  afterEach(() => {
    process.env = { ...originalEnv }; // Restore original env
    vi.clearAllMocks();
  });

  it('should call Tavily search and return processed results on success', async () => {
    process.env.SEARCH_API_KEY = 'fake_tavily_key'; // Set the API key for this test
    const { searchWeb } = await import('./searchService'); // Dynamic import

    const mockTavilyResults = [
      { title: 'Test Title 1', url: 'http://example.com/1', content: 'Snippet 1', score: 0.9 },
      { title: 'Test Title 2', url: 'http://example.com/2', content: 'Snippet 2', score: 0.8 },
    ];
    mockTavilySearch.mockResolvedValue({ results: mockTavilyResults });

    const query = 'test query';
    const results: ProcessedSearchResult[] = await searchWeb(query, 2);

    expect(Tavily).toHaveBeenCalledWith('fake_tavily_key');
    expect(mockTavilySearch).toHaveBeenCalledWith(query, {
      maxResults: 2,
      includeRawContent: false,
      searchDepth: 'basic',
    });
    expect(results).toEqual([
      { title: 'Test Title 1', url: 'http://example.com/1', content: 'Snippet 1', score: 0.9 },
      { title: 'Test Title 2', url: 'http://example.com/2', content: 'Snippet 2', score: 0.8 },
    ]);
  });

  it('should return an empty array if Tavily API returns no results', async () => {
    process.env.SEARCH_API_KEY = 'fake_tavily_key';
    const { searchWeb } = await import('./searchService');

    mockTavilySearch.mockResolvedValue({ results: [] }); // Simulate no results

    const query = 'query with no results';
    const results = await searchWeb(query);

    expect(mockTavilySearch).toHaveBeenCalledWith(query, {
        maxResults: 5, // default
        includeRawContent: false,
        searchDepth: 'basic',
    });
    expect(results).toEqual([]);
  });

  it('should return an empty array if Tavily API returns null results or unexpected response', async () => {
    process.env.SEARCH_API_KEY = 'fake_tavily_key';
    const { searchWeb } = await import('./searchService');

    mockTavilySearch.mockResolvedValue(null); // Simulate null response

    const query = 'query with null results';
    const results = await searchWeb(query);
    expect(results).toEqual([]);

    mockTavilySearch.mockResolvedValue({ someOtherField: [] }); // Simulate unexpected structure
    const results2 = await searchWeb(query);
    expect(results2).toEqual([]);
  });


  it('should throw an error if Tavily API call fails', async () => {
    process.env.SEARCH_API_KEY = 'fake_tavily_key';
    const { searchWeb } = await import('./searchService');

    const apiError = new Error('Tavily API is down');
    mockTavilySearch.mockRejectedValue(apiError);

    const query = 'failing query';
    await expect(searchWeb(query)).rejects.toThrow(`Tavily API error: ${apiError.message}`);
  });

  it('should throw an error if Tavily API call fails with non-Error object', async () => {
    process.env.SEARCH_API_KEY = 'fake_tavily_key';
    const { searchWeb } = await import('./searchService');

    mockTavilySearch.mockRejectedValue("some string error"); // Simulate non-Error rejection

    const query = 'failing query with string';
    await expect(searchWeb(query)).rejects.toThrow('An unknown error occurred while searching the web.');
  });

  it('should throw an error if SEARCH_API_KEY is not configured when searchWeb is called', async () => {
    delete process.env.SEARCH_API_KEY; // Ensure key is not set

    // Dynamically import searchService AFTER updating env var and resetting modules
    // The tavilyClient instance is created at the module level based on initial config.
    vi.resetModules();
    // We need to re-evaluate the module for the tavilyClient to be null
    const { searchWeb: searchWebNewInstance } = await import('./searchService');

    const query = 'test query';
    await expect(searchWebNewInstance(query)).rejects.toThrow(
      'Search service is unavailable: Tavily API key not configured.'
    );
  });
});
