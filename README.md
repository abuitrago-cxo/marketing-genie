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

### Running with Node.js Server (Alternative Local Setup)

This method uses the traditional Python backend for API and the new Node.js server (located in `express_server/`) to serve the frontend and proxy API requests. This is an alternative to using the `make dev` command or running the full Docker deployment for local testing if you specifically want to use the Node.js server for the frontend.

**Prerequisites:**
- Ensure all prerequisites from the main "Getting Started" section are met (Node.js, Python, Gemini API key in `backend/.env`).
- Dependencies for both `frontend` and `backend` should be installed as described previously.

**Steps:**

1.  **Build the Frontend:**
    The Node.js server serves static files, so you need to build the frontend first.
    ```bash
    cd frontend
    npm install # If you haven't already
    npm run build
    cd ..
    ```

2.  **Start the Python Backend API:**
    The Python backend is still needed to handle the API calls. You can run its development server.
    Open a terminal in the `backend/` directory:
    ```bash
    # Ensure your virtual environment is active if you use one
    # Make sure .env file with GEMINI_API_KEY is present in backend/
    pip install . # If you haven't already or if dependencies changed
    langgraph dev
    ```
    This will typically start the backend API on `http://127.0.0.1:2024` or a similar port, and it might open a browser for the LangGraph UI. The important part is that the API service proxied by Vite (usually to `http://127.0.0.1:8000` by default in production-like setups, or `http://127.0.0.1:2024` if `langgraph dev` changes that) is up.
    *Note: The Node.js server is configured by default to proxy to `http://127.0.0.1:8000`. If `langgraph dev` runs the API on a different port (e.g., 2024) for the actual API endpoints the frontend calls, you might need to adjust `PYTHON_BACKEND_URL` for the Node.js server (e.g., by setting it as an environment variable when running `node server.js` or modifying `express_server/server.js`). For this guide, we'll assume the API is available at the default proxy target of `http://127.0.0.1:8000` or that `langgraph dev` also makes it available there.*

3.  **Start the Node.js Server:**
    Open another terminal in the `express_server/` directory:
    ```bash
    npm install # If you haven't already or if dependencies changed
    node server.js
    ```
    This will start the Node.js server, typically on `http://localhost:3000`.

4.  **Access the Application:**
    Open your browser and navigate to `http://localhost:3000/app`.

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

![Agent Flow](./agent.png)

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using a Gemini model.
2.  **Web Research:** For each query, it uses the Gemini model with the Google Search API to find relevant web pages.
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps. It uses a Gemini model for this reflection process.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from the web sources, using a Gemini model.

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