#!/bin/bash
# Glossary Management System - Startup Script (Linux/Mac)
# Starts both backend and frontend servers

echo "========================================"
echo "  Glossary Management System Startup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -f "./venv/bin/python" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please create it first: python -m venv venv${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js not found! Please install Node.js first.${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}[OK] Node.js version: $NODE_VERSION${NC}"

# Check if frontend dependencies are installed
if [ ! -d "./src/frontend/node_modules" ]; then
    echo -e "${YELLOW}[INFO] Installing frontend dependencies...${NC}"
    cd src/frontend
    npm install
    cd ../..
    echo -e "${GREEN}[OK] Frontend dependencies installed${NC}"
fi

echo ""
echo -e "${CYAN}Starting servers...${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}All servers stopped.${NC}"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Start Backend Server
echo -e "${CYAN}[1/2] Starting Backend Server (FastAPI)...${NC}"
./venv/bin/python src/backend/app.py &
BACKEND_PID=$!
echo -e "  -> Backend PID: $BACKEND_PID"
echo -e "${GREEN}  -> API: http://localhost:8000${NC}"
echo -e "${GREEN}  -> Docs: http://localhost:8000/docs${NC}"
sleep 3

# Start Frontend Server
echo ""
echo -e "${CYAN}[2/2] Starting Frontend Server (React + Vite)...${NC}"
cd src/frontend
npm run dev &
FRONTEND_PID=$!
echo -e "  -> Frontend PID: $FRONTEND_PID"
echo -e "${GREEN}  -> UI: http://localhost:3000${NC}"
cd ../..

echo ""
echo "========================================"
echo -e "${GREEN}  Servers Started Successfully!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}Backend API:  http://localhost:8000${NC}"
echo -e "${YELLOW}API Docs:     http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Frontend UI:  http://localhost:3000${NC}"
echo ""
echo -e "${CYAN}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
