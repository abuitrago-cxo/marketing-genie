#!/bin/bash

# Enhanced Health Check Script
# Performs comprehensive health checks for all system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    if curl -f -s --max-time "$timeout" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name: OK${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: FAILED${NC}"
        return 1
    fi
}

# Function to check service connectivity
check_service() {
    local host=$1
    local port=$2
    local name=$3
    
    if nc -z "$host" "$port" 2>/dev/null; then
        echo -e "${GREEN}✅ $name: Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Connection failed${NC}"
        return 1
    fi
}

echo "🏥 Enhanced AI Agent Assistant Health Check"
echo "=========================================="

# Check main application
echo "🔍 Checking main application..."
check_http_endpoint "http://localhost:8000/api/v1/enhanced/health" "Main API"

# Check enhanced endpoints
echo "🔍 Checking enhanced endpoints..."
check_http_endpoint "http://localhost:8000/api/v1/enhanced/agents/status" "Agent Status API"
check_http_endpoint "http://localhost:8000/api/v1/enhanced/llm/status" "LLM Status API"
check_http_endpoint "http://localhost:8000/api/v1/enhanced/system/status" "System Status API"

# Check documentation
echo "🔍 Checking documentation..."
check_http_endpoint "http://localhost:8000/docs" "API Documentation"

# Check database connectivity
if [ -n "$POSTGRES_URI" ]; then
    echo "🔍 Checking PostgreSQL..."
    PG_HOST=$(echo "$POSTGRES_URI" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    PG_PORT=$(echo "$POSTGRES_URI" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -n "$PG_HOST" ] && [ -n "$PG_PORT" ]; then
        check_service "$PG_HOST" "$PG_PORT" "PostgreSQL"
    fi
fi

# Check Redis connectivity
if [ -n "$REDIS_URI" ]; then
    echo "🔍 Checking Redis..."
    REDIS_HOST=$(echo "$REDIS_URI" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    REDIS_PORT=$(echo "$REDIS_URI" | sed -n 's/.*:\([0-9]*\).*/\1/p')
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        check_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    fi
fi

# Check LLM providers
echo "🔍 Checking LLM providers..."
python -c "
import sys
sys.path.append('/deps/backend/src')
try:
    from agent.configuration import get_llm_status
    status = get_llm_status()
    providers = status['available_providers']
    if providers:
        print(f'✅ LLM Providers: {len(providers)} available ({', '.join(providers)})')
    else:
        print('⚠️  LLM Providers: No providers available')
        sys.exit(1)
except Exception as e:
    print(f'❌ LLM Providers: Error - {e}')
    sys.exit(1)
"

# Check agent router
echo "🔍 Checking agent router..."
python -c "
import sys
sys.path.append('/deps/backend/src')
try:
    from agent.router import agent_router
    status = agent_router.get_agent_status()
    agents = status['agents']
    active_tasks = status['total_active_tasks']
    print(f'✅ Agent Router: {len(agents)} agents, {active_tasks} active tasks')
except Exception as e:
    print(f'❌ Agent Router: Error - {e}')
    sys.exit(1)
"

# Memory and disk usage
echo "🔍 Checking system resources..."
echo "Memory usage:"
free -h | head -2

echo "Disk usage:"
df -h / | tail -1

echo ""
echo -e "${GREEN}🎉 Health check completed!${NC}"
