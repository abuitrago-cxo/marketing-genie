import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Define the structure of our configuration
interface AppConfig {
  openRouterApiKey: string;
  queryGeneratorModel: string;
  webSearcherModel: string;
  reflectionModel: string;
  answerModel: string;
  numberOfInitialQueries: number;
  maxResearchLoops: number;
  searchApiKey?: string; // Optional
  logLevel: string;
}

// Retrieve and validate environment variables
const openRouterApiKey = process.env.OPENROUTER_API_KEY;
if (!openRouterApiKey) {
  throw new Error("Missing required environment variable: OPENROUTER_API_KEY");
}

const config: AppConfig = {
  openRouterApiKey,
  queryGeneratorModel: process.env.QUERY_GENERATOR_MODEL || "mistralai/mistral-7b-instruct",
  webSearcherModel: process.env.WEB_SEARCHER_MODEL || "mistralai/mistral-7b-instruct",
  reflectionModel: process.env.REFLECTION_MODEL || "mistralai/mistral-7b-instruct",
  answerModel: process.env.ANSWER_MODEL || "openai/gpt-3.5-turbo",
  numberOfInitialQueries: parseInt(process.env.NUMBER_OF_INITIAL_QUERIES || "3", 10),
  maxResearchLoops: parseInt(process.env.MAX_RESEARCH_LOOPS || "3", 10),
  searchApiKey: process.env.SEARCH_API_KEY,
  logLevel: process.env.LOG_LEVEL || "info",
};

// Validate that parsed numbers are indeed numbers
if (isNaN(config.numberOfInitialQueries)) {
  throw new Error("Invalid value for NUMBER_OF_INITIAL_QUERIES: Must be a number.");
}
if (isNaN(config.maxResearchLoops)) {
  throw new Error("Invalid value for MAX_RESEARCH_LOOPS: Must be a number.");
}

export default config;
