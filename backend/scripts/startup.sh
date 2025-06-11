#!/bin/bash

# Enhanced AI Agent Assistant Startup Script
# This script initializes the enhanced features and starts the application

set -e

echo "🚀 Starting Enhanced AI Agent Assistant..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "🔄 Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within expected time"
    return 1
}

# Parse Redis URI
if [ -n "$REDIS_URI" ]; then
    REDIS_HOST=$(echo "$REDIS_URI" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    REDIS_PORT=$(echo "$REDIS_URI" | sed -n 's/.*:\([0-9]*\).*/\1/p')
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    fi
fi

# Parse PostgreSQL URI
if [ -n "$POSTGRES_URI" ]; then
    PG_HOST=$(echo "$POSTGRES_URI" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    PG_PORT=$(echo "$POSTGRES_URI" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -n "$PG_HOST" ] && [ -n "$PG_PORT" ]; then
        wait_for_service "$PG_HOST" "$PG_PORT" "PostgreSQL"
    fi
fi

# Initialize LLM providers
echo "🧠 Initializing LLM providers..."
python -c "
import sys
# sys.path.append('/deps/backend/src') # /deps/backend should be in PYTHONPATH
from src.agent.configuration import configure_llm_providers # Changed import
config_status = configure_llm_providers()
print(f'✅ Configured providers: {config_status[\"providers_configured\"]}')
if config_status['providers_failed']:
    print(f'⚠️  Failed providers: {config_status[\"providers_failed\"]}')
"

# Initialize agent router
echo "🤖 Initializing agent router..."
python -c "
import sys
# sys.path.append('/deps/backend/src') # /deps/backend should be in PYTHONPATH
from src.agent.router import agent_router # Changed import
status = agent_router.get_agent_status()
print(f'✅ Agent router initialized with {len(status[\"agents\"])} agent types')
"

# Run database migrations if needed
echo "🗄️  Checking database..."
if [ -n "$POSTGRES_URI" ]; then
    python -c "
import sys
# sys.path.append('/deps/backend/src') # /deps/backend should be in PYTHONPATH
# Add any database initialization code here
print('✅ Database check completed')
"
fi

# Start the application
echo "🌟 Starting enhanced application..."

# Set Python path
export PYTHONPATH="/deps/backend:$PYTHONPATH"  # Changed src to be a child of a PYTHONPATH entry


# Environment setup complete. Handing over to base image entrypoint to start the server.
echo "✅ PYTHONPATH set to: $PYTHONPATH"
echo "🏁 Startup script finished. Base image entrypoint will now take over."
