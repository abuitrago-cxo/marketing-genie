# Gemini Fullstack LangGraph Quickstart

This project demonstrates a fullstack application using a React frontend and a LangGraph-powered backend agent. The agent is designed to perform comprehensive research on a user's query by dynamically generating search terms, querying the web using Google Search, reflecting on the results to identify knowledge gaps, and iteratively refining its search until it can provide a well-supported answer with citations. This application serves as an example of building research-augmented conversational AI using LangGraph and Google's Gemini models.

![Gemini Fullstack LangGraph](./app.png)

## Features

- 💬 Fullstack application with a React frontend and LangGraph backend.
- 🧠 Powered by a LangGraph agent for advanced research and conversational AI.
- 🔍 Dynamic search query generation using Google Gemini models.
- 🌐 Integrated web research via Google Search API.
- 🤔 Reflective reasoning to identify knowledge gaps and refine searches.
- 📄 Generates answers with citations from gathered sources.
- 🔄 Hot-reloading for both frontend and backend development during development.

## Project Structure

The project is divided into two main directories:

-   `frontend/`: Contains the React application built with Vite.
-   `backend/`: Contains the LangGraph/FastAPI application, including the research agent logic.

## Getting Started: Development and Local Testing

Follow these steps to get the application running locally for development and testing.

**1. Prerequisites:**

-   Node.js and npm (or yarn/pnpm)
-   Python 3.8+
-   **`GEMINI_API_KEY`**: The backend agent requires a Google Gemini API key.
    1.  Navigate to the `backend/` directory.
    2.  Create a file named `.env` by copying the `backend/.env.example` file.
    3.  Open the `.env` file and add your Gemini API key: `GEMINI_API_KEY="YOUR_ACTUAL_API_KEY"`

**2. Install Dependencies:**

**Backend:**

```bash
cd backend
pip install .
```

**Frontend:**

```bash
cd frontend
npm install
```

**3. Run Development Servers:**

**Backend & Frontend:**

```bash
make dev
```
This will run the backend and frontend development servers.    Open your browser and navigate to the frontend development server URL (e.g., `http://localhost:5173/app`).

_Alternatively, you can run the backend and frontend development servers separately. For the backend, open a terminal in the `backend/` directory and run `langgraph dev`. The backend API will be available at `http://127.0.0.1:2024`. It will also open a browser window to the LangGraph UI. For the frontend, open a terminal in the `frontend/` directory and run `npm run dev`. The frontend will be available at `http://localhost:5173`._

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

![Agent Flow](./agent.png)

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using a Gemini model.
2.  **Web Research:** For each query, it uses the Gemini model with the Google Search API to find relevant web pages.
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps. It uses a Gemini model for this reflection process.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from the web sources, using a Gemini model.

## LLM Provider Configuration

The backend agent can be configured to use different Large Language Model (LLM) providers beyond the default Google Gemini. This allows for flexibility in choosing models, including locally run models via Ollama or LM Studio.

The following environment variables control the LLM provider. These are typically set in your `docker-compose.yml` for containerized deployments, or can be set as system environment variables if running the backend directly. For local development without Docker, you might need to ensure your Python execution environment loads these (e.g., via a `.env` file that your application explicitly loads for these settings).

-   **`LLM_PROVIDER`**:
    *   **Description**: Specifies the LLM provider to use for the agent's core reasoning, query generation, and answer synthesis.
    *   **Values**: `"gemini"`, `"ollama"`, `"lmstudio"`
    *   **Default**: `"gemini"` (as set in `docker-compose.yml`)
    *   **Note**: When using `ollama` or `lmstudio`, ensure the respective services are running and accessible.

-   **`OLLAMA_BASE_URL`**:
    *   **Description**: The base URL for the Ollama API if `LLM_PROVIDER` is set to `"ollama"`.
    *   **Default**: `"http://host.docker.internal:11434"` (as set in `docker-compose.yml`, points to the host machine from within Docker)
    *   **Note**: If running Ollama on a different host or port, or running the backend outside Docker, adjust this value accordingly (e.g., `http://localhost:11434`).

-   **`OLLAMA_MODEL_NAME`**:
    *   **Description**: The model name to use with Ollama (e.g., "llama2", "mistral", "codellama").
    *   **Default**: `"llama2"` (as set in `docker-compose.yml`)
    *   **Note**: The specified model must be pulled and available in your Ollama instance.

-   **`LMSTUDIO_BASE_URL`**:
    *   **Description**: The base URL for the LM Studio compatible API if `LLM_PROVIDER` is set to `"lmstudio"`. This usually ends with `/v1`.
    *   **Default**: `"http://host.docker.internal:1234/v1"` (as set in `docker-compose.yml`, points to the host machine from within Docker)
    *   **Note**: If running LM Studio on a different host or port, or running the backend outside Docker, adjust this value accordingly (e.g., `http://localhost:1234/v1`).

-   **`LMSTUDIO_MODEL_NAME`**:
    *   **Description**: The model identifier to use with LM Studio. This can often be found in the LM Studio UI (e.g., "Publisher/Repository/ModelFile").
    *   **Default**: `"local-model"` (as set in `docker-compose.yml`; this is a generic placeholder and should be updated to a specific model identifier loaded in your LM Studio).

### Important Notes for Ollama and LM Studio Usage:

*   **Accessibility**: When running the application with Docker, `host.docker.internal` is used as the default hostname in `docker-compose.yml` to allow the Docker container to access services (Ollama, LM Studio) running on your host machine. If these services are running elsewhere (e.g., a different machine on your network), update the `*_BASE_URL` in your `docker-compose.yml` or environment configuration.
*   **Model Compatibility**: The models selected in Ollama or LM Studio should ideally be instruction-following chat models. While the system attempts to use them for tasks like query generation and reflection, their performance and ability to adhere to specific output formats (like structured output for search queries or reflection steps) may vary significantly compared to Gemini. Some models may not support the required function calling or structured output capabilities effectively.
*   **Current Limitation - Web Research**: The integrated web research capability, which utilizes Google Search tools directly via Gemini models, is **only functional when `LLM_PROVIDER` is set to `"gemini"`**. If you select "ollama" or "lmstudio", the agent will still attempt to generate search queries and reflect on content (if any were hypothetically provided), but it will **not** be able to perform actual web searches or incorporate real-time web content into its answers. This is because the Google Search tool integration is currently specific to the Gemini models used in this application.

### Configuring via the User Interface

In addition to setting environment variables, you can now configure LLM provider settings directly within the application's user interface.

*   **Accessing Configuration:** Click the **gear icon (⚙️)** usually found in the header of the application to open the LLM Configuration modal.
*   **Available Settings:**
    *   **LLM Provider:** Select between "Gemini", "Ollama", and "LM Studio".
    *   **Gemini API Key:** Input your Gemini API key when "Gemini" is selected. This is stored in your browser's local storage and sent with each request.
    *   **Ollama Settings:** Configure the Base URL (e.g., `http://localhost:11434`) and the Model Name (e.g., `llama2`) when "Ollama" is selected.
    *   **LM Studio Settings:** Configure the Base URL (e.g., `http://localhost:1234/v1`) and the Model Name when "LM Studio" is selected.
*   **Automatic Saving:** Changes made in the UI are automatically saved to your browser's local storage and applied to subsequent requests.

#### Configuration Precedence

The application uses the following order to determine which configuration values to apply for each agent request:

1.  **UI Configuration (Local Storage):** Settings configured and saved via the user interface take the highest precedence. These are sent with each request to the backend.
2.  **Environment Variables:** If a specific setting is not configured in the UI (or if local storage is empty/cleared, or the UI sends a `null` value for a field), the backend application will fall back to using the environment variables defined for it (e.g., in `docker-compose.yml` or the system environment). This includes `GEMINI_API_KEY` (for chat models and the initial default for the UI), `LLM_PROVIDER`, `OLLAMA_BASE_URL`, etc.
3.  **Application Defaults (Backend):** If a setting is not found in either the UI's local storage (and thus not sent in the request) nor in the environment variables, the backend application will rely on its built-in default values (defined in the Pydantic model fields in `backend/src/agent/configuration.py`). For critical settings like API keys or base URLs, if no value is provided by any layer, this may lead to errors or non-functional behavior for the selected provider.

#### Resetting to Defaults

*   The configuration modal includes a **"Reset to Defaults"** button.
*   Clicking this button will:
    1.  Clear any LLM settings currently stored in your browser's local storage.
    2.  Fetch and apply the default configuration currently exposed by the backend via its `/agent/config-defaults` endpoint. These backend-provided defaults are themselves determined by the environment variables set at the time the backend starts, plus any hardcoded application defaults.
*   This is useful if you want to revert to the baseline environment configuration or resolve issues caused by incorrect UI settings.

**Note on `GEMINI_API_KEY` for Web Research:**
As highlighted in the "Important Notes" and within the UI itself, the web research capability (which uses Google Search tools via the `google.generai.Client`) currently relies on a `GEMINI_API_KEY` set as an **environment variable** when the backend application starts. It does **not** use the Gemini API key that might be configured via the UI for this specific web search functionality. Other Gemini-powered chat, reasoning, and query generation steps **will** use the UI-configured (or environment-fallback) Gemini API key.

## Deployment

In production, the backend server serves the optimized static frontend build. LangGraph requires a Redis instance and a Postgres database. Redis is used as a pub-sub broker to enable streaming real time output from background runs. Postgres is used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics. For more details on how to deploy the backend server, take a look at the [LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/deployment_options/). Below is an example of how to build a Docker image that includes the optimized frontend build and the backend server and run it via `docker-compose`.

_Note: For the docker-compose.yml example you need a LangSmith API key, you can get one from [LangSmith](https://smith.langchain.com/settings)._

_Note: If you are not running the docker-compose.yml example or exposing the backend server to the public internet, you update the `apiUrl` in the `frontend/src/App.tsx` file your host. Currently the `apiUrl` is set to `http://localhost:8123` for docker-compose or `http://localhost:2024` for development._

**1. Build the Docker Image:**

   Run the following command from the **project root directory**:
   ```bash
   docker build -t gemini-fullstack-langgraph -f Dockerfile .
   ```
**2. Run the Production Server:**

   ```bash
   GEMINI_API_KEY=<your_gemini_api_key> LANGSMITH_API_KEY=<your_langsmith_api_key> docker-compose up
   ```

Open your browser and navigate to `http://localhost:8123/app/` to see the application. The API will be available at `http://localhost:8123`.

## Technologies Used

- [React](https://reactjs.org/) (with [Vite](https://vitejs.dev/)) - For the frontend user interface.
- [Tailwind CSS](https://tailwindcss.com/) - For styling.
- [Shadcn UI](https://ui.shadcn.com/) - For components.
- [LangGraph](https://github.com/langchain-ai/langgraph) - For building the backend research agent.
- [Google Gemini](https://ai.google.dev/models/gemini) - LLM for query generation, reflection, and answer synthesis.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 