# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
# If you use yarn or pnpm, adjust accordingly (e.g., copy yarn.lock or pnpm-lock.yaml and use yarn install or pnpm install)
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Declare ARGs for Firebase config. These will be passed in during the docker build command.
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
ARG VITE_FIREBASE_MEASUREMENT_ID

# Set ENVs from ARGs for Vite to use during build
ENV VITE_FIREBASE_API_KEY=$VITE_FIREBASE_API_KEY
ENV VITE_FIREBASE_AUTH_DOMAIN=$VITE_FIREBASE_AUTH_DOMAIN
ENV VITE_FIREBASE_PROJECT_ID=$VITE_FIREBASE_PROJECT_ID
ENV VITE_FIREBASE_STORAGE_BUCKET=$VITE_FIREBASE_STORAGE_BUCKET
ENV VITE_FIREBASE_MESSAGING_SENDER_ID=$VITE_FIREBASE_MESSAGING_SENDER_ID
ENV VITE_FIREBASE_APP_ID=$VITE_FIREBASE_APP_ID
ENV VITE_FIREBASE_MEASUREMENT_ID=$VITE_FIREBASE_MEASUREMENT_ID

# Build the frontend
RUN npm run build

# Stage 2: Python Backend
FROM docker.io/langchain/langgraph-api:3.11

# -- Install UV and additional tools --
# Install curl, health check tools, and UV
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    netcat-openbsd \
    postgresql-client \
    redis-tools \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"
# -- End of UV and tools installation --

# -- Copy built frontend from builder stage --
# The app.py expects the frontend build to be at ../frontend/dist relative to its own location.
# If app.py is at /deps/backend/src/agent/app.py, then ../frontend/dist resolves to /deps/frontend/dist.
COPY --from=frontend-builder /app/frontend/dist /deps/frontend/dist
# -- End of copying built frontend --

# -- Adding local package . --
ADD backend/ /deps/backend
# -- End of local package . --

# -- Installing all local dependencies using UV --
# First, we need to ensure pip is available for UV to use
RUN uv pip install --system pip setuptools wheel

# Install additional dependencies for enhanced features
RUN uv pip install --system \
    langchain-anthropic \
    langchain-openai \
    fastapi[all] \
    uvicorn[standard] \
    redis \
    psycopg2-binary

# Install dependencies with UV, respecting constraints
RUN cd /deps/backend && \
    PYTHONDONTWRITEBYTECODE=1 UV_SYSTEM_PYTHON=1 uv pip install --system -c /api/constraints.txt -e .
# -- End of local dependencies install --
ENV LANGGRAPH_HTTP='{"app": "/deps/backend/src/agent/app.py:app"}'
ENV LANGSERVE_GRAPHS='{"agent": "/deps/backend/src/agent/graph.py:graph"}'

# -- Ensure user deps didn't inadvertently overwrite langgraph-api
# Create all required directories that the langgraph-api package expects
RUN mkdir -p /api/langgraph_api /api/langgraph_runtime /api/langgraph_license /api/langgraph_storage && \
    touch /api/langgraph_api/__init__.py /api/langgraph_runtime/__init__.py /api/langgraph_license/__init__.py /api/langgraph_storage/__init__.py
# Use pip for this specific package as it has poetry-based build requirements
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir --no-deps -e /api
# -- End of ensuring user deps didn't inadvertently overwrite langgraph-api --
# -- Removing pip from the final image (but keeping UV) --
RUN uv pip uninstall --system pip setuptools wheel && \
    rm -rf /usr/local/lib/python*/site-packages/pip* /usr/local/lib/python*/site-packages/setuptools* /usr/local/lib/python*/site-packages/wheel* && \
    find /usr/local/bin -name "pip*" -delete
# -- End of pip removal --

# -- Add health check and startup scripts --
COPY backend/scripts/ /scripts/
RUN chmod +x /scripts/*.sh

# -- Set environment variables for enhanced features --
ENV ENABLE_ENHANCED_UI=true
ENV ENABLE_MULTI_LLM=true
ENV ENABLE_AGENT_ROUTING=true
ENV LOG_LEVEL=INFO

# -- Health check --
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/enhanced/health || exit 1

WORKDIR /deps/backend

# -- Startup script --
COPY backend/scripts/startup.sh /startup.sh
RUN chmod +x /startup.sh
CMD ["/startup.sh"]
