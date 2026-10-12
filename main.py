from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="CADAutomata Cloud API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory queue for tasks
task_queue = []

class ProcessBOMRequest(BaseModel):
    component_id: str
    name: str
    dx: float
    dy: float
    dz: float
    output_path: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "queue_size": len(task_queue)}

# 1. Endpoint to add a task (e.g. from frontend or BOM parser)
@app.post("/api/add-task")
def add_task(task: ProcessBOMRequest):
    task_queue.append(task.dict())
    return {"status": "success", "message": f"Task {task.component_id} added to queue."}

# 2. Endpoint for your local laptop worker to fetch the next job
@app.get("/api/next-task")
def get_next_task():
    if not task_queue:
        return {"task": None}
    # Pop the first task from the queue
    next_task = task_queue.pop(0)
    return {"task": next_task}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)