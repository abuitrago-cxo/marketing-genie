// Define the structure for messages in the agent's state
export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool'; // Added system and tool roles
  content: string;
  name?: string; // Optional name for tool calls/results
  tool_calls?: any[]; // For assistant messages requesting tool calls
  tool_call_id?: string; // For tool messages responding to a call
}

// Define the structure for a source gathered during web research
export interface Source {
  url: string;
  title: string;
  snippet?: string;
  short_url?: string; // Optional short URL if available
  value?: string; // Could be the full content of the source, or a summary
  id?: string; // Optional unique ID for the source
}

// Define the overall state of the research agent
export interface AgentState {
  messages: Message[];
  initial_search_query_count?: number;
  query_list?: string[]; // List of initial queries generated
  web_research_result?: string[]; // Array of summaries/content from web research
  sources_gathered: Source[]; // Detailed information about each source
  search_query?: string[]; // Current list of queries being processed (e.g., follow-up queries)
  research_loop_count?: number;
  max_research_loops?: number;
  is_sufficient?: boolean; // Result of the reflection step
  knowledge_gap?: string; // Identified knowledge gap from reflection
  follow_up_queries?: string[]; // Follow-up queries from reflection
  id_counter_for_sources?: number; // Counter to generate unique IDs for sources
  // Potentially add other fields as needed during development
  // e.g., current_research_topic, error_messages, etc.
}
