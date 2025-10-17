import os
import shutil
import time
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_files(files: list[UploadFile], user_id: str):
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    paths = []
    for f in files:
        dest = os.path.join(user_dir, f.filename)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        paths.append(dest)
    return paths

app = FastAPI(title="TissueLab API", version="1.0.0", description="Asynchronous image processing demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int = 0

JOBS: dict[str, JobStatus] = {}

@app.post("/jobs", response_model=JobStatus)
def submit_job(
    background: BackgroundTasks,
    files: list[UploadFile] = File(...),
    x_user_id: str = Header("anonymous")
):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = JobStatus(job_id=job_id, status="PENDING")
    paths = save_files(files, x_user_id)
    background.add_task(fake_work, job_id, paths)
    return JOBS[job_id]

@app.get("/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, detail="job not found")
    return JOBS[job_id]

def fake_work(job_id: str, paths: list[str]):
    job = JOBS[job_id]
    job.status = "RUNNING"
    for i in range(1, 11):
        time.sleep(1)
        job.progress = i * 10
    job.status = "SUCCEEDED"