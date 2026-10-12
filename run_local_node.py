import time
import httpx
from cad_automata.integration.cad_client import CADClient

CLOUD_API_URL = "https://cadautomata.onrender.com/api"

def run_local_worker():
    print("==================================================")
    print("  CADAutomata Local SolidWorks Node Initialized   ")
    print("==================================================")
    
    cad_client = CADClient()
    if not cad_client.is_windows or not cad_client.sw_app:
        print("WARNING: SolidWorks is not active on this node. Running in Simulation Mode.")
    else:
        print("SUCCESS: Connected to live SolidWorks application.")

    print("\n[INFO] Local node is ready for CAD automation tasks.")
    print("Listening for integration commands...\n")

    # Example test execution using local CADClient wrapper
    test_component = {
        "component_id": "LOCAL-TEST-001",
        "name": "Mounting Bracket",
        "dx": 5.0,
        "dy": 2.0,
        "dz": 5.0,
        "output_path": "output_LOCAL-TEST-001.sldprt"
    }

    print(f"Executing test adaptation for: {test_component['component_id']}")
    try:
        result_path = cad_client.execute_adaptation(
            part_name=test_component["name"],
            dx=test_component["dx"],
            dy=test_component["dy"],
            dz=test_component["dz"],
            output_path=test_component["output_path"]
        )
        print(f"SUCCESS: CAD part successfully adapted and saved to: {result_path}")
    except Exception as e:
        print(f"ERROR: Local CAD adaptation failed: {e}")

if __name__ == "__main__":
    run_local_worker()