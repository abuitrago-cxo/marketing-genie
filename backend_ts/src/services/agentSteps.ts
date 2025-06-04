import { generateText, streamText, LanguageModel } from 'ai';
import { createOpenRouter } from '@ai-sdk/openrouter'; // Corrected import based on typical @ai-sdk structure
import config from '../config';
import { getQueryWriterInstructions, getCurrentDate, getWebSearcherInstructions, getReflectionInstructions, getAnswerInstructions } from '../prompts';
import { SearchQueryListSchema, SearchQueryList, ReflectionSchema, Reflection } from '../types/schemas';
import { z } from 'zod';
import { ProcessedSearchResult } from './searchService'; // Assuming searchService.ts is in the same directory
import { Source } from '../types/agentState'; // For processedSources output

// Initialize the OpenRouter provider
// Note: The actual provider creation might vary slightly based on specific @ai-sdk/openrouter version
const openRouterProvider = createOpenRouter({
  apiKey: config.openRouterApiKey,
});

// Get the specific models
const queryGenerationModel = openRouterProvider.chat(config.queryGeneratorModel);
const webSearcherModel = openRouterProvider.chat(config.webSearcherModel);
const reflectionModel = openRouterProvider.chat(config.reflectionModel);
const answerModel = openRouterProvider.chat(config.answerModel);

/**
 * Generates search queries based on a user question using an LLM.
 * @param userQuestion The user's research question.
 * @param numberOfQueries The number of search queries to generate.
 * @returns A promise that resolves to a validated SearchQueryList object.
 * @throws Error if LLM call, JSON parsing, or Zod validation fails.
 */
export const generateSearchQueries = async (
  userQuestion: string,
  numberOfQueries: number
): Promise<SearchQueryList> => {
  const currentDate = getCurrentDate();
  const promptContent = getQueryWriterInstructions({
    research_topic: userQuestion,
    number_queries: numberOfQueries,
    current_date: currentDate,
  });

  // System prompt to guide the LLM for JSON output, though our main prompt already specifies it.
  // This can be helpful for models that strictly need a system role for such instructions.
  const systemPrompt = `You are an expert research assistant. Your task is to generate a JSON object containing a list of search queries and a rationale, according to the user's request and the provided schema. Ensure your output is a single, valid JSON object. The user's request will ask for a specific number of queries.`;

  try {
    const { text, toolCalls, toolResults, finishReason, usage, rawResponse, ...rest } = await generateText({
      model: queryGenerationModel,
      // Some models work better with system prompts, others with just user/assistant roles.
      // The prompt template itself is written as a user request to the LLM.
      system: systemPrompt, // Add system prompt for models that support it well
      prompt: promptContent,
      // The Vercel AI SDK has experimental support for structured output using Zod schemas
      // with certain providers/models. If OpenRouter models support it directly via `mode: 'json'`,
      // that would be ideal. Otherwise, we rely on prompt engineering and manual parsing.
      // For now, we'll parse manually as robust JSON mode isn't universally guaranteed.
      // experimental_mode: 'json',
      // experimental_schema: SearchQueryListSchema
    });

    // Attempt to find a valid JSON block in the response, as LLMs can sometimes add extra text.
    let jsonString = text;
    const jsonRegex = /```json\n([\s\S]*?)\n```|({[\s\S]*})/; // Look for markdown code block or raw object
    const match = jsonRegex.exec(text);
    if (match && match[1]) {
      jsonString = match[1]; // Content of ```json ... ```
    } else if (match && match[2]) {
      jsonString = match[2]; // Content of { ... }
    } else {
        // If no clear JSON block, try to parse the whole text, but trim it first.
        jsonString = text.trim();
        if (!jsonString.startsWith('{') || !jsonString.endsWith('}')) {
            console.warn("LLM output does not appear to be a JSON object:", text);
            // Potentially try to extract JSON from within the string if it's embedded
            const startIndex = jsonString.indexOf('{');
            const endIndex = jsonString.lastIndexOf('}');
            if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
                jsonString = jsonString.substring(startIndex, endIndex + 1);
            } else {
                throw new Error("LLM did not return a parsable JSON object. Raw output: " + text);
            }
        }
    }

    let parsedJson: any;
    try {
      parsedJson = JSON.parse(jsonString);
    } catch (jsonError) {
      console.error("Failed to parse LLM response as JSON:", jsonError);
      console.error("Raw LLM Text:", text);
      console.error("Attempted JSON String:", jsonString);
      throw new Error(`Failed to parse LLM response as JSON. Details: ${(jsonError as Error).message}. Raw output: ${text.substring(0, 200)}...`);
    }

    const validationResult = SearchQueryListSchema.safeParse(parsedJson);

    if (!validationResult.success) {
      console.error("Failed to validate JSON against SearchQueryListSchema:", validationResult.error.errors);
      console.error("Parsed JSON that failed validation:", parsedJson);
      throw new Error(`LLM output failed validation: ${validationResult.error.message}. Parsed data: ${JSON.stringify(parsedJson)}`);
    }

    return validationResult.data;

  } catch (error) {
    console.error("Error generating search queries:", error);
    if (error instanceof Error) {
        throw new Error(`Error in generateSearchQueries: ${error.message}`);
    }
    throw new Error("An unknown error occurred while generating search queries.");
  }
};

interface SummarizationResult {
  summaries: string[];
  processedSources: Source[];
}

/**
 * Extracts relevant content from search results and generates summaries using an LLM.
 * @param searchQuery The original search query that yielded these results.
 * @param results An array of ProcessedSearchResult from the searchWeb function.
 * @param maxResultsToProcess Optional limit on how many search results to process (e.g., top 3-5).
 * @returns A promise that resolves to an object containing an array of summaries and an array of processed Source objects.
 */
export const extractAndSummarizeSearchResults = async (
  searchQuery: string,
  results: ProcessedSearchResult[],
  maxResultsToProcess: number = 3 // Default to processing top 3 results
): Promise<SummarizationResult> => {
  const summaries: string[] = [];
  const processedSources: Source[] = [];
  const currentDate = getCurrentDate();

  // Limit the number of results to process to manage costs and time
  const resultsToProcess = results.slice(0, maxResultsToProcess);

  for (const result of resultsToProcess) {
    // Ensure there's content to summarize
    if (!result.content || result.content.trim() === "") {
      console.warn(`Skipping result with empty content for URL: ${result.url}`);
      continue;
    }

    const promptContent = getWebSearcherInstructions({
      query: searchQuery,
      content: result.content, // This is the snippet/summary from Tavily
      current_date: currentDate,
    });

    try {
      const { text: summaryText } = await generateText({
        model: webSearcherModel, // Using the dedicated webSearcherModel
        prompt: promptContent,
        // System prompt can be added if beneficial for this model/task
        // system: "You are an AI assistant that summarizes provided text based on a query.",
      });

      if (summaryText && summaryText.trim() !== "" && summaryText.trim() !== "The provided content does not answer the query.") {
        summaries.push(summaryText.trim());
        processedSources.push({
          title: result.title,
          url: result.url,
          snippet: result.content, // The original snippet used for summarization
          // value: summaryText.trim(), // Or store the summary here if Source 'value' is for that
          // id: can be generated if needed, e.g., based on a counter or hash
        });
      } else {
        console.log(`Summary for ${result.url} was empty or indicated no answer.`);
      }
    } catch (error) {
      console.error(`Error summarizing content for URL: ${result.url} (Query: ${searchQuery})`, error);
      // Decide on error handling: skip this summary and continue, or throw
      // For now, we log and continue to gather other summaries.
      // If a certain number of errors occur, one might choose to throw.
    }
  }

  return { summaries, processedSources };
};

/**
 * Performs reflection on the gathered summaries to determine if they are sufficient
 * to answer the research topic and generates follow-up queries if needed.
 * @param researchTopic The original research topic.
 * @param summaries An array of summaries gathered so far.
 * @returns A promise that resolves to a validated Reflection object.
 * @throws Error if LLM call, JSON parsing, or Zod validation fails.
 */
export const performReflection = async (
  researchTopic: string,
  summaries: string[]
): Promise<Reflection> => {
  const currentDate = getCurrentDate();
  const promptContent = getReflectionInstructions({
    research_topic: researchTopic,
    summaries: summaries,
    current_date: currentDate,
  });

  // System prompt to reinforce JSON output, similar to query generation.
  const systemPrompt = `You are an expert research analyst. Your task is to reflect on the provided research summaries and determine if they sufficiently answer the user's topic. Output your analysis as a JSON object according to the provided schema, including whether the information is sufficient, any knowledge gaps, and follow-up questions if needed.`;

  try {
    const { text } = await generateText({
      model: reflectionModel, // Using the dedicated reflectionModel
      system: systemPrompt,
      prompt: promptContent,
    });

    // Attempt to find a valid JSON block in the response (similar to generateSearchQueries)
    let jsonString = text;
    const jsonRegex = /```json\n([\s\S]*?)\n```|({[\s\S]*})/;
    const match = jsonRegex.exec(text);
    if (match && match[1]) {
      jsonString = match[1];
    } else if (match && match[2]) {
      jsonString = match[2];
    } else {
        jsonString = text.trim();
        if (!jsonString.startsWith('{') || !jsonString.endsWith('}')) {
            console.warn("Reflection LLM output does not appear to be a JSON object:", text);
            const startIndex = jsonString.indexOf('{');
            const endIndex = jsonString.lastIndexOf('}');
            if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
                jsonString = jsonString.substring(startIndex, endIndex + 1);
            } else {
                throw new Error("Reflection LLM did not return a parsable JSON object. Raw output: " + text);
            }
        }
    }

    let parsedJson: any;
    try {
      parsedJson = JSON.parse(jsonString);
    } catch (jsonError) {
      console.error("Failed to parse Reflection LLM response as JSON:", jsonError);
      console.error("Raw Reflection LLM Text:", text);
      console.error("Attempted JSON String for Reflection:", jsonString);
      throw new Error(`Failed to parse Reflection LLM response as JSON. Details: ${(jsonError as Error).message}. Raw output: ${text.substring(0,200)}...`);
    }

    const validationResult = ReflectionSchema.safeParse(parsedJson);

    if (!validationResult.success) {
      console.error("Failed to validate JSON against ReflectionSchema:", validationResult.error.errors);
      console.error("Parsed JSON that failed reflection validation:", parsedJson);
      throw new Error(`Reflection LLM output failed validation: ${validationResult.error.message}. Parsed data: ${JSON.stringify(parsedJson)}`);
    }

    return validationResult.data;

  } catch (error) {
    console.error("Error performing reflection:", error);
    if (error instanceof Error) {
        throw new Error(`Error in performReflection: ${error.message}`);
    }
    throw new Error("An unknown error occurred while performing reflection.");
  }
};

interface FinalAnswerResult {
  finalAnswer: string;
  finalSources: Source[];
}

/**
 * Generates a final, synthesized answer based on the research topic, summaries, and sources.
 * @param researchTopic The original research topic.
 * @param summaries An array of summaries gathered and refined through the research process.
 * @param sourcesGathered An array of Source objects that contributed to the summaries.
 * @returns A promise that resolves to an object containing the final answer and the list of sources.
 * @throws Error if the LLM call fails.
 */
export const generateFinalAnswer = async (
  researchTopic: string,
  summaries: string[],
  sourcesGathered: Source[] // These are the sources that correspond to the summaries
): Promise<FinalAnswerResult> => {
  const currentDate = getCurrentDate();
  const promptContent = getAnswerInstructions({
    research_topic: researchTopic,
    summaries: summaries,
    sources: sourcesGathered, // Pass the source details for citation
    current_date: currentDate,
  });

  // A system prompt might be less critical here as the main prompt is quite detailed,
  // but can be added if the chosen answerModel benefits from it.
  // const systemPrompt = "You are a helpful AI assistant that synthesizes research into a comprehensive answer.";

  try {
    const { text: llmAnswer } = await generateText({
      model: answerModel, // Using the dedicated answerModel
      // system: systemPrompt, // Optional system prompt
      prompt: promptContent,
    });

    if (!llmAnswer || llmAnswer.trim() === "") {
      console.warn("LLM generated an empty or whitespace-only answer for topic:", researchTopic);
      throw new Error("LLM generated an empty answer.");
    }

    // For now, post-processing is minimal. The LLM is instructed to cite sources.
    // Future enhancements could involve more structured citation replacement if needed.
    // We return the unique sources that were provided to the LLM.
    const uniqueSources = Array.from(new Map(sourcesGathered.map(s => [s.url, s])).values());


    return {
      finalAnswer: llmAnswer.trim(),
      finalSources: uniqueSources,
    };

  } catch (error) {
    console.error("Error generating final answer for topic:", researchTopic, error);
    if (error instanceof Error) {
        throw new Error(`Error in generateFinalAnswer: ${error.message}`);
    }
    throw new Error("An unknown error occurred while generating the final answer.");
  }
};
