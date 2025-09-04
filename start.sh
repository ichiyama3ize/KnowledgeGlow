#!/bin/bash

# KnowledgeGlow Startup Script
# Starts all services for the AI-powered knowledge management system

set -e

echo "🚀 Starting KnowledgeGlow AI Knowledge Management System"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GO_PORT=${GO_PORT:-50575}
PYTHON_PORT=${PYTHON_PORT:-59147}
WEBUI_PORT=${WEBUI_PORT:-8000}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within $max_attempts seconds${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill background processes
    if [ ! -z "$GO_PID" ]; then
        kill $GO_PID 2>/dev/null || true
    fi
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
    if [ ! -z "$WEBUI_PID" ]; then
        kill $WEBUI_PID 2>/dev/null || true
    fi
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Force kill if still running
    pkill -f "go-app/cmd/proxy" 2>/dev/null || true
    pkill -f "ai-service/app/main.py" 2>/dev/null || true
    pkill -f "web-ui/server.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if required ports are available
echo -e "${BLUE}🔍 Checking port availability...${NC}"
check_port $GO_PORT || exit 1
check_port $PYTHON_PORT || exit 1
check_port $WEBUI_PORT || exit 1

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"

# Check Go
if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Go is not installed${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Install Python dependencies if needed
if [ -f "ai-service/requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    pip3 install -r ai-service/requirements.txt > /dev/null 2>&1 || {
        echo -e "${YELLOW}⚠️  Failed to install some Python dependencies, continuing anyway...${NC}"
    }
fi

# Initialize database
echo -e "${BLUE}🗄️  Initializing database...${NC}"
mkdir -p data
if [ -f "data/init.sql" ]; then
    sqlite3 data/knowledge.db < data/init.sql 2>/dev/null || true
fi

# Start Python AI Service
echo -e "${BLUE}🤖 Starting Python AI Service on port $PYTHON_PORT...${NC}"
cd ai-service/app
export AI_SERVICE_PORT=$PYTHON_PORT
python3 main.py > ../../logs/ai-service.log 2>&1 &
PYTHON_PID=$!
cd ../..

# Start Web UI Server
echo -e "${BLUE}🌐 Starting Web UI Server on port $WEBUI_PORT...${NC}"
cd web-ui
export WEBUI_PORT=$WEBUI_PORT
python3 server.py > ../logs/web-ui.log 2>&1 &
WEBUI_PID=$!
cd ..

# Wait for services to be ready
wait_for_service "http://localhost:$PYTHON_PORT/health" "Python AI Service"
wait_for_service "http://localhost:$WEBUI_PORT/health" "Web UI Server"

# Build and start Go Proxy Server
echo -e "${BLUE}🔧 Building Go Proxy Server...${NC}"
cd go-app/cmd
export CGO_ENABLED=0
export GO_PORT=$GO_PORT
export PYTHON_PORT=$PYTHON_PORT
export WEBUI_PORT=$WEBUI_PORT

go build -o ../proxy proxy.go
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build Go proxy server${NC}"
    cleanup
    exit 1
fi

echo -e "${BLUE}🚀 Starting Go Proxy Server on port $GO_PORT...${NC}"
../proxy > ../../logs/go-proxy.log 2>&1 &
GO_PID=$!
cd ../..

# Wait for proxy to be ready
wait_for_service "http://localhost:$GO_PORT/health" "Go Proxy Server"

# Success message
echo -e "${GREEN}🎉 KnowledgeGlow is now running!${NC}"
echo "=================================================="
echo -e "${BLUE}📱 Main Application:${NC} http://localhost:$GO_PORT"
echo -e "${BLUE}🤖 AI Service:${NC}      http://localhost:$PYTHON_PORT"
echo -e "${BLUE}🌐 Web UI:${NC}          http://localhost:$WEBUI_PORT"
echo "=================================================="
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep script running and monitor services
while true; do
    # Check if all services are still running
    if ! kill -0 $GO_PID 2>/dev/null; then
        echo -e "${RED}❌ Go Proxy Server stopped unexpectedly${NC}"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo -e "${RED}❌ Python AI Service stopped unexpectedly${NC}"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $WEBUI_PID 2>/dev/null; then
        echo -e "${RED}❌ Web UI Server stopped unexpectedly${NC}"
        cleanup
        exit 1
    fi
    
    sleep 5
done