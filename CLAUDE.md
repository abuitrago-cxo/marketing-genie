# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

- Frontend: React application with TypeScript, Vite, and Tailwind CSS
- Backend: Python-based LangGraph agent that performs iterative research using Google Gemini models
- Agent Flow:
  1. Generates search queries from user input
  2. Performs web research via Google Search API
  3. Reflects on results to identify knowledge gaps
  4. Iteratively refines search until sufficient information is gathered
  5. Synthesizes answer with citations

## Development Commands

Initial Setup:
```bash
make setup       # Install all dependencies for frontend and backend
```

Development:
```bash
make dev         # Run both frontend and backend dev servers
npm run build    # Build frontend for production (in frontend/)
npm run lint     # Run frontend ESLint
ruff check .     # Run backend linter (in backend/)
mypy .           # Run backend type checker (in backend/)
```

## Environment Setup

Required environment variables:
- GEMINI_API_KEY: Google Gemini API key
- LANGSMITH_API_KEY: LangSmith API key (for production)