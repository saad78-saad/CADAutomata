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
        """Robust COM attachment pattern inspired by Millwright/Swpilot CLI"""
        try:
            import win32com.client
            import pythoncom
            
            pythoncom.CoInitialize()
            try:
                # Attempt to attach to an active SolidWorks instance first
                self.sw_app = win32com.client.GetActiveObject("SldWorks.Application")
                logger.info("Successfully attached to running SolidWorks session.")
            except Exception:
                # If none is running, launch a new instance
                logger.info("No active session found. Launching new SolidWorks instance...")
                self.sw_app = win32com.client.Dispatch("SldWorks.Application")
                self.sw_app.Visible = True
                
        except Exception as e:
            logger.error(f"Failed to initialize SolidWorks COM interface: {e}")
            self.sw_app = None

    def open_part(self, file_path: str):
        if not self.is_windows or not self.sw_app:
            logger.info(f"[MOCK] Opening part template: {file_path}")
            return True
        
        try:
            # Native SolidWorks API call to open document
            doc_type = 1 # swDocPart
            errors = 0
            warnings = 0
            part = self.sw_app.OpenDoc6(file_path, doc_type, 1, "", errors, warnings)
            return part is not None
        except Exception as e:
            logger.error(f"Error opening part {file_path}: {e}")
            return False

    def execute_adaptation(self, part_name: str, dx: float, dy: float, dz: float, output_path: str):
        if not self.is_windows or not self.sw_app:
            logger.info(f"[MOCK] Scaling part {part_name} by dx={dx}, dy={dy}, dz={dz}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            with open(output_path, "w") as f:
                f.write("MOCK_SLDPRT_BINARY_DATA")
            return output_path
        
        try:
            # Structured feature modification action wrapper
            active_doc = self.sw_app.ActiveDoc
            if not active_doc:
                raise ValueError("No active SolidWorks document found for adaptation.")
            
            logger.info(f"Applying scaling deltas -> dX: {dx}, dY: {dy}, dZ: {dz}")
            # Insert your direct SolidWorks feature modification / scaling logic here
            
            active_doc.SaveAs3(output_path, 0, 2)
            return output_path
        except Exception as e:
            logger.error(f"Adaptation execution failed: {e}")
            raise e