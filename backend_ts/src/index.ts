import { Hono } from 'hono';
import { logger } from 'hono/logger';
import { cors } from 'hono/cors';
import { serve } from '@hono/node-server'; // For local development server

import { runResearchProcess } from './services/researchOrchestrator';
import { ResearchRequest, ResearchResponse, ErrorResponse, ResearchOverrideConfig } from './types/api';
import config from './config'; // To access port or other server specific configs if needed

const app = new Hono();

// --- Middleware ---
app.use('*', logger()); // Log all requests
app.use('*', cors());   // Enable CORS for all routes

// --- Routes ---
app.get('/', (c) => {
  return c.text('Research Agent API is running!');
});

app.post('/api/research', async (c) => {
  let requestBody: ResearchRequest;

  try {
    requestBody = await c.req.json<ResearchRequest>();
  } catch (error) {
    console.error("Failed to parse request body:", error);
    return c.json<ErrorResponse>({ error: "Invalid request body. Expected JSON.", details: (error as Error).message }, 400);
  }

  const { question, override_config } = requestBody;

  if (!question || typeof question !== 'string' || question.trim() === "") {
    return c.json<ErrorResponse>({ error: "Bad Request: 'question' field is missing or empty." }, 400);
  }

  console.log(`Received research request for question: "${question}"`);
  if (override_config) {
    console.log("With override config:", override_config);
  }

  try {
    const result: ResearchResponse = await runResearchProcess(question, override_config);
    return c.json<ResearchResponse>(result, 200);
  } catch (error) {
    console.error("Error during research process execution:", error);
    const err = error as Error;
    // In a production environment, you might want to avoid sending detailed internal errors to the client.
    // For now, we send a generic message but log the specific error.
    return c.json<ErrorResponse>({ error: "An internal server error occurred while processing your research request.", details: err.message }, 500);
  }
});

// --- Server ---
// For local development, we'll use @hono/node-server.
// For deployment (e.g., Vercel, Cloudflare Workers), this part might be different
// or handled by the platform. The `export default app` is key for many platforms.

const port = parseInt(process.env.PORT || "3000"); // Default to port 3000
console.log(`Research Agent server starting on port ${port}...`);

// Check if OPENROUTER_API_KEY is set, otherwise the agent won't work.
if (!config.openRouterApiKey) {
    console.error("FATAL ERROR: OPENROUTER_API_KEY is not set in the environment.");
    console.error("The application will not function correctly without it.");
    // Optionally, exit the process if this is a critical local dev issue
    // process.exit(1);
}
if (!config.searchApiKey) {
    console.warn("WARNING: SEARCH_API_KEY is not set. Web search functionality will be disabled.");
}


serve({
  fetch: app.fetch,
  port: port,
}, (info) => {
  console.log(`Server is listening on http://localhost:${info.port}`);
});

export default app; // Export for serverless environments or other entry points
