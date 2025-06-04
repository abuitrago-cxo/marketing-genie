import { describe, it, expect, vi } from 'vitest';
import {
  getCurrentDate,
  getQueryWriterInstructions,
  getWebSearcherInstructions,
  getReflectionInstructions,
  getAnswerInstructions,
} from './index'; // Assuming index.ts is in the same directory or path is adjusted

describe('Prompt Generation Module (prompts/index.ts)', () => {
  describe('getCurrentDate', () => {
    it('should return the current date in "Month Day, Year" format', () => {
      // Mock Date object for consistent testing
      const specificDate = new Date(2024, 6, 22); // July 22, 2024 (month is 0-indexed)
      vi.setSystemTime(specificDate);

      const dateString = getCurrentDate();
      expect(dateString).toBe('July 22, 2024');

      vi.useRealTimers(); // Restore real timers
    });

    it('should match a regex for "Month Day, Year" format', () => {
        const dateString = getCurrentDate();
        // Regex to match: Month name, one or two digits for day, and four digits for year
        expect(dateString).toMatch(/^[A-Za-z]+ \d{1,2}, \d{4}$/);
    });
  });

  describe('getQueryWriterInstructions', () => {
    it('should include research_topic, number_queries, and current_date in the prompt', () => {
      const params = {
        research_topic: 'AI impact on healthcare',
        number_queries: 3,
        current_date: 'July 22, 2024',
      };
      const prompt = getQueryWriterInstructions(params);
      expect(prompt).toContain(params.research_topic);
      expect(prompt).toContain(params.number_queries.toString()); // Ensure it's mentioned
      expect(prompt).toContain(params.current_date);
      expect(prompt).toContain('"rationale":');
      expect(prompt).toContain('"query": [');
    });
  });

  describe('getWebSearcherInstructions', () => {
    it('should include query, content, and current_date in the prompt', () => {
      const params = {
        query: 'What is photosynthesis?',
        content: 'Photosynthesis is a process used by plants...',
        current_date: 'July 22, 2024',
      };
      const prompt = getWebSearcherInstructions(params);
      expect(prompt).toContain(params.query);
      expect(prompt).toContain(params.content);
      expect(prompt).toContain(params.current_date);
      expect(prompt).toContain("Summarize the relevant information");
    });
  });

  describe('getReflectionInstructions', () => {
    it('should include research_topic, summaries, and current_date in the prompt', () => {
      const params = {
        research_topic: 'Renewable energy challenges',
        summaries: ['Summary 1 about solar costs.', 'Summary 2 about wind intermittency.'],
        current_date: 'July 22, 2024',
      };
      const prompt = getReflectionInstructions(params);
      expect(prompt).toContain(params.research_topic);
      params.summaries.forEach(summary => {
        expect(prompt).toContain(summary);
      });
      expect(prompt).toContain(params.current_date);
      expect(prompt).toContain('"is_sufficient": boolean');
      expect(prompt).toContain('"knowledge_gap":');
      expect(prompt).toContain('"follow_up_queries": [');
    });
  });

  describe('getAnswerInstructions', () => {
    it('should include research_topic, summaries, sources, and current_date in the prompt', () => {
      const params = {
        research_topic: 'Benefits of remote work',
        summaries: ['Summary A about productivity.', 'Summary B about work-life balance.'],
        sources: [
          { title: 'Source A', url: 'http://example.com/a' },
          { title: 'Source B', url: 'http://example.com/b' },
        ],
        current_date: 'July 22, 2024',
      };
      const prompt = getAnswerInstructions(params);
      expect(prompt).toContain(params.research_topic);
      params.summaries.forEach(summary => {
        expect(prompt).toContain(summary);
      });
      params.sources.forEach(source => {
        expect(prompt).toContain(source.title);
        expect(prompt).toContain(source.url);
      });
      expect(prompt).toContain(params.current_date);
      expect(prompt).toContain("synthesize the provided research summaries");
      expect(prompt).toContain("Cite Sources");
    });
  });
});
