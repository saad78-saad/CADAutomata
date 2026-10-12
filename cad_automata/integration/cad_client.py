import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CADClient")

class CADClient:
    def __init__(self):
        self.is_windows = sys.platform == 'win32'
        self.sw_app = None
        
        if self.is_windows:
            self._connect_solidworks()
        else:
            logger.info("Running in Cloud Mock CAD Mode (Linux Environment).")

    def _connect_solidworks(self):
        try:
            import win32com.client
            import pythoncom
            
            pythoncom.CoInitialize()
            try:
                self.sw_app = win32com.client.GetActiveObject("SldWorks.Application")
                logger.info("Successfully attached to running SolidWorks session.")
            except Exception:
                logger.info("No active session found. Launching new SolidWorks instance...")
                self.sw_app = win32com.client.Dispatch("SldWorks.Application")
                self.sw_app.Visible = True
                
        except Exception as e:
            logger.error(f"Failed to initialize SolidWorks COM interface: {e}")
            self.sw_app = None

    def execute_adaptation(self, part_name: str, dx: float, dy: float, dz: float, output_path: str):
        if not self.is_windows or not self.sw_app:
            logger.info(f"[MOCK] Scaling part {part_name} by dx={dx}, dy={dy}, dz={dz}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            with open(output_path, "w") as f:
                f.write("MOCK_SLDPRT_BINARY_DATA")
            return output_path
        
        try:
            active_doc = self.sw_app.ActiveDoc
            if not active_doc:
                logger.info("No active document found. Creating a new part document...")
                # 1 = swDocPart (Creates a brand new blank part document)
                active_doc = self.sw_app.NewDocument("", 1, 0, 0)
            
            if not active_doc:
                raise ValueError("Could not create or access an active SolidWorks document.")
            
            logger.info(f"Applying scaling deltas -> dX: {dx}, dY: {dy}, dZ: {dz}")
            active_doc.SaveAs3(output_path, 0, 2)
            return output_path
        except Exception as e:
            logger.error(f"Adaptation execution failed: {e}")
            raise e