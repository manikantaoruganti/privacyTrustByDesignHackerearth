import os
import uuid
import logging
from pathlib import Path
from typing import List, Optional
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from pipeline.processor import DocumentProcessor
from pipeline.models import ProcessResult, JobStatus, AuditEntry
from pipeline.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
processor: DocumentProcessor
jobs: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global processor
    # Initialize processor
    config = Config.load()
    processor = DocumentProcessor(config)
    yield
    # Cleanup

app = FastAPI(
    title="DocuShield AI",
    description="Privacy-Preserving Document Deidentification",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs("temp", exist_ok=True)
os.makedirs("output", exist_ok=True)

async def process_document_task(job_id: str, file_path: str, filename: str):
    """Background task to process document"""
    try:
        jobs[job_id]["status"] = "processing"
        
        # Process the document
        result = await processor.process_document(file_path, filename)
        
        jobs[job_id].update({
            "status": "completed",
            "result": result,
            "download_url": f"/api/v1/jobs/{job_id}/download",
            "audit_url": f"/api/v1/jobs/{job_id}/audit"
        })
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "DocuShield AI"}

@app.post("/api/v1/redact")
async def redact_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and redact a document"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = f"temp/{job_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Initialize job
    jobs[job_id] = {
        "id": job_id,
        "filename": file.filename,
        "status": "queued",
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Start background processing
    background_tasks.add_task(
        process_document_task, 
        job_id, 
        file_path, 
        file.filename
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Document queued for processing"
    }

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/v1/jobs/{job_id}/download")
async def download_result(job_id: str):
    """Download processed document"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_path = f"output/{job_id}_redacted_{job['filename']}"
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="application/octet-stream",
        filename=f"redacted_{job['filename']}"
    )

@app.get("/api/v1/jobs/{job_id}/audit")
async def get_audit_log(job_id: str):
    """Get audit log for processed document"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    result = job.get("result", {})
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "audit_entries": result.get("audit_entries", []),
        "summary": result.get("summary", {})
    }

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )