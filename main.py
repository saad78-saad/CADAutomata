from fastapi import FastAPI
from pydantic import BaseModel
import queue
from typing import Optional

app = FastAPI(title="CADAutomata Cloud API", version="0.1.0")

# In-memory task queue for local workers to poll
task_queue = queue.Queue()
task_results = {}

class ProcessBOMRequest(BaseModel):
    component_id: str
    name: str
    target_length_mm: float
    target_width_mm: float
    target_height_mm: float
    material: str
    dx: float = 0.0
    dy: float = 0.0
    dz: float = 0.0
    output_path: Optional[str] = None

@app.post("/api/process-component")
def process_component(request: ProcessBOMRequest):
    """Enqueues the BOM adaptation request for the local Windows worker."""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    task_data = request.dict()
    task_data["task_id"] = task_id
    
    task_queue.put(task_data)
    return {"status": "queued", "task_id": task_id, "message": "Task successfully added to queue."}

@app.get("/api/next-task")
def get_next_task():
    """Polled by local Windows workers to fetch pending CAD jobs."""
    if task_queue.empty():
        return {"task": None}
    return {"task": task_queue.get()}

@app.post("/api/complete-task")
def complete_task(completion: dict):
    """Receives execution results back from the local worker."""
    task_id = completion.get("task_id")
    task_results[task_id] = completion
    return {"status": "acknowledged", "task_id": task_id}