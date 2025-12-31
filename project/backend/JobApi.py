from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from JobList import JobList
from bson.objectid import ObjectId
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Job Application Tracker API", version="1.0.0")

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#pydantic models
class JobCreate(BaseModel):
    company: str
    position: str
    status: str
    date_applied: datetime
    salary: Optional[float] = None
    job_url: Optional[str] = None
    remarks: Optional[str] = None

class JobUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    date_applied: Optional[datetime] = None
    salary: Optional[float] = None
    job_url: Optional[str] = None
    remarks: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    company: str
    position: str
    status: str
    date_applied: datetime
    salary: Optional[float] = None
    job_url: Optional[str] = None
    remarks: Optional[str] = None

# initialize JobList
try:
    db = JobList()
    print("✓ Database connection successful!")
except Exception as e:
    db = None
    print(f"✗ ERROR initializing database: {e}")
    print(f"  Make sure you have a .env file with MONGODB_ATLAS_CLUSTER_URI")
    import traceback
    traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if db is None:
        raise Exception("Failed to connect to MongoDB")
    yield
    if db:
        db.close_connection()


@app.get("/")
async def root():
    return {"message": "Welcome to the Job Application Tracker API"}

@app.post("/jobs/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate):
    """Create new job list"""
    try:
        job_id = db.create_job(
            company=job.company,
            position=job.position,
            status=job.status,
            date_applied=job.date_applied,
            salary=job.salary,
            job_url=job.job_url,
            remarks=job.remarks
        )
        if job_id is None:
            raise HTTPException(status_code=400, detail="Failed to create job - validation error or database issue")
        
        # Get the created job to return it
        created_job = db.jobs_collection.find_one({"_id": ObjectId(job_id)})
        return JobResponse(
            id=job_id,
            company=created_job["company"],
            position=created_job["position"],
            status=created_job["status"],
            date_applied=created_job["date_applied"],
            salary=created_job.get("salary"),
            job_url=created_job.get("job_url"),
            remarks=created_job.get("remarks")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating job: {e}")
    
@app.get("/jobs/", response_model=List[JobResponse])
async def get_all_jobs():
    """Get all job lists"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected. Check server logs.")
    
    try:
        jobs = db.get_all_jobs()
        return [
            JobResponse(
                id=job["_id"],
                company=job["company"],
                position=job["position"],
                status=job["status"],
                date_applied=job["date_applied"],
                salary=job.get("salary"),
                job_url=job.get("job_url"),
                remarks=job.get("remarks")
            ) for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving jobs: {e}")
    
@app.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job: JobUpdate):
    """Update job by ID"""
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(
                status_code=400, 
                detail="Invalid job ID format")
        
        # Check if job exists
        existing_job = db.jobs_collection.find_one({"_id": ObjectId(job_id)})
        if not existing_job:
            raise HTTPException(
                status_code=404, 
                detail="Job not found"
            )
        
        updated_job = db.update_job(
            job_id=job_id,
            company=job.company,
            position=job.position,
            status=job.status,
            date_applied=job.date_applied,
            salary=job.salary,
            job_url=job.job_url,
            remarks=job.remarks
        )
        if updated_job is None:
            raise HTTPException(status_code=500, detail="Failed to update job")
        else:
            return JobResponse(
                id=job_id,
                company=updated_job["company"],
                position=updated_job["position"],
                status=updated_job["status"],
                date_applied=updated_job["date_applied"],
                salary=updated_job.get("salary"),
                job_url=updated_job.get("job_url"),
                remarks=updated_job.get("remarks")
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating job: {e}")
    
@app.delete("/jobs/{job_id}", response_model=dict)
async def delete_job(job_id: str):
    """Delete job by ID"""
    try:
        if not ObjectId.is_valid(job_id):
            raise HTTPException(
                status_code=400, 
                detail="Invalid job ID format")
        
        # Check if user exists
        job = db.jobs_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=404, 
                detail="Job not found")
        
        success = db.delete_job(job_id)
        if success:
            return {"message": "Job deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete job")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job: {e}")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)