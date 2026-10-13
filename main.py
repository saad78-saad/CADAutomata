from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import queue

app = FastAPI(title="CADAutomata Cloud API", version="0.1.0")

# In-memory task queue (or use Redis/Database for persistence)
task_queue = queue.Queue()
task_results = {}

class BOMTaskRequest(BaseModel):
    component_id: str
    name: str
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0
    file_path: Optional[str] = None

class TaskCompletionRequest(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "CADAutomata Cloud Backend Active", "queue_size": task_queue.qsize()}

@app.post("/api/add-task")
def add_task(task: BOMTaskRequest):
    """Enqueues a new CAD adaptation task from clients."""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    task_data = task.dict()
    task_data["task_id"] = task_id
    
    task_queue.put(task_data)
    return {"status": "queued", "task_id": task_id}

@app.get("/api/next-task")
def get_next_task():
    """Polled by the local Windows worker node to fetch the next CAD job."""
    if task_queue.empty():
        return {"task": None}
    
    task = task_queue.get()
    return {"task": task}

@app.post("/api/complete-task")
def complete_task(completion: TaskCompletionRequest):
    """Receives execution results back from the local Windows worker node."""
    task_results[completion.task_id] = {
        "status": completion.status,
        "result": completion.result,
        "message": completion.message
    }
    return {"status": "acknowledged", "task_id": completion.task_id}