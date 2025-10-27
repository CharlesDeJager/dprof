@echo off
echo 🚀 Starting DProf Application...
echo.

echo 📡 Starting backend server...
cd backend
call venv\Scripts\activate
start /B python run_server.py
cd ..

echo 🌐 Starting frontend server...
cd frontend
start /B npm start
cd ..

echo.
echo ✅ DProf is starting up!
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo ⏹️  Close this window to stop the servers

pause
