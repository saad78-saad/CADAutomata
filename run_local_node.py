import time
import httpx
import os
from agent_loop import AgenticCADEngine

# Cloud backend URL (matches your Render deployment and FastAPI endpoints)
CLOUD_API_URL = "https://cadautomata.onrender.com/api" 
POLL_INTERVAL_SECONDS = 5

def run_polling_worker():
    print("==================================================")
    print("  CADAutomata Continuous Agentic Worker Node      ")
    print("==================================================")
    
    # Initialize the Agentic CAD Engine (which manages CADClient and LLM tool-calling)
    try:
        engine = AgenticCADEngine()
        print("SUCCESS: Initialized Agentic CAD Engine & SolidWorks COM connection.")
    except Exception as e:
        print(f"[WARNING] Could not fully initialize SolidWorks session: {e}")
        print("Running in simulation/fallback mode until SolidWorks is active.")

    print(f"\n[INFO] Polling cloud backend at: {CLOUD_API_URL}")
    print("Listening for incoming BOM delta adaptation tasks... (Press Ctrl+C to stop)\n")

    while True:
        try:
            # 1. Poll the Render backend for the next task
            response = httpx.get(f"{CLOUD_API_URL}/next-task", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                task = data.get("task")
                
                if task:
                    task_id = task.get("task_id", "UNKNOWN")
                    component_name = task.get("name", "Unknown_Part")
                    file_path = task.get("file_path", f"./{component_name}.sldprt")
                    
                    # Extract BOM delta parameters (dx, dy, dz or custom dictionary)
                    bom_delta = {
                        "dx": task.get("dx", 0.0),
                        "dy": task.get("dy", 0.0),
                        "dz": task.get("dz", 0.0)
                    }
                    
                    print(f"\n[JOB RECEIVED] Task ID: {task_id} | Component: {component_name}")
                    print(f"[BOM DELTA] Applying modifications: {bom_delta}")
                    
                    # 2. Execute the task using the Agentic ReAct / Tool-Use Loop
                    try:
                        execution_result = engine.run_task(file_path=file_path, bom_delta=bom_delta)
                        print(f"SUCCESS: Agent executed adaptation for {component_name}.")
                        
                        # 3. Report completion back to the Render cloud backend
                        completion_payload = {
                            "task_id": task_id,
                            "status": "success",
                            "result": execution_result
                        }
                        httpx.post(f"{CLOUD_API_URL}/complete-task", json=completion_payload, timeout=10.0)
                        
                    except Exception as agent_err:
                        print(f"[ERROR] Agent execution failed: {agent_err}")
                        # Report failure back to cloud
                        error_payload = {
                            "task_id": task_id,
                            "status": "error",
                            "message": str(agent_err)
                        }
                        httpx.post(f"{CLOUD_API_URL}/complete-task", json=error_payload, timeout=10.0)
                        
                else:
                    # Queue is empty, print heartbeat dot
                    print(".", end="", flush=True)
            
            time.sleep(POLL_INTERVAL_SECONDS)

        except httpx.RequestError as req_err:
            print(f"\n[WARN] Connection error reaching cloud backend: {req_err}. Retrying in {POLL_INTERVAL_SECONDS}s...")
            time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[INFO] Stopping local worker node gracefully.")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected polling error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_polling_worker()