import { z } from 'zod';

// Schema for a list of search queries
export const SearchQueryListSchema = z.object({
  query: z.array(z.string()).describe("A list of search queries to be used for web research."),
  rationale: z.string().describe("A brief explanation of why these queries are relevant to the research topic.")
});

// TypeScript type inferred from the schema
export type SearchQueryList = z.infer<typeof SearchQueryListSchema>;

// Schema for the reflection step, deciding if information is sufficient
export const ReflectionSchema = z.object({
  is_sufficient: z.boolean().describe("Whether the provided summaries are sufficient to answer the user's question."),
  knowledge_gap: z.string().describe("A description of what information is missing or needs clarification."),
  follow_up_queries: z.array(z.string()).describe("A list of follow-up queries to address the knowledge gap.")
});

// TypeScript type inferred from the schema
export type Reflection = z.infer<typeof ReflectionSchema>;
