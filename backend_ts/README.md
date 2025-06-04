# TypeScript Research Agent Backend

## Overview

This project is a TypeScript port of an original Python-based research agent. It leverages a modern stack including Hono as a lightweight server framework, the Vercel AI SDK for seamless interaction with Large Language Models (LLMs), and OpenRouter for flexible access to a variety of LLM providers. The agent performs multi-step research to answer user questions by generating search queries, performing web searches (via Tavily), summarizing content, reflecting on gathered information, and finally generating a comprehensive answer.

## Features

*   **Built with TypeScript:** For robust, type-safe code.
*   **Hono Server Framework:** Fast and lightweight for building the API.
*   **Vercel AI SDK:** Simplifies LLM interactions.
*   **OpenRouter Integration:** Provides access to a wide range of LLMs.
*   **Tavily Search API:** For performing web searches.
*   **Multi-Step Agent Logic:** Implements a sophisticated research flow:
    1.  Initial Query Generation
    2.  Web Search & Content Summarization
    3.  Reflection and Follow-up Query Generation (if needed)
    4.  Final Answer Synthesis
*   **Configuration Management:** Uses `.env` files for easy setup.
*   **Unit Tests with Vitest:** Ensuring code quality and reliability.
*   **CORS and Logging Middleware:** Basic server utilities included.

## Prerequisites

*   Node.js (v18 or later recommended)
*   npm (comes with Node.js) or yarn

## Setup & Installation

1.  **Navigate to the project directory:**
    If you've cloned a larger repository, navigate into the backend directory:
    ```bash
    cd backend_ts
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Create environment file:**
    Copy the example environment file to create your own local configuration:
    ```bash
    cp .env.example .env
    ```

4.  **Update `.env` file:**
    Open the newly created `.env` file and fill in your actual API keys and any custom configurations. At a minimum, `OPENROUTER_API_KEY` is required. `SEARCH_API_KEY` is required for web search functionality.

## Environment Variables

The `.env` file is used to configure the application. Below are the variables defined in `.env.example`:

*   `OPENROUTER_API_KEY`: **Required.** Your API key for OpenRouter to access LLMs.
*   `SEARCH_API_KEY`: **Required for web search.** Your API key for the Tavily search service. If not provided, web search will be disabled.
*   `QUERY_GENERATOR_MODEL`: (Optional) The OpenRouter model ID for generating search queries. Defaults to `"mistralai/mistral-7b-instruct"`.
*   `WEB_SEARCHER_MODEL`: (Optional) The OpenRouter model ID for summarizing web content. Defaults to `"mistralai/mistral-7b-instruct"`.
*   `REFLECTION_MODEL`: (Optional) The OpenRouter model ID for the reflection step. Defaults to `"mistralai/mistral-7b-instruct"`.
*   `ANSWER_MODEL`: (Optional) The OpenRouter model ID for generating the final answer. Defaults to `"openai/gpt-3.5-turbo"`.
*   `NUMBER_OF_INITIAL_QUERIES`: (Optional) How many search queries to generate initially. Defaults to `"3"`.
*   `MAX_RESEARCH_LOOPS`: (Optional) The maximum number of research loops (search -> summarize -> reflect cycles). Defaults to `"3"`.
*   `LOG_LEVEL`: (Optional) The log level for the application. Defaults to `"info"`.
*   `PORT`: (Optional) The port for the development server. Defaults to `"3000"`.

## Running in Development Mode

To start the development server:

```bash
npm run dev
```

The server will typically start on port 3000 by default (or the port specified in your `.env` file). You should see a log message indicating the server is listening, e.g., `Server is listening on http://localhost:3000`.

## Running Tests

To execute the unit tests and generate a coverage report:

```bash
npm test
```

Test results and coverage information will be displayed in the console. Coverage reports can also be found in the `coverage/` directory.

## API Endpoints

### `/api/research`

*   **Method:** `POST`
*   **Description:** Initiates the research process for a given question.
*   **Request Body:**
    ```json
    {
      "question": "Your research question here",
      "override_config": { // Optional: Override default research parameters
        "initial_search_query_count": 3,
        "max_research_loops": 2
        // Other parameters from AppConfig can potentially be overridden here
      }
    }
    ```
*   **Success Response (200 OK):**
    The response includes the synthesized answer and a list of sources used.
    ```json
    {
      "answer": "The comprehensive answer to your research question, based on the gathered and summarized information...",
      "sources": [
        {
          "title": "Example Source Title 1",
          "url": "https://example.com/source1",
          "snippet": "A brief snippet or the content that was summarized from source 1..."
        },
        {
          "title": "Example Source Title 2",
          "url": "https://example.com/source2",
          "snippet": "A brief snippet from source 2..."
        }
        // ... other sources
      ]
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:** If the request body is invalid or the `question` is missing.
        ```json
        {
          "error": "Bad Request: 'question' field is missing or empty.",
          "details": "Optional additional details about the parsing error if applicable."
        }
        ```
    *   **500 Internal Server Error:** If an error occurs during the research process.
        ```json
        {
          "error": "An internal server error occurred while processing your research request.",
          "details": "In development, this might contain more specific internal error messages. In production, it's usually more generic."
        }
        ```

## Project Structure

A brief overview of the main directories within `src/`:

*   `config/`: Handles application configuration from environment variables.
*   `prompts/`: Contains functions that generate prompts for the LLMs.
*   `services/`: Core logic of the application:
    *   `agentSteps.ts`: Implements individual steps of the research agent (query generation, summarization, reflection, answer generation).
    *   `researchOrchestrator.ts`: Manages the overall flow of the research process.
    *   `searchService.ts`: Handles interactions with the Tavily web search API.
*   `types/`: Defines TypeScript types and interfaces used throughout the application (e.g., API request/response structures, agent state, Zod schemas).
*   `index.ts`: The main entry point for the Hono server, defining routes and middleware.

This structure aims to separate concerns and make the codebase maintainable.
