import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as ai from 'ai'; // To mock generateText
import * as prompts from '../prompts'; // To spyOn prompt functions
import * as searchService from './searchService'; // To mock searchWeb
import { SearchQueryListSchema, ReflectionSchema } from '../types/schemas';
import type { ProcessedSearchResult } from './searchService';
import type { Source } from '../types/agentState';

// Mock the 'ai' module, specifically generateText
vi.mock('ai', async (importOriginal) => {
  const actual = await importOriginal<typeof ai>();
  return {
    ...actual,
    generateText: vi.fn(),
  };
});

// Mock searchService
vi.mock('./searchService', async (importOriginal) => {
    const actual = await importOriginal<typeof searchService>();
    return {
        ...actual,
        searchWeb: vi.fn(),
    };
});


// Cast the mock to the correct type for easier use
const mockGenerateText = ai.generateText as ReturnType<typeof vi.fn>;
const mockSearchWeb = searchService.searchWeb as ReturnType<typeof vi.fn>;

// Dynamically import agentSteps AFTER mocks are set up
const agentSteps = await import('./agentSteps');

describe('Agent Steps (services/agentSteps.ts)', () => {
  beforeEach(() => {
    vi.resetAllMocks(); // Reset all mocks before each test
  });

  describe('generateSearchQueries', () => {
    it('should return valid SearchQueryList on successful LLM call and validation', async () => {
      const mockResponse = {
        query: ['query1', 'query2'],
        rationale: 'Test rationale',
      };
      mockGenerateText.mockResolvedValue({ text: JSON.stringify(mockResponse) });

      const result = await agentSteps.generateSearchQueries('test question', 2);
      expect(mockGenerateText).toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });

    it('should extract JSON from markdown block', async () => {
      const mockResponse = { query: ['q1'], rationale: 'r1' };
      const textResponse = "Some leading text\n```json\n" + JSON.stringify(mockResponse) + "\n```\nTrailing text";
      mockGenerateText.mockResolvedValue({ text: textResponse });

      const result = await agentSteps.generateSearchQueries('test', 1);
      expect(result).toEqual(mockResponse);
    });

    it('should throw error if LLM returns invalid JSON', async () => {
      mockGenerateText.mockResolvedValue({ text: 'this is not json' });
      await expect(agentSteps.generateSearchQueries('test question', 1)).rejects.toThrow(/LLM did not return a parsable JSON object|Failed to parse LLM response as JSON/);
    });

    it('should throw error if LLM returns JSON not matching schema', async () => {
      const invalidResponse = { query: ['query1'], wrong_field: 'oops' }; // Missing rationale
      mockGenerateText.mockResolvedValue({ text: JSON.stringify(invalidResponse) });
      await expect(agentSteps.generateSearchQueries('test question', 1)).rejects.toThrow(/LLM output failed validation/);
    });
  });

  describe('extractAndSummarizeSearchResults', () => {
    const mockSearchResults: ProcessedSearchResult[] = [
      { title: 'Result 1', url: 'http://r1.com', content: 'Content for result 1', score: 1 },
      { title: 'Result 2', url: 'http://r2.com', content: 'Content for result 2', score: 0.9 },
      { title: 'Result 3', url: 'http://r3.com', content: '', score: 0.8 }, // Empty content
    ];

    it('should summarize content and return summaries and sources', async () => {
      mockGenerateText
        .mockResolvedValueOnce({ text: 'Summary for result 1' })
        .mockResolvedValueOnce({ text: 'Summary for result 2' });

      const { summaries, processedSources } = await agentSteps.extractAndSummarizeSearchResults(
        'test query',
        mockSearchResults,
        2 // Process only top 2
      );

      expect(mockGenerateText).toHaveBeenCalledTimes(2); // Called for R1, R2 (R3 skipped due to limit)
      expect(summaries).toEqual(['Summary for result 1', 'Summary for result 2']);
      expect(processedSources).toHaveLength(2);
      expect(processedSources[0]).toEqual(expect.objectContaining({ title: 'Result 1', snippet: 'Content for result 1' }));
      expect(processedSources[1]).toEqual(expect.objectContaining({ title: 'Result 2', snippet: 'Content for result 2' }));
    });

    it('should skip results with empty content', async () => {
      const singleResultWithEmptyContent: ProcessedSearchResult[] = [
         { title: 'Result 3', url: 'http://r3.com', content: '', score: 0.8 },
      ];
      mockGenerateText.mockResolvedValue({ text: 'Should not be called' });

      const { summaries, processedSources } = await agentSteps.extractAndSummarizeSearchResults(
        'test query',
        singleResultWithEmptyContent,
        1
      );
      expect(mockGenerateText).not.toHaveBeenCalled();
      expect(summaries).toEqual([]);
      expect(processedSources).toEqual([]);
    });

    it('should handle LLM summarization failure gracefully for one item', async () => {
      mockGenerateText
        .mockResolvedValueOnce({ text: 'Summary for R1' })
        .mockRejectedValueOnce(new Error('LLM failed for R2'))
        .mockResolvedValueOnce({ text: 'Summary for R3 (actually R2 due to slice)' }); // if mockSearchResults has 3 items and we process 3

      const threeResults: ProcessedSearchResult[] = [
        { title: 'R1', url: 'u1', content: 'c1' },
        { title: 'R2', url: 'u2', content: 'c2' },
        { title: 'R3', url: 'u3', content: 'c3' },
      ];
      const { summaries, processedSources } = await agentSteps.extractAndSummarizeSearchResults('test', threeResults, 3);

      expect(mockGenerateText).toHaveBeenCalledTimes(3);
      expect(summaries).toEqual(['Summary for R1', 'Summary for R3 (actually R2 due to slice)']); // R2 summary failed
      expect(processedSources).toHaveLength(2);
      expect(processedSources.find(s => s.url === 'u2')).toBeUndefined();
    });
  });

  describe('performReflection', () => {
    it('should return valid Reflection on successful LLM call and validation', async () => {
      const mockResponse = {
        is_sufficient: true,
        knowledge_gap: 'None',
        follow_up_queries: [],
      };
      mockGenerateText.mockResolvedValue({ text: JSON.stringify(mockResponse) });

      const result = await agentSteps.performReflection('test topic', ['summary1']);
      expect(mockGenerateText).toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });

    it('should extract JSON from markdown block for reflection', async () => {
      const mockResponse = { is_sufficient: false, knowledge_gap: 'More needed', follow_up_queries: ['q1'] };
      const textResponse = "```json\n" + JSON.stringify(mockResponse) + "\n```";
      mockGenerateText.mockResolvedValue({ text: textResponse });

      const result = await agentSteps.performReflection('test', ['s1']);
      expect(result).toEqual(mockResponse);
    });

    it('should throw error if LLM returns invalid JSON for reflection', async () => {
      mockGenerateText.mockResolvedValue({ text: 'not json at all' });
      await expect(agentSteps.performReflection('test topic', ['s1'])).rejects.toThrow(/LLM did not return a parsable JSON object|Failed to parse Reflection LLM response as JSON/);
    });

    it('should throw error if LLM returns JSON not matching ReflectionSchema', async () => {
      const invalidResponse = { is_sufficient: true, wrong_field: 'oops' }; // Missing fields
      mockGenerateText.mockResolvedValue({ text: JSON.stringify(invalidResponse) });
      await expect(agentSteps.performReflection('test topic', ['s1'])).rejects.toThrow(/Reflection LLM output failed validation/);
    });
  });

  describe('generateFinalAnswer', () => {
    const mockSources: Source[] = [{ title: 'Src1', url: 'u1', snippet: 'snip1' }];

    it('should return final answer from LLM', async () => {
      const finalAnswerText = 'This is the final answer.';
      mockGenerateText.mockResolvedValue({ text: finalAnswerText });

      const result = await agentSteps.generateFinalAnswer('test topic', ['summary1'], mockSources);
      expect(mockGenerateText).toHaveBeenCalled();
      expect(result.finalAnswer).toBe(finalAnswerText);
      expect(result.finalSources).toEqual(mockSources); // Simple pass-through for now
    });

    it('should throw error if LLM returns empty answer', async () => {
      mockGenerateText.mockResolvedValue({ text: '  ' }); // Empty or whitespace
      await expect(agentSteps.generateFinalAnswer('test topic', ['s1'], mockSources)).rejects.toThrow('LLM generated an empty answer.');
    });

    it('should ensure unique sources are returned', async () => {
      const duplicateSources: Source[] = [
        { title: 'Src1', url: 'u1', snippet: 's1'},
        { title: 'Src1 Dupe', url: 'u1', snippet: 's1_dupe'}, // Same URL
        { title: 'Src2', url: 'u2', snippet: 's2'}
      ];
      const expectedUniqueSources: Source[] = [
        { title: 'Src1', url: 'u1', snippet: 's1'},
        { title: 'Src2', url: 'u2', snippet: 's2'}
      ];
      mockGenerateText.mockResolvedValue({ text: "Final Answer" });

      const result = await agentSteps.generateFinalAnswer('test topic', ['s1'], duplicateSources);
      expect(result.finalSources).toHaveLength(2);
      expect(result.finalSources).toEqual(expect.arrayContaining(expectedUniqueSources));
    });
  });
});
