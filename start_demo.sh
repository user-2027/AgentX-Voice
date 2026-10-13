#!/bin/bash
# Quick start script

echo "Starting Call Center System..."

cd /workspaces/agentX 2>/dev/null || cd /workspace/agentX 2>/dev/null || cd "$(dirname "$0")"

# Start backend
echo "Starting backend..."
source venv/bin/activate
python main.py > backend.log 2>&1 &
BACKEND_PID=$!

sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "System started!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "In Codespaces, use Ports tab to access forwarded URLs"
echo "Press Ctrl+C to stop"

trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait

