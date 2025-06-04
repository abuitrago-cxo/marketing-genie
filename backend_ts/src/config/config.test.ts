import { describe, it, expect, beforeEach, vi } from 'vitest';

// Store original process.env
const originalEnv = process.env;

describe('Configuration Module (config/index.ts)', () => {
  beforeEach(() => {
    // Reset process.env to a copy of the original before each test
    // and clear the module cache for dynamic import to reload the config.
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  it('should load config correctly when all environment variables are set', async () => {
    process.env.OPENROUTER_API_KEY = 'test_openrouter_key';
    process.env.QUERY_GENERATOR_MODEL = 'test_query_model';
    process.env.WEB_SEARCHER_MODEL = 'test_web_model';
    process.env.REFLECTION_MODEL = 'test_reflection_model';
    process.env.ANSWER_MODEL = 'test_answer_model';
    process.env.NUMBER_OF_INITIAL_QUERIES = '5';
    process.env.MAX_RESEARCH_LOOPS = '4';
    process.env.SEARCH_API_KEY = 'test_search_key';
    process.env.LOG_LEVEL = 'debug';

    const { default: config } = await import('./index');

    expect(config.openRouterApiKey).toBe('test_openrouter_key');
    expect(config.queryGeneratorModel).toBe('test_query_model');
    expect(config.webSearcherModel).toBe('test_web_model');
    expect(config.reflectionModel).toBe('test_reflection_model');
    expect(config.answerModel).toBe('test_answer_model');
    expect(config.numberOfInitialQueries).toBe(5);
    expect(config.maxResearchLoops).toBe(4);
    expect(config.searchApiKey).toBe('test_search_key');
    expect(config.logLevel).toBe('debug');
  });

  it('should throw an error if OPENROUTER_API_KEY is missing', async () => {
    delete process.env.OPENROUTER_API_KEY;
    // We expect the error to occur when the module is imported (and thus executed)
    await expect(import('./index')).rejects.toThrow(
      'Missing required environment variable: OPENROUTER_API_KEY'
    );
  });

  it('should use default values for optional variables if they are missing', async () => {
    process.env.OPENROUTER_API_KEY = 'test_openrouter_key'; // Required
    delete process.env.QUERY_GENERATOR_MODEL;
    delete process.env.WEB_SEARCHER_MODEL;
    delete process.env.REFLECTION_MODEL;
    delete process.env.ANSWER_MODEL;
    delete process.env.NUMBER_OF_INITIAL_QUERIES;
    delete process.env.MAX_RESEARCH_LOOPS;
    delete process.env.SEARCH_API_KEY;
    delete process.env.LOG_LEVEL;

    const { default: config } = await import('./index');

    expect(config.queryGeneratorModel).toBe("mistralai/mistral-7b-instruct");
    expect(config.webSearcherModel).toBe("mistralai/mistral-7b-instruct");
    expect(config.reflectionModel).toBe("mistralai/mistral-7b-instruct");
    expect(config.answerModel).toBe("openai/gpt-3.5-turbo");
    expect(config.numberOfInitialQueries).toBe(3);
    expect(config.maxResearchLoops).toBe(3);
    expect(config.searchApiKey).toBeUndefined();
    expect(config.logLevel).toBe("info");
  });

  it('should throw an error for invalid NUMBER_OF_INITIAL_QUERIES', async () => {
    process.env.OPENROUTER_API_KEY = 'test_openrouter_key';
    process.env.NUMBER_OF_INITIAL_QUERIES = 'not-a-number';

    await expect(import('./index')).rejects.toThrow(
      'Invalid value for NUMBER_OF_INITIAL_QUERIES: Must be a number.'
    );
  });

  it('should throw an error for invalid MAX_RESEARCH_LOOPS', async () => {
    process.env.OPENROUTER_API_KEY = 'test_openrouter_key';
    process.env.MAX_RESEARCH_LOOPS = 'not-a-number';

    await expect(import('./index')).rejects.toThrow(
      'Invalid value for MAX_RESEARCH_LOOPS: Must be a number.'
    );
  });

   it('should correctly parse valid string numeric values for query and loop counts', async () => {
    process.env.OPENROUTER_API_KEY = 'test_openrouter_key';
    process.env.NUMBER_OF_INITIAL_QUERIES = '7';
    process.env.MAX_RESEARCH_LOOPS = '2';

    const { default: config } = await import('./index');
    expect(config.numberOfInitialQueries).toBe(7);
    expect(config.maxResearchLoops).toBe(2);
  });
});
