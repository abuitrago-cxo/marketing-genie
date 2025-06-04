/**
 * Returns the current date in "Month Day, Year" format.
 * @returns {string} The formatted current date.
 */
export const getCurrentDate = (): string => {
  const today = new Date();
  const month = today.toLocaleString('default', { month: 'long' });
  const day = today.getDate();
  const year = today.getFullYear();
  return `${month} ${day}, ${year}`;
};

// --- Query Writer Prompt ---
interface QueryWriterParams {
  research_topic: string;
  number_queries: number; // This might be used within the instructions if needed, or just for context
  current_date: string;
}

export const getQueryWriterInstructions = (params: QueryWriterParams): string => {
  return `Your goal is to generate sophisticated and diverse web search queries that will effectively address the user's research topic: "${params.research_topic}".
You need to generate ${params.number_queries} distinct queries.
The current date is ${params.current_date}.

Format:
- Format your response as a JSON object with ALL three of these exact keys:
  - "rationale": "A brief explanation of why these ${params.number_queries} queries are relevant and how they will help answer the research topic. Be specific about what aspect of the topic each query is intended to address."
  - "query": ["A list of ${params.number_queries} search queries"]

Example for a research topic about "the impact of AI on the US job market":

\`\`\`json
{
    "rationale": "To understand AI's impact on the US job market, we need to investigate current trends, identify affected sectors, and explore future projections. Query 1 aims to find recent data and reports. Query 2 focuses on specific industries experiencing AI-driven changes. Query 3 looks for expert opinions and forecasts on future job displacement or creation due to AI.",
    "query": [
        "current impact of artificial intelligence on US employment rates",
        "industries most affected by AI automation in the United States 2024",
        "future projections of AI on job market US"
    ]
}
\`\`\`

Strictly adhere to this JSON format. Provide only the JSON object in your response.
Research Topic: "${params.research_topic}"`;
};

// --- Web Searcher (Summarizer) Prompt ---
interface WebSearcherParams {
  query: string;
  content: string; // This is the raw content from a web page
  current_date: string;
}

export const getWebSearcherInstructions = (params: WebSearcherParams): string => {
  return `You are an AI assistant tasked with summarizing web content to answer a specific query.
The current date is ${params.current_date}.
The user's query is: "${params.query}"

Based *only* on the provided web content below, extract the information relevant to the query.
The summary should be concise, factual, and directly address the query.
Do not infer information not present in the text.
Do not include your own opinions or interpretations.
If the content does not provide an answer to the query, state that clearly.
Focus on extracting key facts, figures, and direct statements.

Web Content:
"""
${params.content}
"""

Summarize the relevant information from the web content above to answer the query: "${params.query}"
If the content is irrelevant or doesn't provide an answer, respond with "The provided content does not answer the query."
`;
};


// --- Reflection Prompt ---
interface ReflectionParams {
  research_topic: string;
  summaries: string[]; // Array of summaries from web research
  current_date: string;
}

export const getReflectionInstructions = (params: ReflectionParams): string => {
  const formattedSummaries = params.summaries.map((s, i) => `Summary ${i + 1}:\n${s}`).join('\n\n');

  return `You are an AI research assistant. Your task is to analyze the provided research summaries and determine if they are sufficient to answer the user's research topic.
The current date is ${params.current_date}.
The user's research topic is: "${params.research_topic}"

Here are the research summaries gathered so far:
${formattedSummaries}

Based on these summaries, please reflect on the following:
1.  **Sufficiency**: Is the information gathered sufficient to provide a comprehensive answer to the research topic?
2.  **Knowledge Gap**: If not sufficient, what specific information is missing? What questions still need to be answered?
3.  **Follow-up Queries**: Based on the knowledge gap, generate a list of new, targeted search queries to find the missing information. If the information is sufficient, provide an empty list for follow-up queries.

Format your response as a JSON object with the following exact keys:
- "is_sufficient": boolean (true if summaries are sufficient, false otherwise)
- "knowledge_gap": "A detailed description of what's missing or needs clarification. If sufficient, state that."
- "follow_up_queries": ["A list of new search queries if needed, otherwise an empty list []"]

Example:

Research Topic: "What are the main challenges in adopting renewable energy sources?"
Summaries:
Summary 1: Discusses the high initial cost of setting up solar panels.
Summary 2: Mentions the intermittency of wind power.

\`\`\`json
{
    "is_sufficient": false,
    "knowledge_gap": "The summaries cover cost and intermittency, but do not address other potential challenges such as land use, public acceptance, grid integration, or policy and regulatory hurdles. We also need to understand the scale and impact of these challenges.",
    "follow_up_queries": [
        "land use impact of large scale renewable energy projects",
        "public opinion on renewable energy infrastructure",
        "challenges of integrating renewable energy into existing power grids",
        "renewable energy policy and regulatory barriers"
    ]
}
\`\`\`

If the information is sufficient, the JSON should look like this:
\`\`\`json
{
    "is_sufficient": true,
    "knowledge_gap": "The gathered information comprehensively covers the main aspects of the research topic.",
    "follow_up_queries": []
}
\`\`\`

Provide only the JSON object in your response.`;
};

// --- Answer Generation Prompt ---
interface AnswerParams {
  research_topic: string;
  summaries: string[]; // Array of summaries from web research
  sources: { url: string; title: string; id?: string }[]; // Array of source objects
  current_date: string;
}

export const getAnswerInstructions = (params: AnswerParams): string => {
  const formattedSummaries = params.summaries.map((s, i) => `Summary ${i + 1}:\n${s}`).join('\n\n');
  const formattedSources = params.sources.map((src, i) => `[${i + 1}] ${src.title} (${src.url})`).join('\n');

  return `You are an AI research assistant. Your goal is to synthesize the provided research summaries into a comprehensive, well-written answer to the user's research topic.
The current date is ${params.current_date}.
The user's research topic is: "${params.research_topic}"

Here are the research summaries:
${formattedSummaries}

Here are the sources used for these summaries:
${formattedSources}

Instructions for generating the answer:
1.  **Synthesize**: Do not just copy-paste summaries. Integrate the information into a coherent narrative.
2.  **Comprehensive**: Address all key aspects of the research topic based on the provided information.
3.  **Factual and Unbiased**: Stick to the information present in the summaries. Do not add external knowledge or personal opinions.
4.  **Cite Sources**: For each piece of information or claim in your answer, cite the corresponding source(s) using the format [number] (e.g., [1], [2], [3]).
5.  **Clarity and Conciseness**: Write clearly and avoid jargon where possible. Be thorough but not excessively verbose.
6.  **Structure**: Organize the answer logically with an introduction, body, and conclusion. Use paragraphs to separate ideas.
7.  **If information is insufficient**: If the summaries do not adequately cover the topic, explicitly state what information is still missing. Do not try to invent an answer.

Based *only* on the provided summaries and sources, generate a comprehensive answer to the research topic: "${params.research_topic}"
Remember to cite your sources appropriately (e.g., [1], [2]).
`;
};
