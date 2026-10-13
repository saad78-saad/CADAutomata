from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
import queue

app = FastAPI(title="CADAutomata Cloud API", version="0.2.0")

# In-memory task queue
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
    message: Optional[Any] = None

@app.get("/")
def read_root():
    return {"status": "CADAutomata Cloud Backend Active", "queue_size": task_queue.qsize()}

@app.post("/api/add-task")
def add_task(task: BOMTaskRequest):
    """Enqueues a new CAD adaptation task for local workers."""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    task_data = task.dict()
    task_data["task_id"] = task_id
    
    task_queue.put(task_data)
    print(f"[QUEUE] Added task {task_id}: {task.name}")
    return {"status": "queued", "task_id": task_id}

@app.get("/api/next-task")
def get_next_task():
    """Polled by local Windows worker node to fetch pending tasks."""
    if task_queue.empty():
        return {"task": None}
    task = task_queue.get()
    return {"task": task}

@app.post("/api/complete-task")
def complete_task(completion: TaskCompletionRequest):
    """Receives completion status from local worker."""
    task_results[completion.task_id] = completion.dict()
    print(f"[COMPLETED] Task {completion.task_id} status: {completion.status}")
    return {"status": "acknowledged", "task_id": completion.task_id}