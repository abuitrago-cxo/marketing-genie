---
trigger: always_on
---

# Development Rules and Guidelines

## 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Follow the original Google Gemini fullstack langgraph quickstart repository patterns** for consistency and maintainability.

## 🏗️ Project Architecture (Based on Original Google Gemini Repository)

### Core Architecture Principles
- **LangGraph-First**: All agent workflows must use LangGraph for state management and execution control
- **FastAPI Backend**: Single FastAPI application serving both API endpoints and frontend static files
- **React Frontend**: Vite-based React application with TypeScript and Tailwind CSS
- **Modular Design**: Clear separation between agent logic, API endpoints, and UI components

### Project Structure (Standard)
```
├── backend/                    # Python backend (LangGraph + FastAPI)
│   ├── src/agent/             # Core agent logic (follows original structure)
│   │   ├── app.py            # Main FastAPI application (entry point)
│   │   ├── graph.py          # Original LangGraph workflow (core)
│   │   ├── state.py          # LangGraph state schemas
│   │   ├── configuration.py  # Agent configuration
│   │   ├── prompts.py        # LLM prompts and templates
│   │   └── utils.py          # Utility functions
│   ├── src/api/              # API endpoint modules
│   │   ├── enhanced_endpoints.py    # Enhanced features API
│   │   ├── specialized_endpoints.py # Multi-agent system API
│   │   └── github_endpoints.py      # GitHub integration API
│   ├── langgraph.json        # LangGraph configuration (required)
│   └── pyproject.toml        # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components (organized by feature)
│   │   ├── App.tsx          # Main React application
│   │   ├── main.tsx         # React entry point
│   │   └── global.css       # Global styles
│   ├── index.html           # HTML template
│   ├── vite.config.ts       # Vite configuration
│   └── package.json         # Node.js dependencies
├── docker-compose.yml        # Infrastructure orchestration
├── Dockerfile               # Multi-stage build
└── .env                     # Environment variables
```

## 🧱 Code Structure & Modularity

### Backend Structure Rules
- **`backend/src/agent/`**: Core agent logic following original Google Gemini patterns
  - `app.py`: Main FastAPI application with frontend mounting
  - `graph.py`: Primary LangGraph workflow (original 5-node flow)
  - `state.py`: LangGraph state schemas and type definitions
  - `configuration.py`: Agent configuration and LLM settings
- **`backend/src/api/`**: API endpoint modules grouped by functionality
- **`backend/langgraph.json`**: Required LangGraph configuration file
- **Never create a file longer than 2000 lines** - split into logical modules
- **Use relative imports within the agent package**: `from .state import OverallState`

### Frontend Structure Rules
- **`frontend/src/components/`**: React components organized by feature/domain
  - `enhanced/`: Enhanced UI components
  - `specialized/`: Multi-agent system components
  - `auth/`: Authentication components
  - `ui/`: Reusable UI components (Shadcn)
- **`frontend/src/App.tsx`**: Main React application component
- **`frontend/src/main.tsx`**: React entry point with routing setup
- **Use TypeScript for all components** with strict type checking
- **Follow React functional component patterns** with hooks

## 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
- **Test LangGraph workflows** using the built-in testing utilities.

## ✅ Task Completion
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a "Discovered During Work" section.

## 📎 Style & Conventions
- Follow consistent code formatting and validation standards.
- **Python**: Use Black formatting and type hints for all functions.
- **TypeScript**: Use strict TypeScript with no `any` types allowed.

## 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

## 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.

## 🐳 Docker & Infrastructure Rules

### Container Management
- **Use Docker Compose for development and production** - it provides the complete infrastructure stack
- **Always use health checks** in Docker services to ensure proper startup order
- **Environment variables should be documented** in both `.env.example` and docker-compose.yml
- **Never hardcode secrets** - always use environment variables

### Database & Cache
- **PostgreSQL is the primary database** - used for LangGraph state, threads, runs, and application data
- **Redis is used for pub-sub and caching** - enables real-time streaming and background task management
- **Alwa