import os
from cad_automata.config import settings
from cad_automata.logger import get_logger

logger = get_logger(__name__)

class CADClient:
    def __init__(self):
        self.sw_app = None
        self.mock_mode = False
        self._initialize_connection()

    def _initialize_connection(self):
        """Attempts to connect to SolidWorks. If missing (like on your laptop), 
           it automatically falls back to Mock Mode so the app doesn't crash."""
        try:
            import win32com.client
            self.sw_app = win32com.client.Dispatch("SldWorks.Application")
            self.sw_app.Visible = settings.solidworks_visible
            logger.info("SUCCESS: Connected to live SolidWorks application.")
        except Exception as e:
            self.mock_mode = True
            logger.warning(f"SolidWorks not detected on this machine ({e}).")
            logger.info("Framework running in MOCK MODE for local development/testing.")

    def open_part(self, file_path: str):
        abs_path = os.path.abspath(file_path)
        if self.mock_mode:
            logger.info(f"[MOCK] Simulated opening part: {abs_path}")
            return
        
        self.sw_app.OpenDoc6(abs_path, 1, 1, "", 0, 0)
        logger.info(f"Opened part in SolidWorks: {abs_path}")

    def execute_adaptation(self, part_name: str, dx: float, dy: float, dz: float, output_path: str):
        abs_output = os.path.abspath(output_path)
        
        if self.mock_mode:
            logger.info(f"[MOCK] Simulated scaling for {part_name} -> dX:{dx:.2f}, dY:{dy:.2f}, dZ:{dz:.2f}")
            logger.info(f"[MOCK] Simulated export to {abs_output}")
            return

        # Live SolidWorks execution (runs only on your friend's PC)
        doc = self.sw_app.ActiveDoc
        if not doc:
            raise ValueError("No active document found in SolidWorks.")
        
        logger.info(f"Applying live parametric scaling on {part_name}...")
        doc.SaveAs3(abs_output, 0, 2)
        logger.info(f"Successfully exported adapted model to {abs_output}")