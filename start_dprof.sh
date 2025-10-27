#!/bin/bash

echo "🚀 Starting DProf Application..."
echo

# Start backend
echo "📡 Starting backend server..."
cd backend
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:/opt/homebrew/opt/unixodbc/lib:$DYLD_LIBRARY_PATH
./venv/bin/python run_server.py start &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "✅ DProf is starting up!"
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo
echo "⏹️  Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo
    echo "🛑 Shutting down DProf..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait
