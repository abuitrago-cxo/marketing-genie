import { Source } from './agentState'; // Assuming Source is defined in agentState.ts

// Configuration options that can be overridden in a research request
export interface ResearchOverrideConfig {
  initial_search_query_count?: number;
  max_research_loops?: number;
  // Add other configurable parameters here, e.g.,
  // llm_model_name?: string;
  // embedding_model_name?: string;
  // search_tool_config?: any; // Configuration for the search tool
}

// Defines the structure for a research request from the client
export interface ResearchRequest {
  question: string; // The user's research question or topic
  override_config?: ResearchOverrideConfig; // Optional configurations to override defaults
}

// Defines the structure for a successful research response
export interface ResearchResponse {
  answer: string; // The final synthesized answer to the research question
  sources: Source[]; // List of sources used to generate the answer
  // Optionally, include other metadata, like number of loops, queries used, etc.
  // research_summary?: string; // A summary of the research process
  // debug_info?: any; // For debugging purposes
}

// Defines the structure for an error response
export interface ErrorResponse {
  error: string; // A descriptive error message
  details?: any; // Optional field for more detailed error information or a stack trace
}
