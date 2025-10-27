#!/usr/bin/env python3
import os
import sys
import subprocess
import uvicorn

def start_backend():
    """Start the FastAPI backend server"""
    try:
        print("🚀 Starting DProf Backend Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop the server\n")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "install":
            install_dependencies()
            return
        elif command == "start":
            start_backend()
            return
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: install, start")
            sys.exit(1)
    
    # Default action: start the server
    start_backend()

if __name__ == "__main__":
    main()