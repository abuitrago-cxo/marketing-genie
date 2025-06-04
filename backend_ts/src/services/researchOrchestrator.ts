import config from '../config';
import { AgentState, Message, Source } from '../types/agentState';
import { SearchQueryList, Reflection } from '../types/schemas'; // Types for intermediate results
import {
  generateSearchQueries,
  extractAndSummarizeSearchResults,
  performReflection,
  generateFinalAnswer,
} from './agentSteps';
import { searchWeb, ProcessedSearchResult } from './searchService';
import { ResearchRequest, ResearchResponse, ResearchOverrideConfig } from '../types/api'; // For input and output types

// Helper to ensure no duplicate sources are added based on URL
const addUniqueSources = (existingSources: Source[], newSources: Source[]): Source[] => {
  const existingUrls = new Set(existingSources.map(s => s.url));
  const uniqueNewSources = newSources.filter(s => !existingUrls.has(s.url));
  return [...existingSources, ...uniqueNewSources];
};


export const runResearchProcess = async (
  userQuestion: string,
  overrideConfig?: ResearchOverrideConfig
): Promise<ResearchResponse> => {
  // Initialize AgentState
  const currentAgentState: AgentState = {
    messages: [{ role: 'user', content: userQuestion }],
    initial_search_query_count: overrideConfig?.initial_search_query_count || config.numberOfInitialQueries,
    max_research_loops: overrideConfig?.max_research_loops || config.maxResearchLoops,
    research_loop_count: 0,
    sources_gathered: [],
    web_research_result: [], // Stores all summaries gathered across loops
    query_list: [], // Will be populated by initial query generation or follow-ups
    // Optional fields will be populated as the process runs
    search_query: undefined,
    is_sufficient: undefined,
    knowledge_gap: undefined,
    follow_up_queries: undefined,
    id_counter_for_sources: 0, // Initialize if you plan to use it for unique IDs
  };

  console.log(`Starting research process for question: "${userQuestion}"`);
  console.log(`Config: Initial Queries=${currentAgentState.initial_search_query_count}, Max Loops=${currentAgentState.max_research_loops}`);

  try {
    // 1. Initial Query Generation
    console.log("Step 1: Generating initial search queries...");
    const initialSearchQueries: SearchQueryList = await generateSearchQueries(
      userQuestion,
      currentAgentState.initial_search_query_count! // Assert non-null as it's initialized
    );
    currentAgentState.query_list = initialSearchQueries.query;
    currentAgentState.messages.push({
        role: 'assistant',
        content: `Generated initial queries: ${JSON.stringify(initialSearchQueries.query)}. Rationale: ${initialSearchQueries.rationale}`
    });
    console.log(`Initial queries generated: ${currentAgentState.query_list.join(', ')}`);

    // 2. Research Loop
    while (currentAgentState.research_loop_count! < currentAgentState.max_research_loops!) {
      currentAgentState.research_loop_count!++;
      console.log(`\n--- Research Loop #${currentAgentState.research_loop_count} ---`);

      if (!currentAgentState.query_list || currentAgentState.query_list.length === 0) {
        console.log("No queries to process. Ending research loop early.");
        break;
      }

      console.log(`Processing queries: ${currentAgentState.query_list.join('; ')}`);
      currentAgentState.search_query = [...currentAgentState.query_list]; // Log current queries being processed

      const currentLoopSummaries: string[] = [];
      let currentLoopSources: Source[] = [];

      for (const query of currentAgentState.query_list) {
        console.log(`  Executing query: "${query}"`);
        const searchResults: ProcessedSearchResult[] = await searchWeb(query);
        currentAgentState.messages.push({
            role: 'assistant', // Or a 'tool' role if you want to be more specific
            name: 'searchWeb',
            content: `Search results for "${query}": ${JSON.stringify(searchResults.map(r => ({title: r.title, url: r.url})).slice(0,3))}...` // Log snippet of results
        });

        if (searchResults.length === 0) {
            console.log(`  No search results found for query: "${query}"`);
            continue;
        }

        const { summaries: newSummaries, processedSources: newSources } = await extractAndSummarizeSearchResults(
          query,
          searchResults
        );
        currentLoopSummaries.push(...newSummaries);
        currentLoopSources = addUniqueSources(currentLoopSources, newSources); // Add unique sources from this query

        console.log(`  Summarized ${newSummaries.length} results for query: "${query}"`);
      }

      // Add sources gathered in this loop to the main list, ensuring uniqueness overall
      currentAgentState.sources_gathered = addUniqueSources(currentAgentState.sources_gathered, currentLoopSources);
      currentAgentState.web_research_result!.push(...currentLoopSummaries); // Add new summaries to the main list
      currentAgentState.messages.push({
        role: 'assistant',
        content: `Collected ${currentLoopSummaries.length} new summaries in loop ${currentAgentState.research_loop_count}. Total summaries: ${currentAgentState.web_research_result!.length}`
      });

      if (currentAgentState.web_research_result!.length === 0 && currentAgentState.research_loop_count === 1) {
        // If after the first loop there are no summaries at all, it might be pointless to continue.
        console.warn("No summaries generated after the first research loop. This might indicate issues with search or summarization.");
        // Potentially break or throw an error if this is considered a critical failure.
      }

      // 3. Perform Reflection
      console.log("Performing reflection on gathered summaries...");
      const reflectionResult: Reflection = await performReflection(
        userQuestion,
        currentAgentState.web_research_result!
      );
      currentAgentState.is_sufficient = reflectionResult.is_sufficient;
      currentAgentState.knowledge_gap = reflectionResult.knowledge_gap;
      currentAgentState.follow_up_queries = reflectionResult.follow_up_queries;
      currentAgentState.messages.push({
        role: 'assistant',
        content: `Reflection result: Sufficient=${reflectionResult.is_sufficient}, Knowledge Gap="${reflectionResult.knowledge_gap}", Follow-up Queries=${JSON.stringify(reflectionResult.follow_up_queries)}`
      });
      console.log(`Reflection: Sufficient? ${currentAgentState.is_sufficient}. Knowledge Gap: ${currentAgentState.knowledge_gap}`);

      if (currentAgentState.is_sufficient || !currentAgentState.follow_up_queries || currentAgentState.follow_up_queries.length === 0) {
        console.log("Information deemed sufficient or no follow-up queries generated. Ending research loop.");
        break;
      } else {
        currentAgentState.query_list = currentAgentState.follow_up_queries;
        console.log(`Proceeding to next loop with follow-up queries: ${currentAgentState.query_list.join('; ')}`);
      }
    }

    if (currentAgentState.research_loop_count! >= currentAgentState.max_research_loops! && !currentAgentState.is_sufficient) {
        console.warn(`Max research loops (${currentAgentState.max_research_loops}) reached, but information may still be insufficient.`);
    }

    // 4. Final Answer Generation
    console.log("\nStep 4: Generating final answer...");
    if (!currentAgentState.web_research_result || currentAgentState.web_research_result.length === 0) {
        console.error("No summaries were generated throughout the research process. Cannot generate a final answer.");
        throw new Error("Failed to gather any information during the research process.");
    }

    const { finalAnswer, finalSources } = await generateFinalAnswer(
      userQuestion,
      currentAgentState.web_research_result!,
      currentAgentState.sources_gathered // Pass all unique sources gathered
    );
    currentAgentState.messages.push({ role: 'assistant', content: finalAnswer });

    console.log("Research process completed.");
    return {
      answer: finalAnswer,
      sources: finalSources,
      // Potentially include other state details for debugging if needed
      // _debug_state: currentAgentState
    };

  } catch (error) {
    console.error("Error during research process:", error);
    // Log the current state for debugging
    console.error("Current agent state at time of error:", JSON.stringify(currentAgentState, null, 2));
    // Propagate a user-friendly error or a more detailed one
    if (error instanceof Error) {
      throw new Error(`Research process failed: ${error.message}`);
    }
    throw new Error("An unknown error occurred during the research process.");
  }
};
