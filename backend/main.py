from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import os
import io
from datetime import datetime
import uuid

from app.connectors.file_connector import FileConnector
from app.connectors.database_connector import DatabaseConnector
from app.profiler.data_profiler import DataProfiler
from app.exporters.profile_exporter import ProfileExporter
from app.config import Settings

app = FastAPI(title="DView - Data Profiling Application", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()
profiler = DataProfiler(settings)
exporter = ProfileExporter()

# In-memory storage for session data (in production, use Redis or similar)
sessions = {}

class DatabaseConnection(BaseModel):
    connection_type: str  # "oracle" or "sqlserver"
    host: str
    port: int
    database: str
    username: str
    password: str

class ProfilingRequest(BaseModel):
    session_id: str
    tables: List[str]
    max_records: Optional[int] = None

class ExportRequest(BaseModel):
    session_id: str
    export_format: str  # "xlsx", "json", "html"
    tables: List[str]

@app.get("/")
async def root():
    return {"message": "DView Data Profiling API", "version": "1.0.0"}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze file structure (CSV, JSON, XLSX)"""
    try:
        session_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        temp_dir = f"temp/{session_id}"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = f"{temp_dir}/{file.filename}"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Analyze file structure
        file_connector = FileConnector()
        structure = await file_connector.analyze_file_structure(file_path)
        
        # Store session data
        sessions[session_id] = {
            "type": "file",
            "file_path": file_path,
            "filename": file.filename,
            "structure": structure,
            "created_at": datetime.now()
        }
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "structure": structure
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/connect-database")
async def connect_database(connection: DatabaseConnection):
    """Connect to database and get table list"""
    try:
        session_id = str(uuid.uuid4())
        
        db_connector = DatabaseConnector()
        tables = await db_connector.connect_and_get_tables(
            connection.connection_type,
            connection.host,
            connection.port,
            connection.database,
            connection.username,
            connection.password
        )
        
        # Store session data
        sessions[session_id] = {
            "type": "database",
            "connection": connection.dict(),
            "tables": tables,
            "created_at": datetime.now()
        }
        
        return {
            "session_id": session_id,
            "tables": tables
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/session/{session_id}/record-count")
async def get_record_count(session_id: str, table_name: str):
    """Get record count for a specific table"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    try:
        if session_data["type"] == "file":
            file_connector = FileConnector()
            count = await file_connector.get_record_count(session_data["file_path"], table_name)
        else:
            db_connector = DatabaseConnector()
            count = await db_connector.get_record_count(session_data["connection"], table_name)
        
        return {"table_name": table_name, "record_count": count}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/profile-data")
async def profile_data(request: ProfilingRequest, background_tasks: BackgroundTasks):
    """Start data profiling process"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[request.session_id]
    
    # Start profiling in background
    profiling_task_id = str(uuid.uuid4())
    sessions[request.session_id]["profiling_task_id"] = profiling_task_id
    sessions[request.session_id]["profiling_status"] = "running"
    sessions[request.session_id]["profiling_progress"] = 0
    
    background_tasks.add_task(
        run_profiling,
        request.session_id,
        profiling_task_id,
        session_data,
        request.tables,
        request.max_records
    )
    
    return {
        "task_id": profiling_task_id,
        "status": "started",
        "message": "Profiling started in background"
    }

async def run_profiling(session_id: str, task_id: str, session_data: Dict, tables: List[str], max_records: Optional[int]):
    """Background task for data profiling"""
    try:
        if session_data["type"] == "file":
            results = await profiler.profile_file_data(
                session_data["file_path"],
                tables,
                max_records,
                lambda progress: update_progress(session_id, progress)
            )
        else:
            results = await profiler.profile_database_data(
                session_data["connection"],
                tables,
                max_records,
                lambda progress: update_progress(session_id, progress)
            )
        
        sessions[session_id]["profiling_results"] = results
        sessions[session_id]["profiling_status"] = "completed"
        sessions[session_id]["profiling_progress"] = 100
        
    except Exception as e:
        sessions[session_id]["profiling_status"] = "error"
        sessions[session_id]["profiling_error"] = str(e)

def update_progress(session_id: str, progress: int):
    """Update profiling progress"""
    if session_id in sessions:
        sessions[session_id]["profiling_progress"] = progress

@app.get("/profiling-status/{session_id}")
async def get_profiling_status(session_id: str):
    """Get profiling status and progress"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    return {
        "status": session_data.get("profiling_status", "not_started"),
        "progress": session_data.get("profiling_progress", 0),
        "error": session_data.get("profiling_error"),
        "results_available": "profiling_results" in session_data
    }

@app.get("/profiling-results/{session_id}")
async def get_profiling_results(session_id: str):
    """Get profiling results"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "profiling_results" not in sessions[session_id]:
        raise HTTPException(status_code=404, detail="No profiling results available")
    
    return sessions[session_id]["profiling_results"]

@app.post("/export")
async def export_results(request: ExportRequest):
    """Export profiling results"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[request.session_id]
    
    if "profiling_results" not in session_data:
        raise HTTPException(status_code=404, detail="No profiling results to export")
    
    try:
        export_data = {
            table: session_data["profiling_results"][table]
            for table in request.tables
            if table in session_data["profiling_results"]
        }
        
        if request.export_format == "xlsx":
            file_content, filename = await exporter.export_to_xlsx(export_data)
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif request.export_format == "json":
            file_content, filename = await exporter.export_to_json(export_data)
            return StreamingResponse(
                io.BytesIO(file_content.encode()),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif request.export_format == "html":
            file_content, filename = await exporter.export_to_html(export_data)
            return StreamingResponse(
                io.BytesIO(file_content.encode()),
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings")
async def get_settings():
    """Get current application settings"""
    return {
        "max_threads": settings.max_threads,
        "default_max_records": settings.default_max_records,
        "chunk_size": settings.chunk_size
    }

@app.post("/settings")
async def update_settings(new_settings: Dict[str, Any]):
    """Update application settings"""
    try:
        if "max_threads" in new_settings:
            settings.max_threads = new_settings["max_threads"]
        if "default_max_records" in new_settings:
            settings.default_max_records = new_settings["default_max_records"]
        if "chunk_size" in new_settings:
            settings.chunk_size = new_settings["chunk_size"]
        
        return {"message": "Settings updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)