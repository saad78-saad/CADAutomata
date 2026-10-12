import time
import httpx
from cad_automata.integration.cad_client import CADClient

# Change this to your Render URL later (e.g. "https://cadautomata.onrender.com/api")
CLOUD_API_URL = "https://cadautomata.onrender.com/api" 
POLL_INTERVAL_SECONDS = 5

def run_polling_worker():
    print("==================================================")
    print("  CADAutomata Continuous Local Worker Node        ")
    print("==================================================")
    
    cad_client = CADClient()
    if not cad_client.is_windows or not cad_client.sw_app:
        print("WARNING: SolidWorks is not active. Running in Simulation Mode.")
    else:
        print("SUCCESS: Connected to live SolidWorks application.")

    print(f"\n[INFO] Polling backend at: {CLOUD_API_URL}")
    print("Listening for incoming CAD adaptation tasks... (Press Ctrl+C to stop)\n")

    while True:
        try:
            # Ask the cloud for the next task
            response = httpx.get(f"{CLOUD_API_URL}/next-task", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                task = data.get("task")
                
                if task:
                    print(f"\n[JOB RECEIVED] Processing component: {task['component_id']} ({task['name']})")
                    
                    # Execute adaptation in SolidWorks using your CADClient
                    result_path = cad_client.execute_adaptation(
                        part_name=task["name"],
                        dx=task["dx"],
                        dy=task["dy"],
                        dz=task["dz"],
                        output_path=task["output_path"]
                    )
                    print(f"SUCCESS: Part adapted and saved to: {result_path}")
                else:
                    # Queue is empty, wait and check again
                    print(".", end="", flush=True)
            
            time.sleep(POLL_INTERVAL_SECONDS)

        except httpx.RequestError as req_err:
            print(f"\n[WARN] Connection error: {req_err}. Retrying in {POLL_INTERVAL_SECONDS}s...")
            time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[INFO] Stopping local worker node gracefully.")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_polling_worker()